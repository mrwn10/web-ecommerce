from flask import Blueprint, request, session, jsonify, render_template, redirect, flash
from database import get_connection
from datetime import datetime, timedelta

login = Blueprint('login', __name__)

@login.route('/login', methods=['GET'])
def login_form():
    return render_template('html/login.html')

@login.route('/login', methods=['POST'])
def login_page():
    # Support both form and JSON input
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        return handle_error("User not found", request.is_json)
    
    # Check if account is temporarily locked due to too many attempts
    if user.get('account_locked_until') and user['account_locked_until'] > datetime.now():
        time_left = user['account_locked_until'] - datetime.now()
        minutes = int(time_left.total_seconds() // 60)
        seconds = int(time_left.total_seconds() % 60)
        message = f"Too many failed attempts. Please try again in {minutes} minutes and {seconds} seconds."
        cursor.close()
        conn.close()
        return handle_error(message, request.is_json)
    
    # Check account status
    if user['account_status'] == 'restricted':
        if user['restricted_at']:
            restriction_end = user['restricted_at'] + timedelta(days=user['restriction_days'])
            time_left = restriction_end - datetime.now()
            
            if time_left.total_seconds() > 0:
                days_left = time_left.days
                hours_left = time_left.seconds // 3600
                minutes_left = (time_left.seconds % 3600) // 60
                
                if days_left > 0:
                    message = f"Your account is restricted for {days_left} days and {hours_left} hours"
                else:
                    message = f"Your account is restricted for {hours_left} hours and {minutes_left} minutes"
                
                cursor.close()
                conn.close()
                return handle_error(message, request.is_json)
            else:
                # Restriction period has ended, update account status
                cursor.execute(
                    "UPDATE users SET account_status = 'active', restricted_at = NULL WHERE id = %s",
                    (user['id'],)
                )
                conn.commit()
    
    elif user['account_status'] == 'banned':
        cursor.close()
        conn.close()
        return handle_error("Your account has been permanently banned. Contact support for more information.", request.is_json)
    elif user['account_status'] != 'active':
        cursor.close()
        conn.close()
        return handle_error("Your account is not active. Please contact support.", request.is_json)

    # Verify password
    if user['password'] != password:
        # Increment failed attempts
        new_attempts = user.get('failed_attempts', 0) + 1
        if new_attempts >= 5:
            lock_until = datetime.now() + timedelta(minutes=5)
            cursor.execute(
                "UPDATE users SET failed_attempts = %s, last_failed_attempt = %s, account_locked_until = %s WHERE id = %s",
                (new_attempts, datetime.now(), lock_until, user['id'])
            )
            message = "Too many failed attempts. Account locked for 5 minutes."
        else:
            cursor.execute(
                "UPDATE users SET failed_attempts = %s, last_failed_attempt = %s WHERE id = %s",
                (new_attempts, datetime.now(), user['id'])
            )
            remaining_attempts = 5 - new_attempts
            message = f"Invalid credentials. You have {remaining_attempts} attempts remaining."
        
        conn.commit()
        cursor.close()
        conn.close()
        return handle_error(message, request.is_json)

    # Login successful - reset failed attempts
    cursor.execute(
        "UPDATE users SET failed_attempts = 0, last_failed_attempt = NULL, account_locked_until = NULL WHERE id = %s",
        (user['id'],)
    )
    conn.commit()
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    dashboard_url = f"/{user['role']}_dashboard"

    # Response based on request type
    if request.is_json:
        response = jsonify({
            'status': 'success',
            'role': user['role'],
            'username': user['username'],
            'userId': str(user['id']),
            'redirect_url': dashboard_url
        }), 200
    else:
        response = redirect(dashboard_url)
    
    cursor.close()
    conn.close()
    return response

def handle_error(message, is_json):
    """Helper function to handle error responses consistently"""
    if is_json:
        return jsonify({
            'status': 'error',
            'message': message,
        }), 401
    else:
        flash(message, 'error')
        return render_template('html/login.html', error=message)