document.addEventListener('DOMContentLoaded', function() {
    // Initialize core functionality
    initializeAnimations();
    initializeFormInteractions();
    initializeNotifications();
    
    // Initialize auto-refresh for dashboard
    if (window.location.pathname === '/' || window.location.pathname.includes('dashboard')) {
        initializeDashboardFeatures();
    }
    
    // Update alert destination field based on method selection
    function updateDestinationField() {
        const method = document.getElementById('id_method');
        const destinationField = document.getElementById('id_destination');
        const destinationLabel = document.querySelector('label[for="id_destination"]');
        
        if (!method || !destinationField) return;
        
        // Add smooth transition
        destinationField.style.transition = 'all 0.3s ease';
        
        switch(method.value) {
            case 'email':
                destinationLabel.textContent = 'Email Address';
                destinationField.type = 'email';
                destinationField.placeholder = 'your@email.com';
                break;
            case 'telegram':
                destinationLabel.textContent = 'Telegram Chat ID';
                destinationField.type = 'text';
                destinationField.placeholder = '123456789';
                break;
            case 'slack':
                destinationLabel.textContent = 'Slack Webhook URL';
                destinationField.type = 'url';
                destinationField.placeholder = 'https://hooks.slack.com/services/...';
                break;
        }
        
        // Animate field update
        destinationField.style.transform = 'scale(0.98)';
        setTimeout(() => {
            destinationField.style.transform = 'scale(1)';
        }, 150);
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

// Initialize animations
function initializeAnimations() {
    // Animate cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    // Observe all cards that don't already have animation class
    document.querySelectorAll('.card:not(.animate-fade-in)').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease-out';
        observer.observe(card);
    });
    
    // Add hover effects to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

// Initialize form interactions
function initializeFormInteractions() {
    // Add focus effects to form inputs
    document.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            // Validate on blur
            validateField(this);
        });
        
        // Real-time validation for some fields
        if (input.type === 'url') {
            input.addEventListener('input', function() {
                debounce(() => validateField(this), 500)();
            });
        }
    });
    
    // Form submission animation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<div class="spinner"></div> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
}

// Initialize chart data if available
function initializeChartData() {
    const chartData = document.getElementById('chart-data');
    if (chartData) {
        try {
            const labels = JSON.parse(chartData.dataset.labels || '[]');
            const uptime = JSON.parse(chartData.dataset.uptime || '[]');
            const responseTimes = JSON.parse(chartData.dataset.responseTimes || '[]');
            
            // Store globally for chart initialization
            window.chartData = { labels, uptime, responseTimes };
        } catch (e) {
            console.warn('Failed to parse chart data:', e);
            window.chartData = { labels: [], uptime: [], responseTimes: [] };
        }
    }
}

// Auto-refresh functionality
function startAutoRefresh() {
    let refreshInterval;
    
    const startRefresh = () => {
        refreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                refreshStats();
            }
        }, 30000); // Refresh every 30 seconds
    };
    
    const stopRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    };
    
    // Start refresh and handle visibility changes
    startRefresh();
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            startRefresh();
        } else {
            stopRefresh();
        }
    });
}

// Refresh dashboard stats
function refreshStats() {
    fetch(window.location.href, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        
        // Update stats cards with animation
        const statsCards = document.querySelectorAll('.grid .card');
        const newStatsCards = newDoc.querySelectorAll('.grid .card');
        
        statsCards.forEach((card, index) => {
            if (newStatsCards[index]) {
                // Animate the update
                card.style.transition = 'transform 0.3s ease';
                card.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    card.innerHTML = newStatsCards[index].innerHTML;
                    card.style.transform = 'scale(1)';
                }, 150);
            }
        });
        
        // Show update indicator
        showUpdateIndicator();
    })
    .catch(error => {
        console.warn('Failed to refresh stats:', error);
    });
}

// Show update indicator
function showUpdateIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'fixed top-4 right-4 bg-green-500 text-white px-3 py-2 rounded-lg shadow-lg z-50 animate-fade-in';
    indicator.textContent = 'Updated';
    document.body.appendChild(indicator);
    
    setTimeout(() => {
        indicator.remove();
    }, 3000);
}

