// Global variables
let currentQuantity = 1;
let productPrice = 0;
let productStock = 0;
let userId = null;

// Get product ID from URL parameter
const urlParams = new URLSearchParams(window.location.search);
const productId = urlParams.get('product_id');

// DOM Elements
const productDetailContainer = document.getElementById('product-detail-container');
const loadingSpinner = document.getElementById('loading-spinner');

// Notification position fixed to top-right
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');
    
    // Validate notification parameters
    if (!message || typeof message !== 'string') {
        console.warn('Invalid notification parameters:', {message, type});
        return;
    }
    
    // Set appropriate icon based on type
    let iconClass = 'fa-check-circle';
    if (type === 'error') iconClass = 'fa-exclamation-circle';
    if (type === 'warning') iconClass = 'fa-exclamation-triangle';
    
    // Set message and style
    notification.innerHTML = `<i class="fas ${iconClass}"></i> <span id="notification-message">${message}</span>`;
    notification.className = `notification ${type}`;
    
    // Position fixed to top-right
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.display = 'block';
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Fetch current user ID from server
async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/current-user');
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        const userData = await response.json();
        userId = userData.user_id;
    } catch (error) {
        console.error('Error fetching user:', error);
        // Redirect to login if not authenticated
        window.location.href = '/login';
    }
}

// Fetch product details
async function fetchProductDetails() {
    try {
        showLoading();
        await fetchCurrentUser(); // Ensure we have user ID first
        
        const response = await fetch(`/buyer/api/products/${productId}`);
        
        if (!response.ok) {
            throw new Error('Product not found');
        }
        
        const product = await response.json();
        productPrice = parseFloat(product.product_price);
        productStock = parseInt(product.quantity_status);
        displayProductDetails(product);
    } catch (error) {
        console.error('Error fetching product:', error);
        showError('Failed to load product details. Please try again later.');
    } finally {
        hideLoading();
    }
}

