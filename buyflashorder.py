from flask import Blueprint, jsonify, request
from database import get_connection
import base64
import os

buyflashorder = Blueprint('buyflashorder', __name__)

# Function to convert image data to base64
def encode_image(image_blob):
    return base64.b64encode(image_blob).decode('utf-8')

# Route to get all cart and order data
@buyflashorder.route('/get_cart_orders', methods=['GET'])
def get_cart_orders():
    user_id = request.args.get('user_id')  # Get user_id from query string

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    response_data = {
        "cart": [],
        "orders": []
    }

    # -----------------------------
    # Fetch cart items
    # -----------------------------
    if user_id:
        cursor.execute(
            "SELECT cart_id, user_id, product_id, quantity, price_at_add, added_at FROM cart WHERE user_id = %s",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT cart_id, user_id, product_id, quantity, price_at_add, added_at FROM cart"
        )

    cart_items = cursor.fetchall()

    for item in cart_items:
        cursor.execute(
            "SELECT product_name, image, product_price, description FROM products WHERE product_id = %s",
            (item['product_id'],)
        )
        product = cursor.fetchone()

        image_path = product['image']
        image_data = None
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = encode_image(f.read())

        response_data['cart'].append({
            "cart_id": item['cart_id'],
            "product_id": item['product_id'],
            "product_name": product['product_name'],
            "image_url": image_data,
            "quantity": item['quantity'],
            "price_at_add": str(item['price_at_add']),
            "added_at": item['added_at'],
            "product_price": str(product['product_price']),
            "description": product.get('description', '')
        })

    # -----------------------------
    # Fetch order items
    # -----------------------------
    cursor.execute(
        "SELECT order_id, user_id, product_id, quantity, price_at_add, order_status, ordered_at FROM orders WHERE user_id = %s",
        (user_id,)
    )

    order_items = cursor.fetchall()

    for order in order_items:
        cursor.execute(
            "SELECT product_name, image, product_price, description FROM products WHERE product_id = %s",
            (order['product_id'],)
        )
        product = cursor.fetchone()

        image_path = product['image']
        image_data = None
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = encode_image(f.read())

        response_data['orders'].append({
            "order_id": order['order_id'],
            "product_id": order['product_id'],
            "product_name": product['product_name'],
            "image_url": image_data,
            "quantity": order['quantity'],
            "price_at_add": str(order['price_at_add']),
            "order_status": order['order_status'],
            "ordered_at": order['ordered_at'],
            "product_price": str(product['product_price']),
            "description": product.get('description', '')
        })

    cursor.close()
    conn.close()

    return jsonify(response_data)

# -----------------------------------------------
# Route to cancel a specific cart item
# -----------------------------------------------
@buyflashorder.route('/cancel_cart_item', methods=['POST'])
def cancel_cart_item():
    data = request.get_json()
    cart_id = data.get('cart_id')

    if not cart_id:
        return jsonify({"error": "Cart ID is required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verify the cart item exists
        cursor.execute(
            "SELECT * FROM cart WHERE cart_id = %s",
            (cart_id,)
        )
        cart_item = cursor.fetchone()

        if not cart_item:
            return jsonify({"error": "Cart item not found"}), 404

        # Simply delete the cart item - no inventory adjustment needed
        cursor.execute(
            "DELETE FROM cart WHERE cart_id = %s",
            (cart_id,)
        )

        conn.commit()
        return jsonify({"message": "Item removed from cart successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to remove cart item: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

@buyflashorder.route('/cancel_order_item', methods=['POST'])
def cancel_order_item():
    data = request.get_json()
    order_id = data.get('order_id')

    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1: Retrieve the order item (product_id and quantity)
    cursor.execute(
        "SELECT product_id, quantity FROM orders WHERE order_id = %s",
        (order_id,)
    )
    order_item = cursor.fetchone()

    if not order_item:
        cursor.close()
        conn.close()
        return jsonify({"error": "Order item not found"}), 404

    product_id = order_item['product_id']
    quantity_to_add_back = order_item['quantity']

    # Step 2: Add the quantity back to the product stock
    cursor.execute(
        "UPDATE products SET quantity_status = quantity_status + %s WHERE product_id = %s",
        (quantity_to_add_back, product_id)
    )

    # Step 3: Delete the order item
    cursor.execute(
        "DELETE FROM orders WHERE order_id = %s",
        (order_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Order item has been successfully cancelled and product stock updated"}), 200

# -----------------------------------------------
# Route to checkout cart and move items to orders
# -----------------------------------------------
@buyflashorder.route('/checkout_cart', methods=['POST'])
def checkout_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    cart_ids = data.get('cart_ids')  # New parameter for specific cart items

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Start transaction
        conn.start_transaction()

        # Build query based on whether specific cart_ids are provided
        query = "SELECT cart_id, product_id, quantity, price_at_add FROM cart WHERE user_id = %s"
        params = [user_id]
        
        if cart_ids and isinstance(cart_ids, list):
            try:
                # Convert cart_ids to integers and filter out invalid values
                cart_ids = [int(cid) for cid in cart_ids if str(cid).isdigit()]
                if not cart_ids:
                    return jsonify({"error": "No valid cart IDs provided"}), 400
                
                query += " AND cart_id IN (%s)" % ",".join(["%s"] * len(cart_ids))
                params.extend(cart_ids)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid cart IDs format"}), 400

        cursor.execute(query, params)
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({"error": "No items in cart to checkout"}), 400

        # Process each cart item
        for item in cart_items:
            # Verify product exists and has enough stock
            cursor.execute(
                "SELECT quantity_status FROM products WHERE product_id = %s",
                (item['product_id'],)
            )
            product = cursor.fetchone()

            if not product:
                conn.rollback()
                return jsonify({"error": f"Product {item['product_id']} not found"}), 404

            if item['quantity'] > product['quantity_status']:
                conn.rollback()
                return jsonify({
                    "error": f"Not enough stock for product {item['product_id']}",
                    "product_id": item['product_id'],
                    "available": product['quantity_status']
                }), 400

            # Move to orders table
            cursor.execute(
                """INSERT INTO orders 
                   (user_id, product_id, quantity, price_at_add, order_status, ordered_at)
                   VALUES (%s, %s, %s, %s, %s, NOW())""",
                (user_id, item['product_id'], item['quantity'], item['price_at_add'], 'pending')
            )

            # Update product inventory
            cursor.execute(
                "UPDATE products SET quantity_status = quantity_status - %s WHERE product_id = %s",
                (item['quantity'], item['product_id'])
            )

            # Remove from cart
            cursor.execute(
                "DELETE FROM cart WHERE cart_id = %s",
                (item['cart_id'],)
            )

        # Commit transaction if all items processed successfully
        conn.commit()

        return jsonify({
            "message": "Cart checked out successfully",
            "moved_items": len(cart_items),
            "user_id": user_id,
            "processed_cart_ids": [item['cart_id'] for item in cart_items]
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Checkout failed: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()