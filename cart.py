from flask import Blueprint, request, jsonify, render_template
from database import get_connection
import mysql.connector

cart = Blueprint('cart', __name__)

# Existing add to cart route
@cart.route('/cart/add', methods=['POST'])
def add_to_cart():
    # Ensure request is in JSON format
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    required_fields = ['user_id', 'product_id', 'quantity']
    
    # Check if all required fields are provided
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Check if the product exists by product_id
        cursor.execute(
            "SELECT product_id, product_price, quantity_status FROM products WHERE product_id = %s",
            (data['product_id'],)
        )
        product = cursor.fetchone()

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # 2. Check available quantity
        if data['quantity'] > product['quantity_status']:
            return jsonify({
                'error': 'Not enough stock available',
                'available': product['quantity_status']
            }), 400

        # 3. Calculate the price_at_add based on the product's price and quantity
        price_at_add = product['product_price'] * data['quantity']

        # 4. Add to cart (or update if already in cart)
        cursor.execute(
            """INSERT INTO cart (user_id, product_id, quantity, price_at_add) 
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE quantity = quantity + %s, price_at_add = %s""",
            (data['user_id'], data['product_id'], data['quantity'], price_at_add, data['quantity'], price_at_add)
        )
        connection.commit()

        # If successful, return success response
        return jsonify({
            'message': 'Product added to cart successfully',
            'cart_id': cursor.lastrowid,
            'product_id': data['product_id'],
            'quantity': data['quantity'],
            'price_at_add': price_at_add
        }), 201

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    finally:
        # Ensure that the database connection is always closed
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Existing get cart route
@cart.route('/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(""" 
            SELECT c.cart_id, p.product_id, p.product_name, p.image, 
                   c.quantity, c.price_at_add as price, 
                   (c.quantity * c.price_at_add) as item_total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user_id,))

        items = cursor.fetchall()
        total = sum(item['item_total'] for item in items) if items else 0

        return jsonify({
            'items': items,
            'total': total,
            'count': len(items)
        })

    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    finally:
        # Ensure that the database connection is always closed
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# New route to serve the buyer's cart HTML page
@cart.route('/buyer_cart', methods=['GET'])
def buyer_cart():
    # Optionally pass the user_id as query parameter if you need to display cart contents
    user_id = request.args.get('user_id')
    if user_id:
        # Fetch cart items from the database and pass to template if needed
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(""" 
            SELECT c.cart_id, p.product_id, p.product_name, p.image, 
                   c.quantity, c.price_at_add as price, 
                   (c.quantity * c.price_at_add) as item_total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()
        total = sum(item['item_total'] for item in items) if items else 0
        cursor.close()
        connection.close()
        return render_template('html/buyer_cart.html', items=items, total=total)
    else:
        # If no user_id, simply render the page without cart details
        return render_template('html/buyer_cart.html')
