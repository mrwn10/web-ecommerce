from flask import Blueprint, request, session, jsonify, render_template
from database import get_connection

buyer = Blueprint('buyer', __name__, url_prefix='/buyer')

@buyer.route('/dashboard')
def buyer_dashboard():
    return render_template('html/buyer_dashboard.html')

@buyer.route('/cart')
def buyer_cart():
    product_id = request.args.get('product_id')
    return render_template('html/buyer_cart.html', product_id=product_id)

@buyer.route('/api/products')
def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.product_id, 
            p.product_name, 
            p.description, 
            p.product_price, 
            p.category, 
            p.image, 
            p.quantity_status, 
            p.delivery_status, 
            p.seller_id, 
            u.username AS seller_name 
        FROM products p
        JOIN users u ON p.seller_id = u.id
    """)
    rows = cursor.fetchall()
    conn.close()

    products = [
        {
            "product_id": row[0],
            "product_name": row[1],
            "description": row[2],
            "product_price": row[3],
            "category": row[4],
            "image": row[5],
            "quantity_status": row[6],
            "delivery_status": row[7],
            "seller_id": row[8],
            "seller_name": row[9]
        }
        for row in rows
    ]
    
    return jsonify(products)

@buyer.route('/api/products/<int:product_id>')
def get_single_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.product_id, 
            p.product_name, 
            p.description, 
            p.product_price, 
            p.category, 
            p.image, 
            p.quantity_status, 
            p.delivery_status, 
            p.seller_id, 
            u.username AS seller_name 
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE p.product_id = %s
    """, (product_id,))
    
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Product not found"}), 404

    product = {
        "product_id": row[0],
        "product_name": row[1],
        "description": row[2],
        "product_price": row[3],
        "category": row[4],
        "image": row[5],
        "quantity_status": row[6],
        "delivery_status": row[7],
        "seller_id": row[8],
        "seller_name": row[9]
    }
    
    return jsonify(product)