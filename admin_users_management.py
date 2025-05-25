from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database import get_connection
from flask_mail import Message, Mail
import re
from datetime import datetime, timedelta
import time

admin_users_management = Blueprint('admin_users_management', __name__)

# Initialize Flask-Mail
mail = Mail()

@admin_users_management.route('/admin_users_management')
def users_management():
    if 'role' in session and session['role'] == 'admin':
        return render_template('html/admin_users_management.html')
    return redirect('/login')

@admin_users_management.route('/admin_banned')
def ban_user_page():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    user_id = request.args.get('id')
    username = request.args.get('username')
    email = request.args.get('email')
    
    if not all([user_id, username, email]):
        return redirect('/admin_users_management')
    
    return render_template('html/admin_banned.html', 
                         user_id=user_id, 
                         username=username, 
                         email=email)

@admin_users_management.route('/admin_restricted')
def restrict_user_page():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')
    
    user_id = request.args.get('id')
    username = request.args.get('username')
    email = request.args.get('email')
    
    if not all([user_id, username, email]):
        return redirect('/admin_users_management')
    
    return render_template('html/admin_restricted.html', 
                         user_id=user_id, 
                         username=username, 
                         email=email)

@admin_users_management.route('/api/admin/activate_user', methods=['POST'])
def activate_user():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    email = data.get('email')
    username = data.get('username')
    
    if not all([user_id, email, username]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Update user account status to active and clear restriction
        cursor.execute(
            "UPDATE users SET account_status = 'active', restricted_at = NULL WHERE id = %s",
            (user_id,)
        )
        connection.commit()
        
        # Send activation notification email
        send_activation_notification(email, username)
        
        return jsonify({'message': 'User activated successfully'})
    
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

@admin_users_management.route('/api/admin/ban_user', methods=['POST'])
def ban_user():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    reason = data.get('reason')
    email = data.get('email')
    username = data.get('username')
    
    if not all([user_id, reason, email, username]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Update user account status to banned
        cursor.execute(
            "UPDATE users SET account_status = 'banned', restricted_at = NULL WHERE id = %s",
            (user_id,)
        )
        connection.commit()
        
        # Send email notification
        send_ban_notification(email, username, reason)
        
        return jsonify({'message': 'User banned successfully'})
    
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

@admin_users_management.route('/api/admin/restrict_user', methods=['POST'])
def restrict_user():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    reason = data.get('reason')
    email = data.get('email')
    username = data.get('username')
    
    if not all([user_id, reason, email, username]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Update user account status to restricted and set restriction time
        cursor.execute(
            "UPDATE users SET account_status = 'restricted', restricted_at = NOW() WHERE id = %s",
            (user_id,)
        )
        connection.commit()
        
        # Send email notification
        send_restriction_notification(email, username, reason)
        
        return jsonify({'message': 'User restricted successfully for 7 days'})
    
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

def send_activation_notification(email, username):
    try:
        subject = "Your Account Has Been Reactivated"
        html_content = f"""
        <html>
            <body>
                <h3>Account Reactivation Notification</h3>
                <p>Dear {username},</p>
                <p>We're pleased to inform you that your account has been reactivated.</p>
                <p>You can now access all features of our platform.</p>
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
                <br>
                <p>Sincerely,</p>
                <p>The Administration Team</p>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            sender=('Kids & Baby', 'noreply@yourapp.com'),
            recipients=[email],
            html=html_content
        )
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send activation notification email: {str(e)}")

def send_ban_notification(email, username, reason):
    try:
        subject = "Your Account Has Been Banned"
        html_content = f"""
        <html>
            <body>
                <h3>Account Ban Notification</h3>
                <p>Dear {username},</p>
                <p>We regret to inform you that your account has been banned from our platform.</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p>If you believe this action was taken in error, please contact our support team.</p>
                <br>
                <p>Sincerely,</p>
                <p>The Administration Team</p>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            sender=('Kids & Baby', 'noreply@yourapp.com'),
            recipients=[email],
            html=html_content
        )
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send ban notification email: {str(e)}")

def send_restriction_notification(email, username, reason):
    try:
        subject = "Your Account Has Been Restricted"
        html_content = f"""
        <html>
            <body>
                <h3>Account Restriction Notification</h3>
                <p>Dear {username},</p>
                <p>Your account has been temporarily restricted for 7 days.</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p>During this period, you won't be able to perform certain actions on our platform.</p>
                <p>If you believe this action was taken in error, please contact our support team.</p>
                <br>
                <p>Sincerely,</p>
                <p>The Administration Team</p>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            sender=('Kids & Baby', 'noreply@yourapp.com'),
            recipients=[email],
            html=html_content
        )
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send restriction notification email: {str(e)}")

@admin_users_management.route('/api/admin/get_users')
def get_users():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get all users
        cursor.execute("SELECT * FROM users ORDER BY role, username")
        users = cursor.fetchall()
        
        # Organize users by role
        categorized_users = {
            'riders': [],
            'sellers': [],
            'buyers': []
        }
        
        for user in users:
            # Calculate restriction time left if account is restricted
            restriction_time_left = None
            if user['account_status'] == 'restricted' and user['restricted_at']:
                restriction_end = user['restricted_at'] + timedelta(days=user['restriction_days'])
                time_left = restriction_end - datetime.now()
                
                if time_left.total_seconds() > 0:
                    days_left = time_left.days
                    hours_left = time_left.seconds // 3600
                    minutes_left = (time_left.seconds % 3600) // 60
                    restriction_time_left = f"{days_left}d {hours_left}h {minutes_left}m"
                else:
                    # Restriction period has ended
                    cursor.execute(
                        "UPDATE users SET account_status = 'active', restricted_at = NULL WHERE id = %s",
                        (user['id'],)
                    )
                    connection.commit()
                    user['account_status'] = 'active'
                    user['restricted_at'] = None

            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'account_status': user['account_status'],
                'restricted_at': user['restricted_at'].isoformat() if user['restricted_at'] else None,
                'restriction_days': user['restriction_days'],
                'restriction_time_left': restriction_time_left,
                'province': user['province'],
                'municipal': user['municipal'],
                'barangay': user['barangay'],
                'contact_number': user['contact_number']
            }
            
            if user['role'] == 'rider':
                # Get rider-specific data
                cursor.execute("SELECT * FROM riders WHERE user_id = %s", (user['id'],))
                rider_data = cursor.fetchone()
                if rider_data:
                    user_data.update({
                        'earnings': float(rider_data['earnings']),
                        'total_orders': rider_data['total_orders']
                    })
                categorized_users['riders'].append(user_data)
            elif user['role'] == 'seller':
                # Get seller-specific data
                cursor.execute("SELECT COUNT(*) as product_count FROM products WHERE seller_id = %s", (user['id'],))
                seller_data = cursor.fetchone()
                user_data['product_count'] = seller_data['product_count'] if seller_data else 0
                
                # Get total sales
                cursor.execute("""
                    SELECT SUM(price_at_add * quantity) as total_sales 
                    FROM orders 
                    WHERE product_id IN (SELECT product_id FROM products WHERE seller_id = %s)
                    AND order_status = 'delivered'
                """, (user['id'],))
                sales_data = cursor.fetchone()
                user_data['total_sales'] = float(sales_data['total_sales']) if sales_data and sales_data['total_sales'] else 0
                
                categorized_users['sellers'].append(user_data)
            elif user['role'] == 'buyer':
                # Get buyer-specific data
                cursor.execute("SELECT COUNT(*) as order_count FROM orders WHERE user_id = %s", (user['id'],))
                buyer_data = cursor.fetchone()
                user_data['order_count'] = buyer_data['order_count'] if buyer_data else 0
                
                # Get total spent
                cursor.execute("""
                    SELECT SUM(price_at_add * quantity) as total_spent 
                    FROM orders 
                    WHERE user_id = %s
                    AND order_status = 'delivered'
                """, (user['id'],))
                spent_data = cursor.fetchone()
                user_data['total_spent'] = float(spent_data['total_spent']) if spent_data and spent_data['total_spent'] else 0
                
                categorized_users['buyers'].append(user_data)
        
        return jsonify(categorized_users)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()