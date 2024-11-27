from flask import Flask, request, jsonify
import psycopg2
import os
import json

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )

# Home route
@app.route('/')
def home():
    return "REST API for managing client responses is running!", 200

# Create the 'client_responses' table
@app.route('/create-table', methods=['POST'])
def create_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS client_responses (
            id SERIAL PRIMARY KEY,
            client_name VARCHAR(255),
            response JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Table 'client_responses' created successfully or already exists."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new response
@app.route('/add-response', methods=['POST'])
def add_response():
    data = request.json
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
        return jsonify({"error": str(e)}), 500

# Get all responses
@app.route('/get-responses', methods=['GET'])
def get_responses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client_responses")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Heroku's PORT or default to 5000
    app.run(host="0.0.0.0", port=port)
