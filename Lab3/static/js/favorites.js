document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        return null;
    }

    // Function to toggle favorite
    async function toggleFavorite(button, activityId) {
        try {
            const response = await fetch('/toggle-favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    activity_id: activityId
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Update all buttons for this activity on the page
                const buttons = document.querySelectorAll(`[data-activity-id="${activityId}"]`);
                buttons.forEach(btn => {
                    const icon = btn.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        icon.style.color = 'red';
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        icon.style.color = '';
                    }
                    // Store the favorite state
                    btn.dataset.isFavorite = data.is_favorite;
                });

                // Store favorite state in localStorage
                const favorites = JSON.parse(localStorage.getItem('favorites') || '{}');
                favorites[activityId] = data.is_favorite;
                localStorage.setItem('favorites', JSON.stringify(favorites));
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    }

    // Add click handlers to all favorite buttons
    document.querySelectorAll('.favorite-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.dataset.activityId;
            toggleFavorite(this, activityId);
        });
    });

    // Restore favorite states from localStorage on page load
    const favorites = JSON.parse(localStorage.getItem('favorites') || '{}');
    for (const [activityId, isFavorite] of Object.entries(favorites)) {
        const buttons = document.querySelectorAll(`[data-activity-id="${activityId}"]`);
        buttons.forEach(button => {
            const icon = button.querySelector('i');
            if (isFavorite) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = 'red';
            }
        });
    }
}); 