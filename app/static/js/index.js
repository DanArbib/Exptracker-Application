document.addEventListener('DOMContentLoaded', async function() {
    const accessToken = localStorage.getItem('access_token');
    console.log(accessToken);
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
                window.location.href = '/dashboard';
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
