import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='192.168.254.110',
            user='root',
            password='',
            database='ecommerce_db'
        )
        if connection.is_connected():
            print("Database connection successful!")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
