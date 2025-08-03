from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import sqlite3
import os
import csv

app = Flask(__name__)
app.secret_key = 'secret123'

# Initialize the database from CSV
def init_db_from_csv():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            password TEXT NOT NULL,
            filename TEXT NOT NULL
        )
    ''')

    # Optional: clear existing entries
    c.execute('DELETE FROM users')

    # Load from users.csv
    try:
        with open('users.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                c.execute("INSERT OR IGNORE INTO users (user_id, password, filename) VALUES (?, ?, ?)",
                          (row['user_id'].strip(), row['password'].strip(), row['filename'].strip()))
    except FileNotFoundError:
        print("⚠️ users.csv not found! Please ensure it is uploaded.")

    conn.commit()
    conn.close()

# Run at startup
init_db_from_csv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id'].strip()
    password = request.form['password'].strip()

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = c.fetchone()
    conn.close()

    if result:
        return send_from_directory('static/certificates', result[0], as_attachment=True)
    else:
        flash("Invalid User ID or Password")
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
