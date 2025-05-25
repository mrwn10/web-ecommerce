window.onclick = function(event) {
  var modal = document.getElementById('addModal');

  // Close modal if click is outside of the modal content
  if (event.target === modal) {
    modal.style.display = "none";
  }
}

// Function to handle product deletion
function deleteProduct(productId, event) {
  event.preventDefault(); // Prevent default link behavior
  
  if (confirm('Are you sure you want to delete this product?')) {
    // Show loading state
    const deleteBtn = event.target;
    const originalText = deleteBtn.innerHTML;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
    deleteBtn.style.pointerEvents = 'none'; // Disable the button

    // Create form data
    const formData = new FormData();
    formData.append('product_id', productId);

    // Send delete request
    fetch('/delete-product', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Reload the product list
        location.reload();
      } else {
        alert(data.message || 'Failed to delete product');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error deleting product');
    })
    .finally(() => {
      // Restore button state
      deleteBtn.innerHTML = originalText;
      deleteBtn.style.pointerEvents = 'auto';
    });
  }
}

// Fetch and display product data
document.addEventListener("DOMContentLoaded", function () {
  fetch('/get-products')
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('product-table-container');
      if (data.length === 0) {
        container.innerHTML = "<p>No products found.</p>";
        return;
      }

      let table = `
        <table>
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Description</th>
              <th>Price</th>
              <th>Quantity</th>
              <th>Category</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
      `;

      data.forEach(product => {
        table += `
          <tr>
            <td>${product.product_name}</td>
            <td>${product.description}</td>
            <td>${product.product_price}</td>
            <td>${product.quantity_status}</td>
            <td>${product.category.replace(/_/g, ' ')}</td>
            <td class="action-buttons">
              <a href="/seller_update?product_id=${product.product_id}" class="btn-update">Update</a>
              <a href="#" onclick="deleteProduct('${product.product_id}', event)" class="btn-delete">Delete</a>
            </td>
          </tr>
        `;
      });

      table += `</tbody></table>`;
      container.innerHTML = table;
    })
    .catch(error => {
      console.error('Error fetching product data:', error);
    });
});