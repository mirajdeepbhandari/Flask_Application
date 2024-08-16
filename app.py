from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from yolo_detection import run_detection
import asyncio

app = Flask(__name__)
app.secret_key = 'login'

def establish_connection():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='browser'
        )
        return connection

    except Error as e:
        print(f'Error: {e}')
        flash("Oops! Something went wrong on the server", "db_error")
        return None


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/home")
def home():
    asyncio.create_task(run_detection())
    return render_template("mcq_page.html")

@app.route("/login_validation", methods=["POST"])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("pass")

    connection = establish_connection()

    if connection and connection.is_connected():
        try:
            # Create a cursor object using the cursor() method
            cursor = connection.cursor()

            # Execute a query
            cursor.execute('SELECT * FROM user WHERE email=%s AND password=%s', (email, password))
            record = cursor.fetchone()

            if record:
                return redirect(url_for('home'))
            else:
                flash("Wrong email or password. Please try again.", "login_error")
                # return redirect(url_for('login',email=email, password=password))
                return render_template('login.html',email=email, password=password)
        finally:
            connection.close()  # Ensure the connection is closed

    else:
        return redirect(url_for('login'))  # Handle failed connection gracefully
    



@app.route("/register_validation", methods=["POST"])
def register_validation():
    name = request.form.get("namee")
    email = request.form.get("emaill")
    password = request.form.get("passs")
    conf_password = request.form.get("conf_passs")
    
    connection = establish_connection()

    if connection and connection.is_connected():
        try:
            # Create a cursor object using the cursor() method
            cursor = connection.cursor()

            # Execute a query
            cursor.execute('SELECT * FROM user WHERE email=%s', (email,))
            record = cursor.fetchone()
            
            if record:
                flash("Email already exists. Please try again.", "register_error")
                return redirect(url_for('register'))

            elif password != conf_password:
                flash("Passwords do not match. Please try again.", "register_error")
                return redirect(url_for('register'))

            else:
                cursor.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
                connection.commit()
                return redirect(url_for('login'))

        finally:
            connection.close()  # Ensure the connection is closed

    else:
        return redirect(url_for('register'))  # Handle failed connection gracefully

if __name__ == "__main__":
    app.run(debug=True)
