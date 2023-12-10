from flask import Flask, request, make_response, redirect, url_for, jsonify, abort, render_template, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from model.database import DB_URL, User
import model.books as books
import model.users as users
import model.lists as lists
import model.reviews as reviews
import os
from sys import argv, stderr, exit
import re

"""
central place where URL routes are defined
"""

app = Flask(__name__, template_folder='view')
app.secret_key = os.urandom(24)

#-----------------------------------------------------------------------
# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
engine = create_engine(DB_URL)
Session = scoped_session(sessionmaker(bind=engine))

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    try:
        user = session.query(User).get(int(user_id))
        if not user:
            return None
        else:
            return user
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

# LOGIN ENDPOINTS
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    user_obj = users.get_user_by_email(email)

    if user_obj and user_obj.check_password(request.form['password']):
        login_user(user_obj)
        return redirect(url_for('index'))
    else: # on error
        flash('Invalid email or password')
        return render_template('login.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        ## INPUT CHEKCING ##
        if users.get_user_by_username(username):
            flash("Username already taken.")
            return render_template('register.html')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.")
            return render_template('register.html')

        if not re.match(r"\d", phone):
            flash("Invalid phone number.")
            return render_template('register.html')

        # password checking
        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('register.html')

        if users.create_user(username, full_name, email, phone, password):
            return redirect(url_for('login'))
        else:
            flash("Error creating user.")
            return render_template('register.html')

    return render_template('register.html')

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    # put whatever needed into the HTML
    html = render_template("index.html")

    response = make_response(html)
    return response

@app.route('/users/profile', methods=['GET'])
@login_required
def get_profile_info():
    """
    get current user information for profile page
    """
    user_dict = users.get_user_info(current_user.user_id)
    if user_dict:
        html = render_template('profile.html',
            user_id=user_dict['user_id'],
            username=user_dict['username'],
            full_name = user_dict['full_name'],
            email=user_dict['user_email'],
            phone=user_dict['user_phone'])
    else:
        html = render_template('profile.html', name=None)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

# BOOKS endpoints

@app.route('/books/search', methods=['GET'])
def search_books():
    """
    return a list of all books that fit request structure such as keyword, title, author, etc.
    LIMIT 1000 unless otherwise specified
    """
    # search by keyword, title, author (don't have to specify which is which)
    search_terms = request.args.get('search')
    if not search_terms:
        return jsonify(None)
    
    limit = request.args.get("limit")
    if not limit:
        limit = 1000

    return jsonify(books.search_books(search_terms, limit))

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    search a book by id. returns -1 if no book is found
    """
    # first, validate that book_id is an integer
    try:
        book_id = int(book_id)
    except ValueError:
        abort(400, "book_id is not an integer") # if the thing is <int:> then would this even happen?
        
    return jsonify(books.get_book(book_id))

@app.route('/books', methods=['POST'])
def create_book():
    """
    add a new book to the collection
    """
    cover_image = request.form.get('cover_image')
    rating = request.form.get('rating')
    book_data = request.form.get('metadata')
    # request structure:
        # cover_image, rating, genre, 
        # metadata: title, author, translator, editor, date, description, publisher_name, publisher_location
    if not book_data:
        abort(400, "book data not provided")

    book_id = request.form.get('book_id')
    if not book_id:
        return jsonify(books.create_book(cover_image, rating, book_data)) # should just return the book data back if successful, or the new book_id

    return jsonify(books.update_book(book_id, cover_image, rating, book_data))
    # should also check that certain required parts of book data are provided


@app.route('/books/review/<int:book_id>', methods=['POST'])
def review_book(book_id):
    """
    add a new review for the book (or if one already exists, update it)
    """
    try:
        book_id = int(book_id)
    except ValueError:
        abort(400, "book_id is not an integer")

    return jsonify(reviews.create_review(book_id))

@app.route('/books/list/<int:book_id>', methods=['POST'])
def list_book(book_id):
    """
    add the book to a list
    if valid list_id given in request, will be added to that list
    otherwise, new list will be created with the book in it (Untitled #x)
    """
    try:
        book_id = int(book_id)
    except ValueError:
        abort(400, "book_id is not an integer")

    list_id = request.args.get("list_id")
    if list_id:
        try:
            list_id = int(list_id)
        except ValueError:
            abort(400, "list_id is not an integer")

        return jsonify(lists.add_book(book_id))
    else:
        return jsonify(lists.create_list(book_id))
    
# @app.route('/books/<int:book_id>', methods=['PUT'])
# def update_book(book_id):
#     """
#     update an existing book in the collection
#     """
#     book_data = request.json
#     if not book_data:
#         return jsonify(None) # or something like this
    
#     return jsonify(books.update_book(book_id, book_data))

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    delete a book from the collection
    NOT SURE if this is an endpoint that should be exposed...
    """
    try:
        book_id = int(book_id)
    except ValueError:
        abort(400, "book_id is not an integer")
    
    return jsonify(books.delete_book(book_id))
    

#-----------------------------------------------------------------------

# reviews endpoints

@app.route('/reviews', methods=['GET'])
def get_review():
    """
    return a list of all the reviews written by a user, OR
    return a list of all the reviews for a book, OR
    return just the review
    LIMIT 100 unless otherwise specified
    """
    user_id = request.args.get("user")
    book_id = request.args.get("book")
    review_id = request.args.get("review")

    if not user_id and not book_id and not review_id:
        abort(400, "provide params")

    limit = request.args.get("limit")
    if not limit:
        limit = 100

    return jsonify(reviews.get_reviews(user_id, book_id, review_id, limit))
    
    # if user_id:
    #     return jsonify(users.get_reviews(user_id, limit))
    # if book_id:
    #     try:
    #         book_id = int(book_id)
    #     except ValueError:
    #         abort(400, "book_id is not an integer")
    #     return jsonify(books.get_reviews(book_id, limit))
    # if review_id:
    #     try:
    #         review_id = int(review_id)
    #     except ValueError:
    #         abort(400, "review_id is not an integer")
    #     return jsonify(reviews.get_review(review_id))

@app.route('/reviews', methods=['POST'])
def create_update_review():
    """
    creates a new review for the given book and user
    """
    user_id = request.args.get("user_id")
    if not user_id: 
        abort(400, "user_id not provided")

    review_id = request.args.get("review_id")
    if review_id:
        try:
            review_id = int(review_id)
        except ValueError:
            abort(400, "review_id is not an integer")

        summary = request.args.get("summary")
        note = request.args.get("note")
        rating = request.args.get("rating")

        return jsonify(reviews.update_review(review_id, user_id, summary, note, rating))

    # else, create a new review
    book_id = request.args.get("book_id")
    user_id = request.args.get("user_id")
    
    if not book_id: 
        abort(400, "book_id not provided")
    
    summary = request.args.get("summary")
    note = request.args.get("note")
    rating = request.args.get("rating")

    return jsonify(reviews.create_review(book_id, user_id, summary, note, rating))

# @app.route('/reviews/<int:review_id>', methods=['PUT'])
# def update_review(review_id):
#     """
#     update an existing review
#     """
#     try:
#         review_id = int(review_id)
#     except ValueError:
#         abort(400, "review_id is not an integer")
    
#     user_id = request.args.get("user_id")
#     if not user_id: 
#         abort(400, "user_id not provided")
    
#     summary = request.args.get("summary")
#     note = request.args.get("note")
#     rating = request.args.get("rating")

#     return jsonify(reviews.update_review(review_id, user_id, summary, note, rating))

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    delete a review
    """
    try:
        review_id = int(review_id)
    except ValueError:
        abort(400, "review_id is not an integer")
    
    return jsonify(reviews.delete_review(review_id))


#-----------------------------------------------------------------------

# lists endpoints
@app.route('/lists/search')
def search_lists():
    """
    return all lists that match a keyword/phrase
    LIMIT 100 unless otherwise specified
    """
    search_terms = request.args.get('search')
    if not search_terms:
        return jsonify(None)
    
    limit = request.args.get("limit")
    if not limit:
        limit = 100

    return jsonify(lists.search_lists(search_terms, limit))

@app.route('/lists', methods=['GET'])
def get_lists():
    """
    return all lists made by one user, OR
    return all lists that contain the given book, OR
    return the list if it exists
    LIMIT 100 unless otherwise specified
    """
    user_id = request.args.get("user")
    book_id = request.args.get("book")
    list_id = request.args.get("list")

    if not user_id and not book_id and not list_id:
        abort(400, "provide params")

    limit = request.args.get("limit")
    if not limit:
        limit = 100

    return lists.get_lists(user_id, book_id, list_id, limit)
    
    if user_id:
        return jsonify(users.get_lists(user_id, limit))
    if book_id:
        try:
            book_id = int(book_id)
        except ValueError:
            abort(400, "book_id is not an integer")
        return jsonify(books.get_lists(book_id, limit))
    if list_id:
        try:
            list_id = int(list_id)
        except ValueError:
            abort(400, "list_id is not an integer")
        return jsonify(lists.get_list(list_id))

@app.route('/lists', methods=['POST'])
def create_update_list():
    """
    create a new list with the given info
    """
    books = request.body.get("books")
    title = request.body.get("title")
    description = request.body.get("description")

    list_id = request.body.get("list")
    if list_id:
        try:
            list_id = int(list_id)
        except ValueError:
            abort(400, "list_id is not an integer")
        
        return jsonify(lists.update_list(list_id, books, title, description))

    if not books:
        abort(400, "need at least one book per list")
    if not title:
        title = "Untitled"
    
    return jsonify(lists.create_list(books, title, description))

@app.route('/lists/books', methods=['DELETE'])
def delete_book_from_list():
    """
    removes the specified book from the specified list.
    """
    list_id = request.body.get("list")
    book_id = request.body.get("book")
    if not list_id or not book_id:
        abort(400, "need to provide both list and book ids")

    try:
        list_id = int(list_id)
        book_id = int(book_id)
    except ValueError:
        abort(400, "list_id or book_id is not an integer")
    
    return jsonify(lists.delete_book(list_id, book_id))

@app.route('/lists/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    """
    delete a list
    """
    try:
        list_id = int(list_id)
    except ValueError:
        abort(400, "list_id is not an integer")

    return jsonify(lists.delete_list(list_id))


#-----------------------------------------------------------------------

# users endpoints

@app.route('/users/search', methods=['GET'])
def search_users():
    """
    return all users who match a keyword/phrase
    LIMIT 100 unless otherwise specified
    """
    search_terms = request.args.get('search')
    if not search_terms:
        return jsonify(None)
    
    limit = request.args.get("limit")
    if not limit:
        limit = 100

    return jsonify(users.search_users(search_terms, limit))

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    get user by id
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.get_user(user_id))

@app.route('/users/<int:user_id>/followers', methods=['GET'])
def get_followers(user_id):
    """
    returns a list of user_ids that follow the given user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.get_followers(user_id))

@app.route('/users/<int:user1_id>/followers/<int:user2_id>', methods=['GET'])
def is_a_follower(user1, user2):
    """
    checks whether user2 follows user1
    """
    try:
        user1 = int(user1)
        user2 = int(user2)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.is_a_follower(user2, user1)) # this function checks whether (a,b) a follows b

