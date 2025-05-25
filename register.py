from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import get_connection
import re

register = Blueprint('register', __name__)

def validate_password(password):
    """
    Validate password meets complexity requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, "Password is valid."

def validate_contact_number(contact_number):
    """
    Validate contact number format:
    - Must start with '09'
    - Must be exactly 11 digits
    - Must contain only numbers
    """
    if not contact_number.startswith('09'):
        return False, "Contact number must start with '09'."
    
    if len(contact_number) != 11:
        return False, "Contact number must be exactly 11 digits."
    
    if not contact_number.isdigit():
        return False, "Contact number must contain only numbers."
    
    return True, "Contact number is valid."

def validate_email(email):
    """
    Validate email format using regex
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address."
    return True, "Email is valid."

def validate_username(username):
    """
    Validate username:
    - At least 4 characters
    - Only alphanumeric characters and underscores
    """
    if len(username) < 4:
        return False, "Username must be at least 4 characters long."
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores."
    
    return True, "Username is valid."

@register.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('html/register.html')
    
    # Handle POST request
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    role = data.get('role', '').strip()
    province = data.get('province', '').strip()
    municipal = data.get('municipal', '').strip()
    barangay = data.get('barangay', '').strip()
    contact_number = data.get('contact_number', '').strip()

    # Check if all fields are filled
    if not all([username, email, password, confirm_password, role, province, municipal, barangay, contact_number]):
        return jsonify({
            'status': 'error',
            'message': 'All fields are required.',
            'data': {
                'field': next(field for field in ['username', 'email', 'password', 'confirm_password', 
                                                'role', 'province', 'municipal', 'barangay', 'contact_number'] 
                            if not data.get(field, '').strip())
            }
        }), 400

    # Validate username
    is_valid, message = validate_username(username)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'message': message,
            'data': {'field': 'username'}
        }), 400

    # Validate email
    is_valid, message = validate_email(email)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'message': message,
            'data': {'field': 'email'}
        }), 400

    # Password confirmation check
    if password != confirm_password:
        return jsonify({
            'status': 'error',
            'message': 'Passwords do not match.',
            'data': {'field': 'confirm_password'}
        }), 400

    # Password complexity validation
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'message': message,
            'data': {'field': 'password'}
        }), 400

    # Contact number validation
    is_valid, message = validate_contact_number(contact_number)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'message': message,
            'data': {'field': 'contact_number'}
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check username uniqueness
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Username already exists. Choose a different one.',
                'data': {'field': 'username'}
            }), 400

        # Check email uniqueness
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Email already exists. Choose a different one.',
                'data': {'field': 'email'}
            }), 400

        # Check contact number uniqueness
        cursor.execute("SELECT * FROM users WHERE contact_number = %s", (contact_number,))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Contact number already exists. Choose a different one.',
                'data': {'field': 'contact_number'}
            }), 400

        # Insert into the database
        cursor.execute(""" 
            INSERT INTO users 
            (username, email, password, role, province, municipal, barangay, contact_number) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, email, password, role, province, municipal, barangay, contact_number))
        conn.commit()

        # Confirm insertion
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return jsonify({
                'status': 'success',
                'message': 'Registration successful! Please login.',
                'data': {
                    'username': username,
                    'email': email,
                    'role': role
                }
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error inserting user into the database. Please try again.'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500

    finally:
        if 'conn' in locals():
            conn.close()