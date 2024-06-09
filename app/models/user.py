from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String(36), unique=True, nullable=False)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    user_password = db.Column(db.String(60), nullable=True)
    user_joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    credits = db.Column(db.Integer, default=10)

    # Joined date formatted
    def joined_date_formatted(self):
        return self.user_joined_date.strftime('%Y-%m-%d')

    def __repr__(self):
        return f'<User {self.user_email}>'
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))


