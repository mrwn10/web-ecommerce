// Global variables
let allProducts = [];
let currentCategory = '';

// DOM Elements
const productContainer = document.getElementById('product-container');
const loadingSpinner = document.getElementById('loading-spinner');
const searchInput = document.querySelector('.search-box input');
const categoryFilter = document.querySelector('.category-filter');

// Fetch products from API
async function fetchProducts() {
    try {
        showLoading();
        const response = await fetch('/buyer/api/products');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        allProducts = await response.json();
        displayProducts(allProducts);
        populateCategories(allProducts);
    } catch (error) {
        console.error('Error fetching products:', error);
        showError('Failed to load products. Please try again later.');
    } finally {
        hideLoading();
    }
}

// Display products in the UI
function displayProducts(products) {
    productContainer.innerHTML = '';

    if (products.length === 0) {
        productContainer.innerHTML = `
            <div class="no-products">
                <i class="fas fa-box-open"></i>
                <p>No products found</p>
            </div>
        `;
        return;
    }

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        
        // Image container
        const imageContainer = document.createElement('div');
        imageContainer.className = 'product-image-container';
        
        if (product.image) {
            const img = document.createElement('img');
            img.className = 'product-image';
            img.alt = product.product_name;
            img.src = `${product.image.replace(/\\/g, '/')}`;
            img.loading = 'lazy';
            imageContainer.appendChild(img);
        } else {
            imageContainer.innerHTML = '<div class="no-image"><i class="fas fa-image"></i> No image available</div>';
        }
        
        // Product details
        card.innerHTML = `
            <div class="product-name">${product.product_name}</div>
            <div class="product-description">${product.description || 'No description available'}</div>
            <div class="product-price">₱${parseFloat(product.product_price).toFixed(2)}</div>
            <div class="product-category">${formatCategory(product.category)}</div>
            <div class="product-meta">
                <span>Available: ${product.quantity_status}</span>
                <span>Seller: ${product.seller_name}</span>
            </div>
        `;
        
        // View Details button
        const viewDetailsButton = document.createElement('a');
        viewDetailsButton.href = `/buyer_cart?product_id=${product.product_id}`;
        viewDetailsButton.className = 'view-details-btn';
        viewDetailsButton.innerHTML = '<i class="fas fa-eye"></i> View Details';
        card.appendChild(viewDetailsButton);

        card.prepend(imageContainer);
        productContainer.appendChild(card);
    });
}

// Populate category filter dropdown
function populateCategories(products) {
    const categories = new Set();
    products.forEach(product => {
        categories.add(product.category);
    });

    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = formatCategory(category);
        categoryFilter.appendChild(option);
    });
}

// Format category name for display
function formatCategory(category) {
    if (!category) return 'Uncategorized';
    return category.replace(/_/g, ' ')
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ');
}

// Filter products based on search and category
function filterProducts() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categoryFilter.value;
    
    const filtered = allProducts.filter(product => {
        const matchesSearch = product.product_name.toLowerCase().includes(searchTerm) || 
                            (product.description && product.description.toLowerCase().includes(searchTerm));
        const matchesCategory = !selectedCategory || product.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });
    
    displayProducts(filtered);
}

// Show loading spinner
function showLoading() {
    loadingSpinner.style.display = 'flex';
    productContainer.style.display = 'none';
}

// Hide loading spinner
function hideLoading() {
    loadingSpinner.style.display = 'none';
    productContainer.style.display = 'grid';
}

// Show error message
function showError(message) {
    productContainer.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

// Event Listeners
searchInput.addEventListener('input', filterProducts);
categoryFilter.addEventListener('change', filterProducts);

// Initialize when page loads
document.addEventListener('DOMContentLoaded', fetchProducts);