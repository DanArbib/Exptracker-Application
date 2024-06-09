from flask import request, jsonify, render_template
from prometheus_flask_exporter import Counter, Histogram
from time import time
from app import app, db, logger, bcrypt_app
from app.models.user import User, Expense
from app.utils.decorators import validate_jwt
import uuid
import jwt
import os

login_requests_counter = Counter('login_requests', 'Number of login requests', ['status'])
login_latency_histogram = Histogram('login_latency_seconds', 'Latency of login requests')
login_attempts_counter = Counter('login_attempts', 'Number of login attempts', ['status'])
expense_additions_counter = Counter('expense_additions', 'Number of expense additions', ['status'])
expense_deletions_counter = Counter('expense_deletions', 'Number of expense deletions', ['status'])


@app.route("/health", methods=['GET'])
def health():
    return jsonify({'status': 'success', 'message': 'healthy'}), 200

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/sign", methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@app.route("/logout", methods=['GET'])
def logout():
    return render_template('logout.html')


@app.route("/dashboard", methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route("/topup", methods=['GET'])
def topup():
    return render_template('topup.html')


### API ROUTES ###
@app.route("/api/v1/sign", methods=['POST'])
def signup_api():
    """
    Handles user signup by creating a new user account and sending an email verification link.

    This route expects a JSON payload containing 'email' and 'password' fields.
    It checks if the email already exists in the database and handles the case where it exists but is not verified.
    If the email is new or has been removed, it creates a new user account with a hashed password.
    Then, it generates a confirmation token and sends an email with a verification link to the user.

    Returns:
        JSON: A JSON response indicating the success of the signup process or an error message.
    """
    email = request.json.get('email')
    password = request.json.get('password')

    try:
        existing_user = User.query.filter_by(user_email=email).first()

        if existing_user:
            logger.info(f"User with email - {email} already exists")
            return jsonify({'status': "User exists."}), 400

        # Hashed password and unique user id
        hashed_password = bcrypt_app.generate_password_hash(password).decode('utf-8')
        uid = str(uuid.uuid4())

        # Add the new user
        new_user = User(user_email=email, user_password=hashed_password, user_uid=uid)

        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user with email - {email} saved successfully")
        return jsonify({'status': 'success', 'message': 'New user saved successfully'}), 200

    except Exception as e:
        print(e)
        logger.error(f"Failed to add new user with email - {email} to the database - {e}")
        return jsonify({'status': "Issue with adding a new user."}), 500
    

@app.route("/api/v1/login", methods=['POST'])
@login_latency_histogram.time()
def login_api():
    """
    Logs in a user by email and password.

    This route expects a JSON payload containing 'email' and 'password' fields.
    It checks if the email and password match a user in the database.
    If the login is successful, it returns an access token.
    If the login fails, it returns an error response.

    Returns:
        JSON: A JSON response with an access token and email verification status or an error message.
    """
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(user_email=email).first()

    if user:
        if bcrypt_app.check_password_hash(user.user_password, password):
            data = {
                'user_id': user.id,
            }
            access_token = jwt.encode(data, os.environ.get('JWT_SECRET_KEY'), algorithm='HS256')
            logger.info(f"User with email - {email} logged in successfully")
            login_attempts_counter.labels(status='success').inc()
            return jsonify({'access_token': access_token}), 200
        
    logger.error(f"User with email - {email} tried to login")    
    login_attempts_counter.labels(status='failure').inc()
    return jsonify({'status': "Wrong email or password."}), 400


@app.route("/api/v1/user", methods=['GET'])
@validate_jwt
def user(user):
    try:
        data = {
            'email': user.user_email.split('@')[0],
            'credits': user.credits,
        }
        logger.info(f"User data was retrieved successfully - {user.id}")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error retrieving user data for user id - {user.id}: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve user data'}), 500


@app.route("/api/v1/expenses", methods=['POST'])
@validate_jwt
def add_expense(user):
    try:
        amount = request.json.get('amount')
        category = request.json.get('category')
        new_expense = Expense(amount=amount, category=category, user_id=user.id)
        db.session.add(new_expense)
        db.session.commit()
        logger.info(f"New expense was added successfully for user id - {user.id}")
        expense_additions_counter.labels(status='success').inc()
        return jsonify({'status': 'success', 'message': 'Expense added successfully'}), 200
    except Exception as e:
        logger.error(f"Error adding new expense for user id - {user.id}: {e}")
        expense_additions_counter.labels(status='failure').inc()
        return jsonify({'status': 'error', 'message': 'Failed to add expense'}), 500


@app.route("/api/v1/expenses", methods=['GET'])
@validate_jwt
def get_expenses(user):
    try:
        expenses = Expense.query.filter_by(user_id=user.id).all()
        logger.info(f"Expenses for user id - {user.id} retrieved successfully")
        return jsonify([{'amount': e.amount, 'category': e.category, 'date': e.date, 'id': e.id} for e in expenses]), 200
    except Exception as e:
        logger.error(f"Error retrieving expenses for user id - {user.id}: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve expenses'}), 500


@app.route("/api/v1/expenses/<int:expense_id>", methods=['DELETE'])
@validate_jwt
def delete_expense(user, expense_id):
    try:
        expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
        if not expense:
            logger.error(f"Expense not found or you are not authorized to delete it for user id - {user.id}")
            return jsonify({'status': 'error', 'message': 'Expense not found or you are not authorized to delete it'}), 404

        db.session.delete(expense)
        db.session.commit()
        expense_deletions_counter.labels(status='not_found').inc()
        logger.info(f"Expense deleted successfully for user id - {user.id}")
        return jsonify({'status': 'success', 'message': 'Expense deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting expense for user id - {user.id}, expense id - {expense_id}: {e}")
        expense_deletions_counter.labels(status='failure').inc()
        return jsonify({'status': 'error', 'message': 'Failed to delete expense'}), 500