# bookmanagement.py
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash,jsonify
from pymongo import MongoClient

# Create a blueprint for book management
book_management_bp = Blueprint('book_management', __name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Bibliothéque_Numérique"]
books_collection = db["books"]

# Add Book Route
@book_management_bp.route('/add_book', methods=['POST'])
def add_book():
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
    return redirect(url_for('admin_dashboard'))

# View All Books Route
@book_management_bp.route('/books', methods=['GET'])
def view_books():
    search_query = request.args.get('search', '')
    if search_query:
        books = list(books_collection.find({
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"author": {"$regex": search_query, "$options": "i"}}
            ]
        }))
    else:
        books = list(books_collection.find())
    return render_template('view_books.html', books=books)

# Update Book Route
@book_management_bp.route('/update_book/<isbn>', methods=['POST'])
def update_book(isbn):
    updated_data = {
        "title": request.form.get('title'),
        "author": request.form.get('author'),
        "genre": request.form.get('genre'),
        "publication_year": request.form.get('publication_year'),
        "status": request.form.get('status')
    }
    books_collection.update_one({"isbn": isbn}, {"$set": updated_data})
    flash("Book updated successfully!")
    return redirect(url_for('book_management.view_books'))

# Delete Book Route
@book_management_bp.route('/delete_book/<isbn>', methods=['POST'])
def delete_book(isbn):
    books_collection.delete_one({"isbn": isbn})
    flash("Book deleted successfully!")
    return redirect(url_for('book_management.view_books'))
@book_management_bp.route('/api/books', methods=['GET'])
def get_books():
    books = list(books_collection.find({}, {'_id': 0}))  # Exclude the MongoDB ID
    return jsonify(books)