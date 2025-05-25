from flask import Blueprint, jsonify, request
from database import get_connection
import base64, os
from flask_socketio import SocketIO, emit

flashcard = Blueprint('flashcard', __name__)
socketio = SocketIO()

# Function to convert image data to base64
def encode_image(image_blob):
    return base64.b64encode(image_blob).decode('utf-8')

def fetch_flashcards(user_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if user_id:
        cursor.execute(
            "SELECT product_id, product_name, image, quantity_status, product_price, description, category FROM products WHERE user_id = %s",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT product_id, product_name, image, quantity_status, product_price, description, category FROM products"
        )
    
    products = cursor.fetchall()
    
    flashcards = []
    for product in products:
        image_path = product['image']
        image_data = None
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = encode_image(f.read())
                
        flashcards.append({
            "product_id": product['product_id'],
            "image_name": product['product_name'],
            "image_url": image_data,
            "quantity_status": product['quantity_status'],
            "product_price": str(product['product_price']),
            "description": product.get('description', ''),
            "category": product.get('category', '')  # Add this line
        })
    
    cursor.close()
    conn.close()
    return flashcards

@flashcard.route('/get_flashcards', methods=['GET'])
def get_flashcards():
    user_id = request.args.get('user_id')  # Get user_id from query string
    flashcards = fetch_flashcards(user_id)
    return jsonify(flashcards)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Successfully connected'})

@socketio.on('request_flashcards')
def handle_request_flashcards(data):
    user_id = data.get('user_id')
    flashcards = fetch_flashcards(user_id)
    emit('update_flashcards', {'flashcards': flashcards})

def notify_flashcards_update(user_id=None):
    """Call this function whenever flashcards are updated in the database"""
    flashcards = fetch_flashcards(user_id)
    if user_id:
        socketio.emit('update_flashcards', {'flashcards': flashcards}, room=f'user_{user_id}')
    else:
        socketio.emit('update_flashcards', {'flashcards': flashcards})