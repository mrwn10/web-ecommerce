// Global variables
const successToast = new bootstrap.Toast(document.getElementById('successToast'));
const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
let currentActiveTab = 'orders'; // Track current active tab

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadInitialData();
});

function initializeEventListeners() {
    // Tab change event
    const tabEls = document.querySelectorAll('#purchasesTab button[data-bs-toggle="tab"]');
    tabEls.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            currentActiveTab = event.target.getAttribute('aria-controls');
        });
    });

    // Cancel button event delegation
    document.addEventListener('click', function(e) {
        const cancelBtn = e.target.closest('.cancel-btn');
        if (cancelBtn) {
            const itemId = cancelBtn.dataset.id;
            const itemType = cancelBtn.dataset.type;
            const itemName = cancelBtn.dataset.name;
            showCancelModal(itemId, itemType, itemName);
        }
    });

    // Checkout button event delegation
    document.addEventListener('click', function(e) {
        const checkoutBtn = e.target.closest('.checkout-btn');
        if (checkoutBtn) {
            const cartId = checkoutBtn.dataset.id;
            checkoutCartItem(cartId);
        }
    });

    // Checkout All button event
    document.addEventListener('click', function(e) {
        if (e.target.id === 'checkoutAllBtn') {
            checkoutAllCartItems();
        }
    });

    // Confirm cancel button
    document.getElementById('confirmCancel').addEventListener('click', confirmCancelAction);
}

function loadInitialData() {
    const userId = getUserId();
    if (!userId) {
        redirectToLogin();
        return;
    }
    fetchCartAndOrders(userId);
}

function getUserId() {
    // Check multiple possible sources for user_id
    return CURRENT_USER_ID || 
           document.querySelector('meta[name="user-id"]')?.content || 
           sessionStorage.getItem('user_id') || 
           localStorage.getItem('user_id');
}

