from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bookmanagement import book_management_bp
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Bibliothéque_Numérique"]
users_collection = db["users"]

# Predefine Admin (ensure it exists)
admin_user = {
    "username": "admin",
    "password": generate_password_hash("admin123", method='pbkdf2:sha256'),  # Correct hashing method
}
if not users_collection.find_one({"username": "admin"}):
    users_collection.insert_one(admin_user)


app.register_blueprint(book_management_bp)
# Home Page
@app.route('/')
def home():
    username = session.get('username')
    role = session.get('role')
    return render_template('index.html', username=username, role=role)

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        email = request.form['email']

        if role not in ["etudiant", "enseignant"]:
            flash("Invalid role!")
            return redirect(url_for('register'))

        if users_collection.find_one({"username": username}):
            flash("User already exists!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Correct hashing method
        new_user = {
            "username": username,
            "password": hashed_password,
            "role": role,
            "email": email
        }
        users_collection.insert_one(new_user)
        flash("User registered successfully!")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            # Store user info in session
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome {user['username']}, you are logged in as {user['role']}.")

            # Redirect to admin dashboard if user is an admin
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))  # Redirect to home for other users
        else:
            flash("Invalid credentials!")
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    # Logic to end the session (e.g., remove user from session)
    session.pop('username', None)  # Correct the key to 'username'
    session.pop('role', None)  # Optional: Remove role from session
    flash("You have been logged out.")
    return redirect(url_for('home'))  # Redirect to the home page or login page

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is logged in and is an admin
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html', username=session['username'], role=session['role'])
    else:
        flash("Access denied. You are not authorized to view this page.")
        return redirect(url_for('home'))
    


if __name__ == '__main__':
    app.run(
        port=5001,  # Make sure the parentheses are correctly closed
        debug=True
    )