@app.route('/users/<int:user_id>/following', methods=['GET'])
def get_following(user_id):
    """
    returns a list of user_ids that the given user is following
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.get_following(user_id))

@app.route('/users/<int:user1_id>/following/<int:user2_id>', methods=['GET'])
def is_following(user1, user2):
    """
    checks whether user1 follows user2
    """
    try:
        user1 = int(user1)
        user2 = int(user2)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.is_a_follower(user1, user2))

@app.route('/users', methods=['POST'])
def create_update_user():
    """
    creates or updates a new user
    depending on whether user_id is given
    """
    user_data = request.body.get('user_data')
    # request structure:
        # username, profile_image
        # metadata: full_name, location, email, etc.
    if not user_data:
        abort(400, "user data not provided")
    # should also check that certain required parts of user data are provided
        
    user_id = request.body.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            abort(400, "user_id is not an integer")
    
        return jsonify(users.update_user(user_id, user_data))

    return jsonify(users.create_user(user_data)) # should just return the user data back if successful, or the new user_id?

@app.route('/users/<int:user1_id>/follow/<int:user2_id>', methods=['POST', 'PUT'])
def follow_user(user1, user2):
    """
    user 1 follows user 2
    """
    try:
        user1 = int(user1)
        user2 = int(user2)
    except ValueError:
        abort(400, "user_id is not an integer")
    
    return jsonify(users.follow_user(user1, user2))

@app.route('/users/<int:user1_id>/unfollow/<int:user2_id>', methods=['POST', 'PUT'])
def unfollow_user(user1, user2):
    """
    user 1 unfollows user 2
    """
    try:
        user1 = int(user1)
        user2 = int(user2)
    except ValueError:
        abort(400, "user_id is not an integer")
    
    return jsonify(users.unfollow_user(user1, user2))

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    delete the user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")
    return jsonify (users.delete_user(user_id))


if __name__ == '__main__':
    app.run(debug=True)