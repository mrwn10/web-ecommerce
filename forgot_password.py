from flask import Blueprint, jsonify, request, render_template
from flask_mail import Mail, Message
from database import get_connection
import random
import string
import time
from datetime import datetime, timedelta
import re

forgot_password = Blueprint('forgot_password', __name__)

# Configure Flask-Mail
mail = Mail()

# Dictionary to store OTPs and their expiration times (in production, use a database)
otp_storage = {}
cooldowns = {}

# Constants
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 3

def generate_otp():
    """Generate a secure OTP"""
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@forgot_password.route('/request_otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    # Validate email format
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    # Check if email exists in database
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Email not found in our system'}), 404
        conn.close()
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Database error while verifying email'
        }), 500
    
    # Check cooldown
    current_time = time.time()
    if email in cooldowns and current_time < cooldowns[email]:
        remaining = int(cooldowns[email] - current_time)
        return jsonify({
            'success': False,
            'message': f'Please wait {remaining} seconds before requesting another OTP',
            'cooldown': remaining
        }), 429
    
    # Generate OTP
    otp = generate_otp()
    expiration_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Store OTP with attempt counter and set cooldown
    otp_storage[email] = {
        'otp': otp,
        'expires_at': expiration_time.timestamp(),
        'attempts': 0
    }
    cooldowns[email] = current_time + COOLDOWN_SECONDS
    
    # Send email (in production, use a background task)
    try:
        msg = Message(
            subject='Your Password Reset OTP',
            sender='noreply@yourapp.com',  # Use your domain
            recipients=[email],
            html=f"""
            <h3>Password Reset Request</h3>
            <p>Your OTP code is: <strong>{otp}</strong></p>
            <p>This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            """
        )
        mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'OTP sent to {email}',
            'expires_in': OTP_EXPIRY_MINUTES * 60
        })
    except Exception as e:
        # Clean up failed OTP attempt
        if email in otp_storage:
            del otp_storage[email]
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP. Please try again later.'
        }), 500

@forgot_password.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()
    
    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400
    
    # Check if OTP exists
    if email not in otp_storage:
        return jsonify({'success': False, 'message': 'OTP not found or expired'}), 404
    
    stored_otp = otp_storage[email]
    
    # Check attempts
    if stored_otp['attempts'] >= MAX_OTP_ATTEMPTS:
        del otp_storage[email]
        return jsonify({
            'success': False,
            'message': 'Maximum OTP attempts reached. Please request a new OTP.'
        }), 403
    
    # Check expiration
    if datetime.now().timestamp() > stored_otp['expires_at']:
        del otp_storage[email]
        return jsonify({'success': False, 'message': 'OTP expired'}), 400
    
    # Increment attempt counter
    otp_storage[email]['attempts'] += 1
    
    # Verify OTP
    if otp != stored_otp['otp']:
        return jsonify({
            'success': False,
            'message': 'Invalid OTP',
            'attempts_remaining': MAX_OTP_ATTEMPTS - otp_storage[email]['attempts']
        }), 400
    
    # OTP is valid - mark as verified but don't delete yet (needed for password reset)
    otp_storage[email]['verified'] = True
    
    return jsonify({
        'success': True,
        'message': 'OTP verified successfully',
        'reset_token': f"temp_{random.getrandbits(128):032x}"  # Simple token for demo
    })

@forgot_password.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    new_password = data.get('new_password')
    otp = data.get('otp')
    
    if not email or not new_password or not otp:
        return jsonify({'success': False, 'message': 'Email, OTP and new password are required'}), 400
    
    # Password strength validation
    if len(new_password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400
    
    # Verify OTP exists and is verified
    if email not in otp_storage or not otp_storage[email].get('verified'):
        return jsonify({
            'success': False,
            'message': 'OTP verification required first'
        }), 403
    
    # Final OTP check
    if otp != otp_storage[email]['otp']:
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
    
    # Update password in database
    try:
        # Replace this with your password hashing implementation
        # hashed_pw = your_password_hashing_function(new_password)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (new_password, email)  # Replace with hashed_pw when implementing hashing
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        conn.commit()
        conn.close()
        
        # Clean up OTP after successful password reset
        del otp_storage[email]
        if email in cooldowns:
            del cooldowns[email]
        
        return jsonify({
            'success': True,
            'message': 'Password updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to update password. Please try again.'
        }), 500

@forgot_password.route('/forgot_password', methods=['GET'])
def show_forgot_password_page():
    return render_template('html/forgot_password.html')