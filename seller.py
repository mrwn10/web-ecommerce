from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
import os
from database import get_connection

# Initialize the Blueprint for seller routes
seller = Blueprint('seller', __name__)

# Route for adding a new product
@seller.route('/add-product', methods=['GET', 'POST'])
def add_product():
    # Check if the user is logged in and has the 'seller' role
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403

    if request.method == 'POST':
        # Retrieve form data
        product_name = request.form['product_name']
        description = request.form['description']
        product_price = request.form['product_price']
        quantity_status = request.form['quantity_status']
        category = request.form['category']
        image = request.files['image']

        # Handle image upload
        image_data = None
        if image:
            # Save the image to a folder on the server and get the file path
            image_folder = os.path.join('static', 'uploads')
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_filename = os.path.join(image_folder, image.filename)
            image.save(image_filename)
            image_data = image_filename  # Store the file path in the database

        # Insert the product into the database
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO products 
            (product_name, description, product_price, quantity_status, category, image, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            product_name, description, product_price, quantity_status,
            category, image_data, session['user_id']
        ))
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect back to the seller dashboard after success
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller.seller_dashboard'))

    # Render the product adding form if the request is GET
    return render_template('html/seller_dashboard.html')

# Route for seller dashboard
@seller.route('/seller-dashboard')
def seller_dashboard():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('auth.login'))
    return render_template('html/seller_dashboard.html')

@seller.route('/get-products')
def get_products():
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, product_name, description, product_price, 
               quantity_status, category, image
        FROM products 
        WHERE seller_id = %s
    """, (session['user_id'],))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert Windows paths to forward slashes for web compatibility
    for product in products:
        if product['image']:
            product['image'] = product['image'].replace('\\', '/')
    return jsonify(products)

# New route for update page
@seller.route('/seller-update')
def seller_update():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('auth.login'))
    
    product_id = request.args.get('product_id')
    if not product_id:
        flash('No product specified', 'error')
        return redirect(url_for('seller.seller_dashboard'))
    
    return render_template('html/seller_update.html', product_id=product_id)

@seller.route('/get-product-details')
def get_product_details():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({'message': 'Product ID required'}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, product_name, description, product_price, 
               quantity_status, category, image 
        FROM products 
        WHERE product_id = %s AND seller_id = %s
    """, (product_id, session['user_id']))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    # Convert backslashes to forward slashes for web compatibility
    if product['image']:
        product['image'] = product['image'].replace('\\', '/')
    
    return jsonify(product)

# New route to handle product updates
@seller.route('/update-product', methods=['POST'])
def update_product():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    try:
        # Get form data
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        description = request.form['description']
        product_price = request.form['product_price']
        quantity_status = request.form['quantity_status']
        category = request.form['category']
        
        # Handle image upload if present
        image_data = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save the image to a folder on the server
                image_folder = os.path.join('static', 'uploads')
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                image_filename = os.path.join(image_folder, image.filename)
                image.save(image_filename)
                image_data = image_filename
        
        # Update product in database
        conn = get_connection()
        cursor = conn.cursor()
        
        if image_data:
            sql = """
                UPDATE products 
                SET product_name = %s, description = %s, product_price = %s, 
                    quantity_status = %s, category = %s, image = %s
                WHERE product_id = %s AND seller_id = %s
            """
            cursor.execute(sql, (
                product_name, description, product_price, quantity_status,
                category, image_data, product_id, session['user_id']
            ))
        else:
            sql = """
                UPDATE products 
                SET product_name = %s, description = %s, product_price = %s, 
                    quantity_status = %s, category = %s
                WHERE product_id = %s AND seller_id = %s
            """
            cursor.execute(sql, (
                product_name, description, product_price, quantity_status,
                category, product_id, session['user_id']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
import os
from database import get_connection

# Initialize the Blueprint for seller routes
seller = Blueprint('seller', __name__)

# Route for adding a new product
@seller.route('/add-product', methods=['GET', 'POST'])
def add_product():
    # Check if the user is logged in and has the 'seller' role
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403

    if request.method == 'POST':
        # Retrieve form data
        product_name = request.form['product_name']
        description = request.form['description']
        product_price = request.form['product_price']
        quantity_status = request.form['quantity_status']
        category = request.form['category']
        image = request.files['image']

        # Handle image upload
        image_data = None
        if image:
            # Save the image to a folder on the server and get the file path
            image_folder = os.path.join('static', 'uploads')
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_filename = os.path.join(image_folder, image.filename)
            image.save(image_filename)
            image_data = image_filename  # Store the file path in the database

        # Insert the product into the database
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO products 
            (product_name, description, product_price, quantity_status, category, image, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            product_name, description, product_price, quantity_status,
            category, image_data, session['user_id']
        ))
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect back to the seller dashboard after success
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller.seller_dashboard'))

    # Render the product adding form if the request is GET
    return render_template('html/seller_dashboard.html')

# Route for seller dashboard
@seller.route('/seller-dashboard')
def seller_dashboard():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('auth.login'))
    return render_template('html/seller_dashboard.html')

