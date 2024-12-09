# bookmanagement.py

from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime, timedelta

# Create a blueprint for book management
book_management_bp = Blueprint('book_management', __name__)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://khaleduser:FW5VoILzxQ9OR7xb@cluster0.eij2z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Bibliothéque_Numérique"]
books_collection = db["books"]







# Add Book Route
from datetime import datetime, timedelta

# Add Book Route with availability calculation
@book_management_bp.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    publication_year = request.form['publication_year']
    isbn = request.form['isbn']
    status = request.form['status']

    # Calculate availability dates
    current_date = datetime.now()
    if status.lower() == "borrowed":
        due_date = current_date + timedelta(days=14)  # Example: 2 weeks borrowing period
    else:
        due_date = None  # No due date for available or reserved books

    # Prepare the book data
    new_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "publication_year": publication_year,
        "isbn": isbn,
        "status": status,
        "added_date": current_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d") if due_date else None
    }

    # Insert the book into the database
    books_collection.insert_one(new_book)
    flash("Book added successfully with calculated dates!")
    return redirect(url_for('book_management.admin_dashboard'))

    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    publication_year = request.form['publication_year']
    isbn = request.form['isbn']
    status = request.form['status']

    new_book = {
        "title": title,
        "author": author,
        "genre": genre,
        "publication_year": publication_year,
        "isbn": isbn,
        "status": status
        
    }

    books_collection.insert_one(new_book)
    flash("Book added successfully!")
    return redirect(url_for('book_management.admin_dashboard'))





# Admin Dashboard Route (to display books)
@book_management_bp.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')



# Delete Book Route
@book_management_bp.route('/delete_book/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    result = books_collection.delete_one({"isbn": isbn})
    if result.deleted_count > 0:
        return jsonify({"message": "Book deleted successfully!"}), 200
    else:
        return jsonify({"message": "Book not found."}), 404

# Modify Book Route
@book_management_bp.route('/modify_book/<isbn>', methods=['POST'])
def modify_book(isbn):
    updated_data = {
        "title": request.form['title'],
        "author": request.form['author'],
        "genre": request.form['genre'],
        "publication_year": request.form['publication_year'],
        "status": request.form['status']
    }
    result = books_collection.update_one({"isbn": isbn}, {"$set": updated_data})
    if result.modified_count > 0:
        flash("Book updated successfully!")
        return redirect(url_for('book_management.admin_dashboard'))
    else:
        flash("Book not found or no changes were made.")
        return redirect(url_for('book_management.admin_dashboard'))

# Fetch all books
@book_management_bp.route('/api/books', methods=['GET'])
def get_all_books():
    books = list(books_collection.find({}, {'_id': 0}))  # Exclude the MongoDB ID
    return jsonify(books)

# Fetch books with filters
@book_management_bp.route('/api/books/filter', methods=['GET'])
def get_filtered_books():
    filters = {}
    if 'filter' in request.args:
        for field in request.args.getlist('filter'):
            if field in ['title', 'author', 'genre', 'isbn', 'publication_year']:
                filters[field] = {'$regex': request.args.get('search', ''), '$options': 'i'}
    
    books = list(books_collection.find(filters, {'_id': 0}))
    return jsonify(books)