function redirectToLogin() {
    showError('Please log in to view your orders and cart');
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

async function fetchCartAndOrders(userId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/get_cart_orders?user_id=${userId}`);
        
        if (!response.ok) {
            if (response.status === 401) {
                redirectToLogin();
                return;
            }
            throw new Error('Failed to fetch data');
        }
        
        const data = await response.json();
        renderOrders(data.orders);
        renderCart(data.cart);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to load data. Please try again.');
    } finally {
        showLoading(false);
    }
}

function renderOrders(orders = []) {
    const container = document.getElementById('orders-container');
    
    if (!orders.length) {
        container.innerHTML = `
            <div class="col-12 empty-state py-5">
                <i class="fas fa-clipboard-list fa-3x mb-3"></i>
                <h4>No Orders Yet</h4>
                <p class="text-muted">You haven't placed any orders yet.</p>
                <a href="/buyer_dashboard" class="btn btn-purple mt-3">Start Shopping</a>
            </div>
        `;
        return;
    }

    container.innerHTML = orders.map(order => {
        const statusClass = getStatusClass(order.order_status);
        const formattedDate = formatDate(order.ordered_at);
        const totalPrice = parseFloat(order.price_at_add).toFixed(2);
        const unitPrice = (order.price_at_add / order.quantity).toFixed(2);
        const canCancel = !['completed', 'cancelled', 'delivered'].includes(order.order_status.toLowerCase());

        return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card product-card h-100">
                ${order.image_url ? 
                    `<img src="data:image/jpeg;base64,${order.image_url}" class="card-img-top product-image" alt="${order.product_name}">` : 
                    `<div class="product-image-placeholder d-flex align-items-center justify-content-center">
                        <i class="fas fa-image fa-3x text-muted"></i>
                    </div>`
                }
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${escapeHtml(order.product_name)}</h5>
                    <p class="card-text text-muted flex-grow-1">${truncateDescription(order.description)}</p>
                    <ul class="list-group list-group-flush mb-3">
                        <li class="list-group-item">Quantity: ${order.quantity}</li>
                        <li class="list-group-item">Price: ₱${unitPrice} each</li>
                        <li class="list-group-item fw-bold">Total: ₱${totalPrice}</li>
                        <li class="list-group-item">Ordered: ${formattedDate}</li>
                    </ul>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="status-badge ${statusClass}">${capitalizeFirstLetter(order.order_status)}</span>
                        ${canCancel ? `
                        <button class="btn btn-outline-danger btn-sm cancel-btn" 
                                data-id="${order.order_id}" 
                                data-type="order"
                                data-name="${escapeHtml(order.product_name)}">
                            <i class="fas fa-times-circle me-1"></i>Cancel
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function renderCart(cartItems = []) {
    const container = document.getElementById('cart-container');
    
    if (!cartItems.length) {
        container.innerHTML = `
            <div class="col-12 empty-state py-5">
                <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                <h4>Your Cart is Empty</h4>
                <p class="text-muted">Add some products to get started!</p>
                <a href="/buyer_dashboard" class="btn btn-purple mt-3">Browse Products</a>
            </div>
        `;
        return;
    }

    // Calculate total price for all items
    const totalCartPrice = cartItems.reduce((sum, item) => sum + parseFloat(item.price_at_add), 0).toFixed(2);

    // Add Checkout All button at the top
    container.innerHTML = `
        <div class="col-12 mb-4">
            <div class="card summary-card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Total Items: ${cartItems.length}</h5>
                        <h4 class="mb-0 text-purple">₱${totalCartPrice}</h4>
                    </div>
                </div>
            </div>
            <button id="checkoutAllBtn" class="btn btn-purple w-100">
                <i class="fas fa-shopping-bag me-2"></i>Checkout All Items
            </button>
        </div>
    `;

    // Render each cart item
    container.innerHTML += cartItems.map(item => {
        const formattedDate = formatDate(item.added_at);
        const totalPrice = parseFloat(item.price_at_add).toFixed(2);
        const unitPrice = (item.price_at_add / item.quantity).toFixed(2);

        return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card product-card h-100">
                ${item.image_url ? 
                    `<img src="data:image/jpeg;base64,${item.image_url}" class="card-img-top product-image" alt="${item.product_name}">` : 
                    `<div class="product-image-placeholder d-flex align-items-center justify-content-center">
                        <i class="fas fa-image fa-3x text-muted"></i>
                    </div>`
                }
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${escapeHtml(item.product_name)}</h5>
                    <p class="card-text text-muted flex-grow-1">${truncateDescription(item.description)}</p>
                    <ul class="list-group list-group-flush mb-3">
                        <li class="list-group-item">Quantity: ${item.quantity}</li>
                        <li class="list-group-item">Price: ₱${unitPrice} each</li>
                        <li class="list-group-item fw-bold">Total: ₱${totalPrice}</li>
                        <li class="list-group-item">Added: ${formattedDate}</li>
                    </ul>
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-purple btn-sm checkout-btn" 
                                data-id="${item.cart_id}">
                            <i class="fas fa-shopping-bag me-1"></i>Checkout
                        </button>
                        <button class="btn btn-outline-danger btn-sm cancel-btn" 
                                data-id="${item.cart_id}" 
                                data-type="cart"
                                data-name="${escapeHtml(item.product_name)}">
                            <i class="fas fa-trash-alt me-1"></i>Remove
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

async function checkoutCartItem(cartId) {
    try {
        const userId = getUserId();
        if (!userId) {
            redirectToLogin();
            return;
        }

        const response = await fetch('/checkout_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                cart_ids: [parseInt(cartId)]  // Send as array with single cart ID
            }),
            credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to checkout item');
        }

        const data = await response.json();
        showSuccess(data.message || 'Item checked out successfully');
        fetchCartAndOrders(userId);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to checkout item. Please try again.');
    }
}

async function checkoutAllCartItems() {
    const userId = getUserId();
    if (!userId) {
        redirectToLogin();
        return;
    }

    try {
        const response = await fetch('/checkout_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId
                // No cart_ids specified means checkout all
            }),
            credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to checkout all items');
        }

        const data = await response.json();
        showSuccess(data.message || 'All items checked out successfully');
        fetchCartAndOrders(userId);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to checkout items. Please try again.');
    }
}

function showCancelModal(itemId, itemType, itemName) {
    const modal = new bootstrap.Modal(document.getElementById('cancelModal'));
    const confirmBtn = document.getElementById('confirmCancel');
    const modalText = document.getElementById('cancelModalText');
    const modalDesc = document.getElementById('cancelModalDescription');
    
    // Store data on confirm button
    confirmBtn.dataset.currentId = itemId;
    confirmBtn.dataset.currentType = itemType;
    
    // Set modal content based on item type
    if (itemType === 'cart') {
        modalText.textContent = `Remove "${itemName}" from your cart?`;
        modalDesc.textContent = 'This item will be permanently removed from your cart.';
    } else {
        modalText.textContent = `Cancel your order for "${itemName}"?`;
        modalDesc.textContent = 'The product quantity will be returned to inventory.';
    }
    
    modal.show();
}

function confirmCancelAction() {
    const itemId = this.dataset.currentId;
    const itemType = this.dataset.currentType;
    cancelItem(itemId, itemType);
}

async function cancelItem(itemId, itemType) {
    const endpoint = itemType === 'cart' ? '/cancel_cart_item' : '/cancel_order_item';
    const userId = getUserId();
    
    if (!userId) {
        redirectToLogin();
        return;
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                [itemType === 'cart' ? 'cart_id' : 'order_id']: itemId
            }),
            credentials: 'include'
        });

        if (response.status === 401) {
            redirectToLogin();
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to process request');
        }

        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            const successMessage = itemType === 'cart' 
                ? 'Item removed from cart successfully' 
                : 'Order cancelled successfully';
            showSuccess(successMessage);
            fetchCartAndOrders(userId);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to process request. Please try again.');
    } finally {
        bootstrap.Modal.getInstance(document.getElementById('cancelModal')).hide();
    }
}

function refreshData() {
    const userId = getUserId();
    if (userId) {
        fetchCartAndOrders(userId);
        showSuccess('Data refreshed successfully');
    } else {
        redirectToLogin();
    }
}

// Helper functions
function getStatusClass(status) {
    if (!status) return 'status-pending';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('pending')) return 'status-pending';
    if (statusLower.includes('processing')) return 'status-processing';
    if (statusLower.includes('completed')) return 'status-completed';
    if (statusLower.includes('cancelled')) return 'status-cancelled';
    if (statusLower.includes('shipped')) return 'status-shipped';
    if (statusLower.includes('delivered')) return 'status-delivered';
    return 'status-pending';
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    try {
        const date = new Date(dateString);
        return isNaN(date) ? 'Invalid date' : date.toLocaleString();
    } catch {
        return 'Invalid date';
    }
}

function truncateDescription(desc, length = 100) {
    if (!desc) return 'No description available';
    return desc.length > length ? desc.substring(0, length) + '...' : desc;
}

function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showLoading(show) {
    if (show) {
        document.getElementById('orders-container').innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-purple" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading your orders...</p>
            </div>
        `;
        document.getElementById('cart-container').innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-purple" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading your cart items...</p>
            </div>
        `;
    }
}

function showSuccess(message) {
    document.getElementById('successToastMessage').textContent = message;
    successToast.show();
}

function showError(message) {
    document.getElementById('errorToastMessage').textContent = message;
    errorToast.show();
}