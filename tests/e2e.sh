#!/bin/bash

flask_url="http://nginx"
signup_data='{"email": "test2@example.com", "password": "password123"}'
expense_data='{"amount": 50, "category": "Groceries"}'

# Check health
response=$(curl -s -o /dev/null -w "%{http_code}" $flask_url/health)

if [ $response -eq 200 ]; then
    echo "Health check passed. Status code: $response"
    exit 0
fi

# Sign up
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$signup_data" $flask_url/api/v1/sign)

if [ $response -ne 200 ]; then
    echo "Signup test failed. Status code: $response"
    exit 1
fi

# Login
login_response=$(curl -s -H "Content-Type: application/json" -d "$signup_data" $flask_url/api/v1/login)
access_token=$(echo $login_response | tr -d '\n' | sed -e 's/.*"access_token":"\([^"]*\)".*/\1/')

if [ ! -z "$access_token" ]; then
    echo "Login test passed. Access token obtained: $access_token"
else
    echo "Login test failed. Unable to obtain access token."
    exit 1
fi

# Add to database
expense_response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $access_token" -d "$expense_data" $flask_url/api/v1/expenses)

if [ $expense_response -eq 200 ]; then
    echo "Expense addition test passed. Status code: $expense_response"
fi


# Get from database
expenses_response=$(curl -s -H "Authorization: Bearer $access_token" $flask_url/api/v1/expenses)
echo "Expenses response:"
echo $expenses_response


# Delete from database
expense_id=$(echo $expenses_response | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ -z "$expense_id" ]; then
    echo "Failed to extract expense ID from response."
    exit 1
fi

echo "Expense ID created: $expense_id"

delete_response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE -H "Authorization: Bearer $access_token" $flask_url/api/v1/expenses/$expense_id)

if [ $delete_response -eq 200 ]; then
    echo "Expense deletion test passed. Status code: $delete_response"
fi


exit 0