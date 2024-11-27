from flask import Flask, request, jsonify
import psycopg2
import os

# Flask application initialization
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
    return "REST API is running with full database control!", 200

# Route to create a new table
@app.route('/create-table', methods=['POST'])
def create_table():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "No SQL query provided"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Table created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to create table: {str(e)}"}), 500

# Route to add a new record
@app.route('/add-record', methods=['POST'])
def add_record():
    data = request.json
    table = data.get("table")
    record = data.get("record")
    if not table or not record:
        return jsonify({"error": "Invalid input"}), 400
    try:
        columns = ', '.join(record.keys())
        values = ', '.join(['%s'] * len(record))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})", tuple(record.values()))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Record added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add record: {str(e)}"}), 500

# Route to update a record
@app.route('/update-record', methods=['PUT'])
def update_record():
    data = request.json
    table = data.get("table")
    record_id = data.get("id")
    updates = data.get("updates")
    if not table or not record_id or not updates:
        return jsonify({"error": "Invalid input"}), 400
    try:
        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE {table} SET {set_clause} WHERE id = %s",
            tuple(updates.values()) + (record_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Record updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update record: {str(e)}"}), 500

# Route to delete a record
@app.route('/delete-record', methods=['DELETE'])
def delete_record():
    data = request.json
    table = data.get("table")
    record_id = data.get("id")
    if not table or not record_id:
        return jsonify({"error": "Invalid input"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Record deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete record: {str(e)}"}), 500

# Route to delete a table
@app.route('/delete-table', methods=['DELETE'])
def delete_table():
    data = request.json
    table = data.get("table")
    if not table:
        return jsonify({"error": "Invalid input"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Table {table} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete table: {str(e)}"}), 500

# Main application entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