// Display product details
function displayProductDetails(product) {
    const isOutOfStock = productStock <= 0;
    
    productDetailContainer.innerHTML = `
        <div class="product-detail-card">
            <div class="product-detail-image-container">
                ${product.image ? 
                    `<img src="${product.image.replace(/\\/g, '/')}" alt="${product.product_name}" class="product-detail-image">` : 
                    '<div class="no-image"><i class="fas fa-image"></i> No image available</div>'}
            </div>
            <div class="product-detail-info">
                <h1 class="product-detail-name">${product.product_name}</h1>
                <div class="price-section">
                    <div class="product-detail-price">₱${productPrice.toFixed(2)}</div>
                    <div class="subtotal">Subtotal: ₱<span id="subtotal-value">${productPrice.toFixed(2)}</span></div>
                </div>
                <div class="product-detail-category">${formatCategory(product.category)}</div>
                
                <div class="product-detail-description">
                    <h3>Description</h3>
                    <p>${product.description || 'No description available'}</p>
                </div>
                
                <div class="product-detail-meta">
                    <div><i class="fas fa-store"></i> Seller: ${product.seller_name}</div>
                    <div><i class="fas fa-cubes"></i> Availability: ${productStock} units</div>
                </div>
                
                ${isOutOfStock ? 
                    '<div class="out-of-stock">This product is currently out of stock</div>' : 
                    `
                    <div class="quantity-selector">
                        <span class="quantity-label">Quantity:</span>
                        <div class="quantity-controls">
                            <button class="quantity-btn minus-btn">
                                <i class="fas fa-minus"></i>
                            </button>
                            <input type="number" class="quantity-input" value="1" min="1" max="${productStock}">
                            <button class="quantity-btn plus-btn">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                    `}
                    
                <div class="product-detail-actions">
                    ${isOutOfStock ? '' : `
                    <button class="add-to-cart-btn">
                        <i class="fas fa-cart-plus"></i> Add to Cart
                    </button>
                    <button class="buy-now-btn">
                        <i class="fas fa-bolt"></i> Buy Now
                    </button>
                    `}
                    <button class="back-to-dashboard-btn">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Initialize event listeners properly
    if (!isOutOfStock) {
        // Quantity controls
        const minusBtn = document.querySelector('.minus-btn');
        const plusBtn = document.querySelector('.plus-btn');
        const quantityInput = document.querySelector('.quantity-input');
        
        minusBtn.addEventListener('click', () => adjustQuantity(-1));
        plusBtn.addEventListener('click', () => adjustQuantity(1));
        
        quantityInput.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                value = 1;
            } else if (value > productStock) {
                value = productStock;
            }
            this.value = value;
            currentQuantity = value;
            updateSubtotal();
            updateButtonStates();
        });
        
        // Action buttons
        document.querySelector('.add-to-cart-btn').addEventListener('click', 
            () => addToCart(product.product_id));
        document.querySelector('.buy-now-btn').addEventListener('click', 
            () => buyNow(product.product_id));
        
        updateButtonStates();
    }
    
    // Back to dashboard button
    document.querySelector('.back-to-dashboard-btn').addEventListener('click', 
        () => window.location.href = '/buyer_dashboard');
}

// Adjust quantity function
function adjustQuantity(change) {
    const quantityInput = document.querySelector('.quantity-input');
    let newValue = parseInt(quantityInput.value) + change;
    
    if (newValue < 1) newValue = 1;
    if (newValue > productStock) newValue = productStock;
    
    quantityInput.value = newValue;
    currentQuantity = newValue;
    updateSubtotal();
    updateButtonStates();
}

// Update button states based on quantity
function updateButtonStates() {
    const minusBtn = document.querySelector('.minus-btn');
    const plusBtn = document.querySelector('.plus-btn');
    
    if (minusBtn && plusBtn) {
        minusBtn.disabled = currentQuantity <= 1;
        plusBtn.disabled = currentQuantity >= productStock;
    }
}

// Update subtotal calculation
function updateSubtotal() {
    const subtotalValue = document.getElementById('subtotal-value');
    const subtotal = (productPrice * currentQuantity).toFixed(2);
    subtotalValue.textContent = subtotal;
}

// Format category name for display
function formatCategory(category) {
    if (!category) return 'Uncategorized';
    return category.replace(/_/g, ' ')
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ');
}

// Add to cart function
async function addToCart(productId) {
    const quantity = currentQuantity;
    
    try {
        if (!userId) {
            throw new Error('You must be logged in to add items to cart');
        }
        
        if (quantity > productStock) {
            throw new Error(`Only ${productStock} units available`);
        }
        
        if (productStock <= 0) {
            throw new Error('This product is out of stock');
        }
        
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                quantity: quantity
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to add to cart');
        }
        
        // Show success notification
        showNotification(`Added ${quantity} item(s) to cart!`);
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        
        if (error.message.includes('logged in')) {
            // Redirect to login page if not authenticated
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        } else {
            // Show error notification
            showNotification(`Error: ${error.message}`, 'error');
            
            // Handle insufficient stock specifically
            if (error.message.includes('Only') || error.message.includes('out of stock')) {
                // Refresh product details to show updated stock
                fetchProductDetails();
            }
        }
    }
}

// Buy now function
async function buyNow(productId) {
    const quantity = currentQuantity;
    
    try {
        if (!userId) {
            throw new Error('You must be logged in to place an order');
        }
        
        if (quantity > productStock) {
            throw new Error(`Only ${productStock} units available`);
        }
        
        const response = await fetch('/order/buy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                quantity: quantity
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to place order');
        }
        
        // Show success notification
        showNotification(`Order placed successfully!`);
        
        // Refresh product details to show updated stock
        fetchProductDetails();
        
    } catch (error) {
        console.error('Error placing order:', error);
        
        if (error.message.includes('logged in')) {
            // Redirect to login page if not authenticated
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        } else {
            // Show error notification
            showNotification(`Error: ${error.message}`, 'error');
        }
    }
}

// Show loading spinner
function showLoading() {
    loadingSpinner.style.display = 'flex';
    productDetailContainer.style.display = 'none';
}

// Hide loading spinner
function hideLoading() {
    loadingSpinner.style.display = 'none';
    productDetailContainer.style.display = 'block';
}

// Show error message
function showError(message) {
    productDetailContainer.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <a href="/buyer_dashboard" class="back-to-dashboard-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
    `;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Ensure notification is hidden on initial load
    document.getElementById('notification').style.display = 'none';
    fetchProductDetails();
});