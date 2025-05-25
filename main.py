from flask import Flask, render_template, redirect, session, jsonify
from flask_cors import CORS

from login import login  # Login blueprint
from register import register  # Register blueprint
from seller import seller  # Seller blueprint with add-product route
from flashcard import flashcard
from buyer import buyer
from cart import cart
from buy_order import buy_order
from buyflashorder import buyflashorder
from buyer_account_settings import buyer_account_settings
from admin_account_settings import admin_account_settings
from rider_deliveries import rider_deliveries
from forgot_password import forgot_password
from admin_users_management import admin_users_management
from admin_total_users import admin_total_users
from seller_prod import seller_prod
from rider_leaderboards import rider_leaderboards
from flask_mail import Mail

from database import get_connection

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for session handling
CORS(app)  # Enable CORS globally

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'marwindalin01@gmail.com'
app.config['MAIL_PASSWORD'] = 'upnj vhui irmi penn'

mail = Mail(app)

# Register Blueprints
app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(seller)
app.register_blueprint(flashcard)
app.register_blueprint(buyer)
app.register_blueprint(cart)
app.register_blueprint(buy_order)
app.register_blueprint(buyflashorder)
app.register_blueprint(buyer_account_settings)
app.register_blueprint(rider_deliveries)
app.register_blueprint(forgot_password)
app.register_blueprint(admin_total_users)
app.register_blueprint(admin_account_settings)
app.register_blueprint(admin_users_management)
app.register_blueprint(seller_prod)
app.register_blueprint(rider_leaderboards)

# Redirect root to login
@app.route('/')
def home():
    return redirect('/login')

# Role-based dashboards
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('html/admin_dashboard.html')
    return redirect('/login')

@app.route('/buyer_dashboard')
def buyer_dashboard():
    if 'role' in session and session['role'] == 'buyer':
        return render_template('html/buyer_dashboard.html')
    return redirect('/login')

@app.route('/seller_dashboard')
def seller_dashboard():
    if 'role' in session and session['role'] == 'seller':
        return render_template('html/seller_dashboard.html')
    return redirect('/login')

@app.route('/rider_dashboard')
def rider_dashboard():
    if 'role' in session and session['role'] == 'rider':
        return render_template('html/rider_dashboard.html')
    return redirect('/login')

@app.route('/seller_update')
def seller_update():
    if 'role' in session and session['role'] == 'seller':
        return render_template('html/seller_update.html')
    return redirect('/login')

@app.route('/seller_account_settings')
def seller_account_settings():
    if 'role' in session and session['role'] == 'seller':
        return render_template('html/seller_account_settings.html')
    return redirect('/login')

@app.route('/seller_products')
def seller_products():
    if 'role' in session and session['role'] == 'seller':
        return render_template('html/seller_products.html')
    return redirect('/login')

@app.route('/buyer_account_settings')
def buyer_account_settings():
    if 'role' in session and session['role'] == 'buyer':
        return render_template('html/buyer_account_settings.html')
    return redirect('/login')

@app.route('/admin_account_settings')
def admin_account_settings():
    if 'role' in session and session['role'] == 'admin':
        return render_template('html/admin_account_settings.html')
    return redirect('/login')

@app.route('/admin_restricted')
def admin_restricted():
    if 'role' in session and session['role'] == 'admin':
        return render_template('html/admin_restricted.html')
    return redirect('/login')

@app.route('/admin_banned')
def admin_banned():
    if 'role' in session and session['role'] == 'admin':
        return render_template('html/admin_banned.html')
    return redirect('/login')

@app.route('/buyer_order')
def buyer_order():
    if 'role' in session and session['role'] == 'buyer':
        # Pass the user_id to the template
        return render_template('html/buyer_order.html', 
                            user_id=session.get('user_id'),
                            current_user=session.get('user_id'))
    return redirect('/login')

@app.route('/api/current-user')
def get_current_user():
    if 'user_id' in session:
        return jsonify({'user_id': session['user_id']})
    else:
        return jsonify({'error': 'Not authenticated'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
