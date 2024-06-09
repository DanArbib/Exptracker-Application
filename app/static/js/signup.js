document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
    var errorMessage = document.getElementById('error-message');

    if (password.length < 6) {
        errorMessage.textContent = "Password must be at least 6 characters long.";
    } else if (password !== confirmPassword) {
        errorMessage.textContent = "Passwords do not match.";
    } else {
        errorMessage.textContent = "";

        // Send the form data as JSON
        fetch('/api/v1/sign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "User exists.") {
                errorMessage.textContent = "User already exists.";
            } else {
                window.location.href = '/login';
            }
        })
        .catch(error => {
            errorMessage.textContent = "An error occurred. Please try again.";
            console.error('Error:', error);
        });
    }
});
