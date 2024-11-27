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

# Add a new response
@app.route('/add-response', methods=['POST'])
def add_response():
    data = request.json
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

# Get all responses
@app.route('/get-responses', methods=['GET'])
def get_responses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client_responses")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Heroku's PORT or default to 5000
    app.run(host="0.0.0.0", port=port)
