// Get the user details from URL parameters
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('id');
            const username = urlParams.get('username');
            const email = urlParams.get('email');
            
            if (userId && username && email) {
                document.getElementById('userId').textContent = userId;
                document.getElementById('username').textContent = username;
                document.getElementById('userEmail').textContent = email;
            } else {
                window.location.href = '/admin_users_management';
            }

            // Character count for reason textarea
            const textarea = document.getElementById('banReason');
            const charCount = document.getElementById('charCount');
            
            textarea.addEventListener('input', function() {
                const currentLength = this.value.length;
                charCount.textContent = currentLength;
                
                if (currentLength > 500) {
                    this.value = this.value.substring(0, 500);
                    charCount.textContent = 500;
                }
            });
        });
        
        function confirmBan() {
            const reason = document.getElementById('banReason').value.trim();
            if (!reason) {
                showAlert('Please provide a reason for banning this user.', 'error');
                return;
            }
            
            if (reason.length > 500) {
                showAlert('Reason cannot exceed 500 characters.', 'error');
                return;
            }
            
            const userId = document.getElementById('userId').textContent;
            const username = document.getElementById('username').textContent;
            const email = document.getElementById('userEmail').textContent;
            
            const confirmBtn = document.querySelector('.btn-confirm');
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            fetch('/api/admin/ban_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    reason: reason,
                    email: email,
                    username: username
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert('Error: ' + data.error, 'error');
                } else {
                    showAlert('User banned successfully. Notification sent.', 'success', () => {
                        window.location.href = '/admin_users_management';
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="fas fa-ban"></i> Confirm Ban';
            });
        }

        function showAlert(message, type, callback) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.innerHTML = `
                <div class="alert-content">
                    <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
                    <span>${message}</span>
                </div>
                <i class="fas fa-times close-alert"></i>
            `;
            
            document.body.appendChild(alertDiv);
            
            setTimeout(() => {
                alertDiv.classList.add('show');
            }, 10);
            
            const closeBtn = alertDiv.querySelector('.close-alert');
            closeBtn.addEventListener('click', () => {
                alertDiv.classList.remove('show');
                setTimeout(() => {
                    alertDiv.remove();
                    if (callback) callback();
                }, 300);
            });
            
            if (type === 'success') {
                setTimeout(() => {
                    alertDiv.classList.remove('show');
                    setTimeout(() => {
                        alertDiv.remove();
                        if (callback) callback();
                    }, 300);
                }, 3000);
            }
        }