// Field validation
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // URL validation
    if (field.type === 'url' && value) {
        try {
            new URL(value);
        } catch {
            isValid = false;
            message = 'Please enter a valid URL';
        }
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
    }
    
    // Update field styling
    field.classList.toggle('border-red-300', !isValid);
    field.classList.toggle('border-green-300', isValid && value);
    
    // Show/hide validation message
    let validationMsg = field.parentElement.querySelector('.validation-message');
    if (!isValid && message) {
        if (!validationMsg) {
            validationMsg = document.createElement('p');
            validationMsg.className = 'validation-message text-sm text-red-600 mt-1';
            field.parentElement.appendChild(validationMsg);
        }
        validationMsg.textContent = message;
    } else if (validationMsg) {
        validationMsg.remove();
    }
    
    return isValid;
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize notifications
function initializeNotifications() {
    // Mark notification as read when clicked
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!this.dataset.notificationId) return;
            
            // Mark as read
            fetch(`/notifications/${this.dataset.notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            }).then(response => {
                if (response.ok) {
                    this.classList.remove('unread');
                    this.style.opacity = '0.7';
                }
            }).catch(error => {
                console.warn('Failed to mark notification as read:', error);
            });
        });
    });
}

// Initialize dashboard features
function initializeDashboardFeatures() {
    // Auto-refresh stats every 2 minutes
    let refreshInterval;
    
    const startAutoRefresh = () => {
        refreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                refreshDashboardStats();
            }
        }, 120000); // Refresh every 2 minutes
    };
    
    const stopAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    };
    
    // Handle visibility changes
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Add click handlers for check now buttons
    document.querySelectorAll('[data-action="check-now"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            this.innerHTML = '<div class="loading-spinner"></div> Checking...';
            this.disabled = true;
            
            // Re-enable after 5 seconds
            setTimeout(() => {
                this.innerHTML = 'Check Now';
                this.disabled = false;
            }, 5000);
            
            // Proceed with the original action
            if (this.href) {
                window.location.href = this.href;
            }
        });
    });
}

// Refresh dashboard statistics
function refreshDashboardStats() {
    const statsSection = document.getElementById('stats-section');
    if (!statsSection) return;
    
    fetch(window.location.href, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        const newStatsSection = newDoc.getElementById('stats-section');
        
        if (newStatsSection) {
            // Animate the update
            statsSection.style.transition = 'opacity 0.3s ease';
            statsSection.style.opacity = '0.7';
            
            setTimeout(() => {
                statsSection.innerHTML = newStatsSection.innerHTML;
                statsSection.style.opacity = '1';
                
                // Show success indicator
                showUpdateNotification('Stats updated', 'success');
            }, 300);
        }
    })
    .catch(error => {
        console.error('Failed to refresh dashboard stats:', error);
        showUpdateNotification('Failed to update stats', 'error');
    });
}

// Show update notification
function showUpdateNotification(message, type = 'success') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
    
    notification.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-fade-in`;
    notification.innerHTML = `
        <div class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                ${type === 'success' ? 
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>' :
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
                }
            </svg>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Utility: Get CSRF token
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

// Example tracking code to include in your pages
window.addEventListener('load', function() {
    const startTime = Date.now();
    let scrollDepth = 0;
    let trackClicksCount = 0;
    
    // Track clicks
    document.addEventListener('click', function() {
        trackClicksCount++;
    });
    
    window.addEventListener('scroll', function() {
        scrollDepth = Math.max(scrollDepth, 
            (window.scrollY + window.innerHeight) / document.body.scrollHeight * 100
        );
    });
    
    window.addEventListener('beforeunload', function() {
        navigator.sendBeacon('/track-engagement', JSON.stringify({
            url: window.location.pathname,
            duration: (Date.now() - startTime) / 1000,
            scroll_depth: scrollDepth,
            interactions: trackClicksCount
        }));
    });
});