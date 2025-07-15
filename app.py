from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# Initialize the database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            password TEXT NOT NULL,
            filename TEXT NOT NULL
        )
    ''')
    # Add users
    c.execute("INSERT OR IGNORE INTO users (user_id, password, filename) VALUES (?, ?, ?)",
              ('123456789', '6789', 'certificate.pdf'))  # Update filename if needed
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']

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
