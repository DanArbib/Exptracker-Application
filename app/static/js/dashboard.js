// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', async function() {

    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
        try {
            const response = await fetch('/api/v1/user', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            if (response.ok) {
                const userData = await response.json();
                document.getElementById('userEmail').textContent = userData.email;
                // Fetch and display expenses
                fetchExpenses(accessToken);
            } else {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
            window.location.href = '/login';
        }
    } else {
        window.location.href = '/login';
    }
});

async function fetchExpenses(token) {
    const response = await fetch('/api/v1/expenses', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (response.ok) {
        const expenses = await response.json();
        const expenseList = document.getElementById('expenseList');
        expenses.forEach(expense => {
            const li = document.createElement('li');
            li.id = `expense_${expense.id}`;
            li.innerHTML = `Price: $${expense.amount} | Category: ${expense.category} | Date: ${expense.date} 
                <button class="deletebtn" onclick="deleteExpense(${expense.id})">Delete</button>`;
            expenseList.appendChild(li);
        });
    }
}

async function addExpense() {
    const amount = parseFloat(prompt("Enter the expense amount:"));
    if (isNaN(amount)) {
        alert("Please enter a valid amount.");
        return;
    }
    
    const category = prompt("Enter the expense category:");
    if (!category) {
        alert("Please enter a category.");
        return;
    }

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        alert("Access token not found. Please login.");
        return;
    }

    const expenseData = {
        amount: amount,
        category: category
    };

    try {
        const response = await fetch('/api/v1/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(expenseData)
        });

        if (response.ok) {
            fetchExpenses(accessToken);
        } else {
            throw new Error('Error adding expense');
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        alert("Failed to add expense. Please try again later.");
    }
}


async function deleteExpense(expenseId) {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        alert("Access token not found. Please login.");
        return;
    }

    try {
        const response = await fetch(`/api/v1/expenses/${expenseId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (response.ok) {
            // Remove the expense from the UI
            document.getElementById(`expense_${expenseId}`).remove();
        } else {
            throw new Error('Error deleting expense');
        }
    } catch (error) {
        console.error('Error deleting expense:', error);
        alert("Failed to delete expense. Please try again later.");
    }
}

