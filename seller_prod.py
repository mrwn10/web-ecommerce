from flask import Blueprint, request, jsonify, render_template, session
from database import get_connection
import mysql.connector

seller_prod = Blueprint('seller_prod', __name__)

@seller_prod.route('/seller_products')
def seller_dashboard():
    # Get the logged-in seller's ID from session
    seller_id = session.get('user_id')
    
    if not seller_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to get all orders for this seller's products
        query = """
        SELECT o.order_id, o.product_id, o.quantity, o.price_at_add, 
               o.order_status, o.ordered_at,
               p.product_id, p.product_name, p.description, p.product_price,
               p.category, p.image, p.quantity_status, p.delivery_status,
               u.username as buyer_name, u.contact_number as buyer_contact
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN users u ON o.user_id = u.id
        WHERE p.seller_id = %s
        ORDER BY o.ordered_at DESC
        """
        cursor.execute(query, (seller_id,))
        all_orders = cursor.fetchall()
        
        # Categorize orders by status
        pending_orders = [order for order in all_orders if order['order_status'] == 'pending']
        shipped_orders = [order for order in all_orders if order['order_status'] == 'shipped']
        delivered_orders = [order for order in all_orders if order['order_status'] == 'delivered']
        
        return render_template('html/seller_products.html',
                             pending_orders=pending_orders,
                             shipped_orders=shipped_orders,
                             delivered_orders=delivered_orders)
        
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@seller_prod.route('/api/orders')
def get_orders():
    seller_id = session.get('user_id')
    if not seller_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT o.order_id, o.product_id, o.quantity, o.price_at_add, 
               o.order_status, o.ordered_at,
               p.product_id, p.product_name, p.description, p.product_price,
               p.category, p.image, p.quantity_status, p.delivery_status,
               u.username as buyer_name, u.contact_number as buyer_contact
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN users u ON o.user_id = u.id
        WHERE p.seller_id = %s
        ORDER BY o.ordered_at DESC
        """
        cursor.execute(query, (seller_id,))
        orders = cursor.fetchall()
        
        return jsonify(orders)
        
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@seller_prod.route('/update_order_status', methods=['POST'])
def update_order_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('new_status')
    
    if not order_id or not new_status:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Verify the order belongs to this seller's products
        seller_id = session.get('user_id')
        verify_query = """
        SELECT 1 FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.order_id = %s AND p.seller_id = %s
        """
        cursor.execute(verify_query, (order_id, seller_id))
        if not cursor.fetchone():
            return jsonify({'error': 'Order not found or unauthorized'}), 404
        
        # Update the status
        update_query = "UPDATE orders SET order_status = %s WHERE order_id = %s"
        cursor.execute(update_query, (new_status, order_id))
        connection.commit()
        
        return jsonify({'success': True})
        
    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()