@seller.route('/get-products')
def get_products():
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, product_name, description, product_price, 
               quantity_status, category, image
        FROM products 
        WHERE seller_id = %s
    """, (session['user_id'],))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert Windows paths to forward slashes for web compatibility
    for product in products:
        if product['image']:
            product['image'] = product['image'].replace('\\', '/')
    return jsonify(products)

# New route for update page
@seller.route('/seller-update')
def seller_update():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('auth.login'))
    
    product_id = request.args.get('product_id')
    if not product_id:
        flash('No product specified', 'error')
        return redirect(url_for('seller.seller_dashboard'))
    
    return render_template('html/seller_update.html', product_id=product_id)

@seller.route('/get-product-details')
def get_product_details():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({'message': 'Product ID required'}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, product_name, description, product_price, 
               quantity_status, category, image 
        FROM products 
        WHERE product_id = %s AND seller_id = %s
    """, (product_id, session['user_id']))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    # Convert backslashes to forward slashes for web compatibility
    if product['image']:
        product['image'] = product['image'].replace('\\', '/')
    
    return jsonify(product)

# New route to handle product updates
@seller.route('/update-product', methods=['POST'])
def update_product():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    try:
        # Get form data
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        description = request.form['description']
        product_price = request.form['product_price']
        quantity_status = request.form['quantity_status']
        category = request.form['category']
        
        # Handle image upload if present
        image_data = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save the image to a folder on the server
                image_folder = os.path.join('static', 'uploads')
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                image_filename = os.path.join(image_folder, image.filename)
                image.save(image_filename)
                image_data = image_filename
        
        # Update product in database
        conn = get_connection()
        cursor = conn.cursor()
        
        if image_data:
            sql = """
                UPDATE products 
                SET product_name = %s, description = %s, product_price = %s, 
                    quantity_status = %s, category = %s, image = %s
                WHERE product_id = %s AND seller_id = %s
            """
            cursor.execute(sql, (
                product_name, description, product_price, quantity_status,
                category, image_data, product_id, session['user_id']
            ))
        else:
            sql = """
                UPDATE products 
                SET product_name = %s, description = %s, product_price = %s, 
                    quantity_status = %s, category = %s
                WHERE product_id = %s AND seller_id = %s
            """
            cursor.execute(sql, (
                product_name, description, product_price, quantity_status,
                category, product_id, session['user_id']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@seller.route('/delete-product', methods=['POST'])
def delete_product():
    # Check if user is logged in as seller
    if 'user_id' not in session or session.get('role') != 'seller':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    try:
        product_id = request.form.get('product_id')
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First get the product details (including image path)
        cursor.execute("""
            SELECT image FROM products 
            WHERE product_id = %s AND seller_id = %s
        """, (product_id, session['user_id']))
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        # Delete the product from database
        cursor.execute("""
            DELETE FROM products 
            WHERE product_id = %s AND seller_id = %s
        """, (product_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Delete the associated image file if it exists
        if product[0]:  # if there's an image path
            try:
                image_path = product[0]
                # Convert to consistent path format
                image_path = os.path.normpath(image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")
                # Continue even if file deletion fails
        
        flash('Product deleted successfully!', 'success')
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    
    except Exception as e:
        # Ensure database connection is closed if an error occurs
        if 'conn' in locals():
            conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500