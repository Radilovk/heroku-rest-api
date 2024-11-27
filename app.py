from flask import Flask, request, jsonify
import psycopg2
import os
import json

# Flask application initialization
app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port="5432"
        )
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")

# Home route for checking application status
@app.route('/')
def home():
    return "REST API for managing client responses and test table is running!", 200

# Route to add a new response
@app.route('/add-response', methods=['POST'])
def add_response():
    data = request.json
    if not data or 'client_name' not in data or 'response' not in data:
        return jsonify({"error": "Invalid input"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO client_responses (client_name, response) VALUES (%s, %s)",
            (data['client_name'], json.dumps(data['response']))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Response added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add response: {str(e)}"}), 500

# Route to get all responses
@app.route('/get-responses', methods=['GET'])
def get_responses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client_responses")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Обработка на резултатите
        results = [
            {
                "id": row[0],
                "client_name": row[1],
                "response": row[2],
                "created_at": row[3].isoformat()
            } for row in rows
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch responses: {str(e)}"}), 500

# Administrative route to execute SQL commands
@app.route('/admin/create-table', methods=['POST'])
def create_table():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Table created successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to execute query: {str(e)}"}), 500

# Route to view all data from test_table
@app.route('/admin/view-test-table', methods=['GET'])
def view_test_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Форматиране на резултатите
        results = [
            {"id": row[0], "name": row[1], "email": row[2], "created_at": row[3].isoformat()}
            for row in rows
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch table: {str(e)}"}), 500

# Main application entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Heroku's PORT or default to 5000
    app.run(host="0.0.0.0", port=port)
