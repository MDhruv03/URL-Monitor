document.addEventListener('DOMContentLoaded', function() {
    // Update alert destination field based on method selection
    function updateDestinationField() {
        const method = document.getElementById('id_method').value;
        const destinationField = document.getElementById('id_destination');
        const destinationLabel = document.querySelector('label[for="id_destination"]');
        
        if (method === 'email') {
            destinationLabel.textContent = 'Email Address';
            destinationField.type = 'email';
            destinationField.placeholder = 'your@email.com';
        } else if (method === 'telegram') {
            destinationLabel.textContent = 'Telegram Chat ID';
            destinationField.type = 'text';
            destinationField.placeholder = '123456789';
        } else if (method === 'slack') {
            destinationLabel.textContent = 'Slack Webhook URL';
            destinationField.type = 'url';
            destinationField.placeholder = 'https://hooks.slack.com/services/...';
        }
    }
    
    // Initialize if method field exists
    const methodField = document.getElementById('id_method');
    if (methodField) {
        methodField.addEventListener('change', updateDestinationField);
        updateDestinationField(); // Initial call
    }
    
    // Mark notification as read when clicked
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.dataset.notificationId;
            fetch(`/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            }).then(response => {
                if (response.ok) {
                    this.classList.remove('unread');
                }
            });
            window.location.href = this.href;
        });
    });
    
    // Auto-refresh dashboard every 60 seconds
    if (window.location.pathname === '/') {
        setInterval(() => {
            fetch(window.location.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, 'text/html');
                const newContent = newDoc.querySelector('.container').innerHTML;
                document.querySelector('.container').innerHTML = newContent;
            });
        }, 60000);
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}