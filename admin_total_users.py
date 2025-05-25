from flask import Blueprint, jsonify
from database import get_connection
import mysql.connector
from datetime import datetime

admin_total_users = Blueprint('admin_total_users', __name__)

@admin_total_users.route('/total_users', methods=['GET'])
def get_total_users():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get total count of all users
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        # Get count of riders
        cursor.execute("SELECT COUNT(*) as total_riders FROM users WHERE role = 'rider'")
        total_riders = cursor.fetchone()['total_riders']

        # Get count of buyers
        cursor.execute("SELECT COUNT(*) as total_buyers FROM users WHERE role = 'buyer'")
        total_buyers = cursor.fetchone()['total_buyers']

        # Get count of sellers
        cursor.execute("SELECT COUNT(*) as total_sellers FROM users WHERE role = 'seller'")
        total_sellers = cursor.fetchone()['total_sellers']

        # Get count of admins
        cursor.execute("SELECT COUNT(*) as total_admins FROM users WHERE role = 'admin'")
        total_admins = cursor.fetchone()['total_admins']

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'total_users': total_users,
            'roles': {
                'riders': total_riders,
                'buyers': total_buyers,
                'sellers': total_sellers,
                'admins': total_admins
            }
        })

    except mysql.connector.Error as err:
        return jsonify({
            'success': False,
            'error': str(err)
        }), 500

@admin_total_users.route('/order_stats', methods=['GET'])
def get_order_stats():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Monthly delivered orders data
        cursor.execute("""
            SELECT 
                YEAR(ordered_at) as year,
                MONTH(ordered_at) as month,
                SUM(price_at_add) as total_sales,
                COUNT(*) as order_count
            FROM orders
            WHERE order_status = 'delivered'
            GROUP BY YEAR(ordered_at), MONTH(ordered_at)
            ORDER BY year, month
        """)
        monthly_data = cursor.fetchall()

        # Yearly delivered orders data
        cursor.execute("""
            SELECT 
                YEAR(ordered_at) as year,
                SUM(price_at_add) as total_sales,
                COUNT(*) as order_count
            FROM orders
            WHERE order_status = 'delivered'
            GROUP BY YEAR(ordered_at)
            ORDER BY year
        """)
        yearly_data = cursor.fetchall()

        cursor.close()
        connection.close()

        # Format monthly data with month names
        formatted_monthly = []
        for entry in monthly_data:
            month_name = datetime.strptime(str(entry['month']), "%m").strftime("%B")
            formatted_monthly.append({
                'year': entry['year'],
                'month': entry['month'],
                'month_name': month_name,
                'total_sales': float(entry['total_sales']),
                'order_count': entry['order_count']
            })

        # Format yearly data
        formatted_yearly = []
        for entry in yearly_data:
            formatted_yearly.append({
                'year': entry['year'],
                'total_sales': float(entry['total_sales']),
                'order_count': entry['order_count']
            })

        return jsonify({
            'success': True,
            'monthly': formatted_monthly,
            'yearly': formatted_yearly
        })

    except mysql.connector.Error as err:
        return jsonify({
            'success': False,
            'error': str(err)
        }), 500