document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    const response = await fetch('api/v1/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, password: password })
    });

    const data = await response.json();

    if (response.status === 200) {
        localStorage.setItem('access_token', data.access_token);
        window.location.href = '/dashboard';
    } else {
        errorMessage.textContent = data.status;
    }
});
