from flask import Blueprint, request, jsonify, session
from database import get_connection
import re

admin_account_settings = Blueprint('admin_account_settings', __name__)

@admin_account_settings.route('/admin/account-settings', methods=['GET'])
def account_settings():
    # Get user_id from query params for Flutter, fallback to session for web
    user_id = request.args.get('user_id') or session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                username, 
                email, 
                province, 
                municipal, 
                barangay, 
                contact_number 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        return jsonify({'status': 'success', 'data': user})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_account_settings.route('/admin/account-settings/update', methods=['POST'])
def update_account_settings():
    try:
        # Get data from JSON for Flutter
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

        # Get all fields with defaults
        username = data.get('username')
        email = data.get('email')
        province = data.get('province', '')
        municipal = data.get('municipal', '')
        barangay = data.get('barangay', '')
        contact_number = data.get('contact_number', '')

        # Validation
        if not username or not email:
            return jsonify({'status': 'error', 'message': 'Username and email are required'}), 400

        if contact_number and not re.match(r'^[0-9]{10,15}$', contact_number):
            return jsonify({'status': 'error', 'message': 'Invalid contact number format'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Check for existing username/email
            cursor.execute("""
                SELECT id FROM users 
                WHERE (username = %s OR email = %s) AND id != %s
            """, (username, email, user_id))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Username or email already taken'}), 400

            # Update user
            cursor.execute("""
                UPDATE users SET 
                    username = %s, 
                    email = %s,
                    province = %s,
                    municipal = %s,
                    barangay = %s,
                    contact_number = %s
                WHERE id = %s
            """, (username, email, province, municipal, barangay, contact_number, user_id))
            conn.commit()

            # Return updated user data
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            
            return jsonify({
                'status': 'success',
                'message': 'Account updated successfully',
                'data': updated_user
            })
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500