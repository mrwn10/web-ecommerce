from flask import Blueprint, jsonify, request
from database import get_connection
from datetime import datetime

rider_deliveries = Blueprint('rider_deliveries', __name__)

@rider_deliveries.route('/api/user-orders', methods=['GET'])
def get_pending_orders():
    """Endpoint to fetch pending orders (existing functionality)"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.username,
                u.province,
                u.municipal,
                u.barangay,
                u.contact_number,
                o.order_id,
                o.quantity,
                o.price_at_add,
                o.order_status,
                o.ordered_at
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE o.order_status = 'pending'
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        user_orders = []
        for row in results:
            user_orders.append({
                'order_id': row['order_id'],
                'username': row['username'],
                'province': row['province'],
                'municipal': row['municipal'],
                'barangay': row['barangay'],
                'contact_number': row['contact_number'],
                'quantity': row['quantity'],
                'price_at_add': float(row['price_at_add']) if row['price_at_add'] is not None else None,
                'order_status': row['order_status'],
                'ordered_at': row['ordered_at'].strftime('%Y-%m-%d %H:%M:%S') if row['ordered_at'] else None
            })
        
        return jsonify({
            'success': True,
            'data': user_orders,
            'count': len(user_orders)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@rider_deliveries.route('/api/shipped-orders', methods=['GET'])
def get_shipped_orders():
    """Endpoint to fetch shipped orders"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.username,
                u.province,
                u.municipal,
                u.barangay,
                u.contact_number,
                o.order_id,
                o.quantity,
                o.price_at_add,
                o.order_status,
                o.ordered_at
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE o.order_status = 'shipped'
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        user_orders = []
        for row in results:
            user_orders.append({
                'order_id': row['order_id'],
                'username': row['username'],
                'province': row['province'],
                'municipal': row['municipal'],
                'barangay': row['barangay'],
                'contact_number': row['contact_number'],
                'quantity': row['quantity'],
                'price_at_add': float(row['price_at_add']) if row['price_at_add'] is not None else None,
                'order_status': row['order_status'],
                'ordered_at': row['ordered_at'].strftime('%Y-%m-%d %H:%M:%S') if row['ordered_at'] else None
            })
        
        return jsonify({
            'success': True,
            'data': user_orders,
            'count': len(user_orders)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@rider_deliveries.route('/api/accept-delivery', methods=['POST'])
def accept_delivery():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        rider_id = data.get('rider_id')
        
        if not order_id or not rider_id:
            return jsonify({'success': False, 'error': 'Missing order_id or rider_id'}), 400
        
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Start transaction
        connection.start_transaction()
        
        # 1. First check if rider exists (but don't create if not, wait until delivery)
        cursor.execute("SELECT rider_id FROM riders WHERE user_id = %s", (rider_id,))
        rider = cursor.fetchone()
        
        # 2. Update order status to 'shipped' (no rider stats changes here)
        cursor.execute(
            "UPDATE orders SET order_status = 'shipped' WHERE order_id = %s AND order_status = 'pending'",
            (order_id,)
        )
        
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({
                'success': False,
                'error': 'Order not found or already taken'
            }), 400
        
        # Commit transaction
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Delivery accepted successfully',
            'data': {
                'order_id': order_id,
                'new_status': 'shipped',
                'earnings_added': 0,      # No earnings added at acceptance
                'total_orders_incremented': 0  # No orders counted yet
            }
        })

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@rider_deliveries.route('/api/mark-delivered', methods=['POST'])
def mark_delivered():
    """Endpoint to mark shipped orders as delivered"""
    connection = None
    cursor = None
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        rider_id = data.get('rider_id')  # Added rider_id parameter
        
        if not order_id or not rider_id:
            return jsonify({'success': False, 'error': 'Missing order_id or rider_id'}), 400
        
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Start transaction
        connection.start_transaction()
        
        # 1. First check if rider exists
        cursor.execute("SELECT rider_id FROM riders WHERE user_id = %s", (rider_id,))
        rider = cursor.fetchone()
        
        if not rider:
            # If rider doesn't exist, create a new record with initial stats
            cursor.execute(
                "INSERT INTO riders (user_id, earnings, total_orders) VALUES (%s, 50, 1)",
                (rider_id,)
            )
        else:
            # 2. Update rider's earnings and total_orders
            cursor.execute(
                "UPDATE riders SET earnings = earnings + 50, total_orders = total_orders + 1 WHERE user_id = %s",
                (rider_id,)
            )
        
        # 3. Update order status to 'delivered'
        cursor.execute(
            "UPDATE orders SET order_status = 'delivered' WHERE order_id = %s AND order_status = 'shipped'",
            (order_id,)
        )
        
        if cursor.rowcount == 0:
            connection.rollback()
            # Get current status for better error message
            cursor.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
            current_status = cursor.fetchone()
            error_msg = 'Order not found'
            if current_status:
                error_msg = f"Order is in '{current_status['order_status']}' status (must be 'shipped')"
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Commit transaction
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order marked as delivered successfully',
            'data': {
                'order_id': order_id,
                'new_status': 'delivered',
                'earnings_added': 50,          # Earnings added upon delivery
                'total_orders_incremented': 1    # Order counted upon delivery
            }
        })

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@rider_deliveries.route('/api/rider-stats/<int:user_id>', methods=['GET'])
def get_rider_stats(user_id):
    """Endpoint to fetch rider statistics (earnings and total orders)"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get rider stats from riders table
        cursor.execute("""
            SELECT r.earnings, r.total_orders, u.username 
            FROM riders r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = %s
        """, (user_id,))
        rider_stats = cursor.fetchone()
        
        if not rider_stats:
            # If rider doesn't exist in riders table yet, return default values
            cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
                
            return jsonify({
                'success': True,
                'data': {
                    'username': user['username'],
                    'earnings': 0.00,
                    'total_orders': 0,
                    'is_new_rider': True
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'username': rider_stats['username'],
                'earnings': float(rider_stats['earnings']),
                'total_orders': rider_stats['total_orders'],
                'is_new_rider': False
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()