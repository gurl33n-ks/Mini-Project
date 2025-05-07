from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import bcrypt
import re

app = Flask(__name__)

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Icedcoffee@1234",
    database="university_network"
)
cursor = conn.cursor()

# Helper functions
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@dypatil\.edu$", email)

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[\W_]", password)
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        if not is_valid_email(email):
            return "Invalid email domain. Only @dypatil.edu allowed."

        password = request.form['password']
        if not is_strong_password(password):
            return "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character."

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        name = request.form['name']

        try:
            cursor.execute("INSERT INTO users (email, password, name) VALUES (%s, %s, %s)", (email, hashed_pw, name))
            conn.commit()
            return "User registered successfully."
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT id, password, name FROM users WHERE email=%s", (email,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode(), result[1].encode()):
            return redirect(url_for('dashboard', user_id=result[0], user_name=result[2]))
        else:
            return "Login failed. Check your credentials."

    return render_template('login.html')

@app.route('/dashboard/<int:user_id>/<user_name>')
def dashboard(user_id, user_name):
    return render_template('dashboard.html', user_name=user_name, user_id=user_id)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        feedback = request.form['feedback']
        email = request.form['email']

        if not is_valid_email(email):
            return "Invalid email domain. Only @dypatil.edu allowed."

        try:
            cursor.execute(
                "INSERT INTO feedback (name, subject, feedback, email_address) VALUES (%s, %s, %s, %s)",
                (name, subject, feedback, email)
            )
            conn.commit()
            return "Feedback submitted successfully."
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('feedback.html')

@app.route('/manage_committee/<int:user_id>', methods=['GET', 'POST'])
def manage_committee(user_id):
    if request.method == 'POST':
        name = request.form['committee_name']
        desc = request.form['description']

        cursor.execute("SELECT id FROM committees WHERE name=%s", (name,))
        result = cursor.fetchone()

        if result:
            cursor.execute(
                "UPDATE committees SET description=%s, updated_by=%s WHERE name=%s",
                (desc, user_id, name)
            )
            conn.commit()
            return "Committee updated."
        else:
            cursor.execute(
                "INSERT INTO committees (name, description, updated_by) VALUES (%s, %s, %s)",
                (name, desc, user_id)
            )
            conn.commit()
            return "Committee added."

    return render_template('manage_committee.html')

if __name__ == '__main__':
    app.run(debug=True)