// Fetch current user data when page loads
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/buyer/account-settings')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const user = data.data;
                        document.getElementById('username').value = user.username || '';
                        document.getElementById('email').value = user.email || '';
                        document.getElementById('province').value = user.province || '';
                        document.getElementById('municipal').value = user.municipal || '';
                        document.getElementById('barangay').value = user.barangay || '';
                        document.getElementById('contact_number').value = user.contact_number || '';
                    }
                });
        });

        // Handle update
        document.getElementById('update-btn').addEventListener('click', function() {
            const userData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                province: document.getElementById('province').value,
                municipal: document.getElementById('municipal').value,
                barangay: document.getElementById('barangay').value,
                contact_number: document.getElementById('contact_number').value
            };

            fetch('/buyer/account-settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Account updated successfully!');
                } else {
                    alert('Error: ' + data.message);
                }
            });
        });