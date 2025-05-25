from flask import Blueprint, jsonify, request
from database import get_connection
from datetime import datetime

rider_leaderboards = Blueprint('rider_leaderboards', __name__)

@rider_leaderboards.route('/api/leaderboards/riders', methods=['GET'])
def get_rider_leaderboards():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get sort parameter from query string (default to earnings)
        sort_by = request.args.get('sort_by', default='earnings', type=str)
        
        # Validate sort parameter
        if sort_by not in ['earnings', 'total_orders']:
            sort_by = 'earnings'
        
        # Determine sort direction
        sort_order = 'DESC'  # Always sort highest to lowest for leaderboards
        
        # Query to get rider leaderboards
        query = f"""
        SELECT 
            r.rider_id,
            u.username,
            r.earnings,
            r.total_orders,
            u.province,
            u.municipal,
            u.barangay
        FROM riders r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.{sort_by} {sort_order}
        """
        
        cursor.execute(query)
        riders = cursor.fetchall()
        
        # Format the earnings as currency
        for rider in riders:
            rider['earnings'] = float(rider['earnings'])  # Ensure it's serializable
        
        return jsonify({
            'success': True,
            'sort_by': sort_by,
            'data': riders
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if connection:
            connection.close()