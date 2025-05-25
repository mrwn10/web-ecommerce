from flask import Blueprint, request, jsonify
from database import get_connection
import mysql.connector

buy_order = Blueprint('buy_order', __name__)

@buy_order.route('/order/buy', methods=['POST'])
def buy_now():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    required_fields = ['user_id', 'product_id', 'quantity']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Check if the product exists
        cursor.execute(
            "SELECT product_id, product_price, quantity_status FROM products WHERE product_id = %s",
            (data['product_id'],)
        )
        product = cursor.fetchone()

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # 2. Check if enough quantity is available
        if data['quantity'] > product['quantity_status']:
            return jsonify({
                'error': 'Not enough stock available',
                'available': product['quantity_status']
            }), 400

        # 3. Calculate price_at_add (snapshot price when buying)
        price_at_add = product['product_price'] * data['quantity']

        # 4. Insert into orders
        cursor.execute(
            """INSERT INTO orders (user_id, product_id, quantity, price_at_add, order_status)
               VALUES (%s, %s, %s, %s, %s)""",
            (data['user_id'], data['product_id'], data['quantity'], price_at_add, 'pending')
        )

        # 5. Deduct quantity from products
        cursor.execute(
            """UPDATE products 
               SET quantity_status = quantity_status - %s 
               WHERE product_id = %s""",
            (data['quantity'], data['product_id'])
        )

        connection.commit()

        return jsonify({
            'message': 'Order placed successfully',
            'order_id': cursor.lastrowid,
            'product_id': data['product_id'],
            'quantity': data['quantity'],
            'price_at_add': price_at_add,
            'order_status': 'pending'
        }), 201

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@buy_order.route('/order/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.order_id, p.product_id, p.product_name, p.image,
                   o.quantity, o.price_at_add as price, 
                   o.order_status, o.ordered_at,
                   (o.quantity * o.price_at_add) as item_total
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.user_id = %s
            ORDER BY o.ordered_at DESC
        """, (user_id,))

        orders = cursor.fetchall()
        total = sum(order['item_total'] for order in orders) if orders else 0

        return jsonify({
            'orders': orders,
            'total_spent': total,
            'count': len(orders)
        })

    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
