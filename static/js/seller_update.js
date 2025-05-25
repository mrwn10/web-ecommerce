// Function to get URL parameters
        function getUrlParameter(name) {
            name = name.replace(/[\[\]]/g, '\\$&');
            const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
            const results = regex.exec(window.location.href);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, ' '));
        }

        // Function to show message
        function showMessage(type, text) {
            const messageDiv = document.getElementById('message');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${text}`;
            messageDiv.style.display = 'block';
            
            // Hide message after 5 seconds
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }

        // Function to normalize image path
        function normalizeImagePath(path) {
            if (!path) return null;
            
            // Replace backslashes with forward slashes
            let normalized = path.replace(/\\/g, '/');
            
            // Ensure the path starts correctly
            if (!normalized.startsWith('/static/') && !normalized.startsWith('static/')) {
                normalized = '/static/uploads/' + normalized.split('uploads/').pop();
            } else if (normalized.startsWith('static/')) {
                normalized = '/' + normalized;
            }
            
            return normalized;
        }

        // Get the product ID from the URL
        document.addEventListener("DOMContentLoaded", function() {
            const productId = getUrlParameter('product_id');
            
            if (!productId) {
                showMessage('error', 'No product ID specified!');
                setTimeout(() => {
                    window.location.href = '/seller-dashboard';
                }, 2000);
                return;
            }

            // Display the product ID
            document.getElementById('product-id-display').textContent = productId;
            document.getElementById('product_id').value = productId;
            
            // Fetch product details
            fetch(`/get-product-details?product_id=${productId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.message) {
                        showMessage('error', data.message);
                        setTimeout(() => {
                            window.location.href = '/seller-dashboard';
                        }, 2000);
                        return;
                    }
                    
                    // Populate form fields with product data
                    document.getElementById('product_name').value = data.product_name;
                    document.getElementById('description').value = data.description;
                    document.getElementById('product_price').value = data.product_price;
                    document.getElementById('quantity_status').value = data.quantity_status;
                    document.getElementById('category').value = data.category;
                    
                    // Handle product image display
                    const imagePreview = document.getElementById('image-preview');
                    const noImageDiv = document.getElementById('no-image');
                    const currentImageLabel = document.getElementById('current-image-label');
                    
                    if (data.image) {
                        const imageUrl = normalizeImagePath(data.image);
                        if (imageUrl) {
                            imagePreview.src = imageUrl;
                            imagePreview.style.display = 'block';
                            noImageDiv.style.display = 'none';
                            currentImageLabel.style.display = 'block';
                        } else {
                            imagePreview.style.display = 'none';
                            noImageDiv.style.display = 'flex';
                            currentImageLabel.style.display = 'none';
                        }
                    } else {
                        imagePreview.style.display = 'none';
                        noImageDiv.style.display = 'flex';
                        currentImageLabel.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching product details:', error);
                    showMessage('error', 'Error loading product details');
                });
            
            // Form submission handler
            document.getElementById('update-product-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const form = e.target;
                const formData = new FormData(form);
                
                // Show loading state
                const submitBtn = form.querySelector('.btn-submit');
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
                submitBtn.disabled = true;
                
                fetch('/update-product', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err; });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        showMessage('success', data.message);
                        setTimeout(() => {
                            window.location.href = '/seller-dashboard';
                        }, 2000);
                    } else {
                        showMessage('error', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('error', error.message || 'Error updating product');
                })
                .finally(() => {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                });
            });
            
            // Image preview handler for new uploads
            document.getElementById('image').addEventListener('change', function(e) {
                const file = e.target.files[0];
                const imagePreview = document.getElementById('image-preview');
                const noImageDiv = document.getElementById('no-image');
                const currentImageLabel = document.getElementById('current-image-label');
                
                if (file) {
                    // Validate file type
                    if (!file.type.match('image.*')) {
                        showMessage('error', 'Please select a valid image file (JPEG, PNG, etc.)');
                        e.target.value = '';
                        return;
                    }
                    
                    // Validate file size (max 5MB)
                    if (file.size > 5 * 1024 * 1024) {
                        showMessage('error', 'Image size must be less than 5MB');
                        e.target.value = '';
                        return;
                    }
                    
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        imagePreview.src = event.target.result;
                        imagePreview.style.display = 'block';
                        noImageDiv.style.display = 'none';
                        currentImageLabel.textContent = 'New Image Preview:';
                        currentImageLabel.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                } else {
                    // If no file selected, revert to current image
                    if (imagePreview.src && !imagePreview.src.includes('data:')) {
                        currentImageLabel.textContent = 'Current Image:';
                        currentImageLabel.style.display = 'block';
                        noImageDiv.style.display = 'none';
                    } else {
                        currentImageLabel.style.display = 'none';
                        noImageDiv.style.display = 'flex';
                    }
                }
            });
        });