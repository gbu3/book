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
from html import escape

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
    return redirect(url_for('login'))

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

def get_error_page(message):
    """Returns error page with a given error message """
    html = render_template('error.html',
                           error_message = message)
    response = make_response(html)
    return response

@app.route('/about', methods=['GET'])
@login_required
def about():
    html = render_template("about.html")
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
        html = render_template('profile.html', user=user_dict)
    else:
        html = render_template('profile.html', user=None)
    response = make_response(html)
    return response

@app.route('/users/settings', methods=['GET', 'POST'])
@login_required
def get_user_settings():
    """
    loads the user settings page
    """
    user_id = request.args.get('user_id')
    if not user_id:
        abort(400, "user id not provided")

    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    if current_user.user_id != user_id:
        html = render_template("error.html",
                               error_message = "Access denied")
    else:
        user_dict = users.get_user_info(user_id)
        html = render_template("user_settings.html", user=user_dict)
    response = make_response(html)
    return response

@app.route('/search/users', methods=['GET', 'POST'])
@login_required
def get_user_search_page():
    html = render_template("user_search.html")
    response = make_response(html)
    return response

@app.route('/search/books', methods=['GET', 'POST'])
@login_required
def get_book_search_page():
    html = render_template("book_search.html")
    response = make_response(html)
    return response

@app.route('/search/authors', methods=['GET', 'POST'])
@login_required
def get_author_search_page():
    html = render_template("author_search.html")
    response = make_response(html)
    return response

# @app.route('/search/lists', methods=['GET', 'POST'])
# @login_required
# def get_list_search_page():
#     html = render_template("list_search.html")
#     response = make_response(html)
#     return response

#-----------------------------------------------------------------------

# BOOKS endpoints

@app.route('/books/search', methods=['GET'])
@login_required
def search_books():
    """
    search by:
    - title
    - author: name, fuller_name, personal_name, or author id
    - work id 
    - edition id
    - publish date
    - publisher name
    search will be filtered by a combination of the given parameters
    default limit is 100
    """
    edition_id = request.args.get('edition_id')
    if edition_id:
        edition_id = edition_id.strip()
    work_id = request.args.get('work_id')
    if edition_id:
        edition_id = edition_id.strip()
    author_name = request.args.get('author_name')
    if author_name:
        author_name = author_name.strip()
    author_id = request.args.get('author_id')
    if author_id:
        author_id = author_id.strip()
    title = request.args.get('title')
    if title:
        title = title.strip()
    publisher_name = request.args.get('publisher_name')
    if publisher_name:
        publisher_name = publisher_name.strip()
    publish_date = request.args.get('publish_date')
    if publish_date:
        publish_date = publish_date.strip()
    limit = request.args.get('limit')
    if limit:
        limit = limit.strip()

    try:
        limit = int(limit) if limit else None
    except ValueError:
        abort(400, "limit must be an integer")

    if all(arg is None for arg in [edition_id, work_id, author_name, author_id, title, publish_date, publisher_name]):
        html = render_template("book_search.html",
                               valid_search_terms=False)
    else:
        results = books.search_editions(
            edition_id=edition_id,
            work_id=work_id,
            author_name=author_name,
            author_id=author_id,
            title=title,
            publish_date=publish_date,
            publisher_name=publisher_name,
            limit=limit
        )
        print(results)

        html = render_template("book_search.html",
                               valid_search_terms=True,
                               results=results)
    
    response = make_response(html)
    return response

@app.route('/books/<string:edition_id>', methods=['GET'])
@login_required
def get_edition_info(edition_id):
    if not edition_id:
        abort(400, "edition id not provided")
    
    result = books.get_edition_info(edition_id)
    print(result)

    # if the current user already has a review, pass in the review_id
    curr_user_reviews = reviews.get_reviews(user_id=current_user.user_id, 
                                           book_id=edition_id)
    
    user_lists = lists.get_lists(user_id=current_user.user_id)
    print("user_lists: ", user_lists)
    
    if curr_user_reviews:
        curr_review_id = curr_user_reviews[0]['review_id']
    else:
        curr_review_id = 0

    html = render_template("book_page.html",
                           book=result,
                           user_lists=user_lists,
                           curr_review_id=curr_review_id)
    
    response = make_response(html)
    return response

@app.route('/books', methods=['GET'])
@app.route('/books/', methods=['GET'])
@login_required
def wrong_route_books():
    """
    Providing for incorrect usages of the books endpoint
    """
    return get_error_page("Error: missing book id"), 404


# authors endpoints

@app.route('/authors/search')
@login_required
def search_author():
    """
    search an author by name, fuller_name, personal_name,
    or author_id
    returns a list of author dicts
    limit of search results is default 100
    """
    author_name = request.args.get('author_name')
    if author_name:
        author_name = author_name.strip()
    author_id = request.args.get('author_id')
    if author_id:
        author_id = author_id.strip()

    limit = request.args.get('limit')
    if limit:
        limit = limit.strip()

    try:
        limit = int(limit) if limit else None
    except ValueError:
        abort(400, "limit must be an integer")

    if not author_name and not author_id:
        html = render_template("author_search.html",
                               valid_search_terms=False)
    
    else:
        results = books.search_author(
            author_name=author_name,
            author_id=author_id,
            limit=limit
        )

        print(results)

        html = render_template("author_search.html",
                               valid_search_terms=True,
                               results=results)
    
    response = make_response(html)
    return response

@app.route('/authors/<string:author_id>', methods=['GET'])
@login_required
def get_author_info(author_id):
    if not author_id:
        abort(400, "author id not provided")
    
    result = books.get_author_info(author_id)

    print(result)

    html = render_template("author_page.html",
                           author=result)
    
    response = make_response(html)
    return response

@app.route('/authors', methods=['GET'])
@app.route('/authors/', methods=['GET'])
@login_required
def wrong_route_authors():
    """
    Providing for incorrect usages of the authors endpoint
    """
    return get_error_page("Error: missing author id"), 404

#-----------------------------------------------------------------------

# users endpoints

@app.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """
    search users by user_id, username, full_name, or email
    LIMIT 100 unless otherwise specified
    """
    user_id = request.args.get('user_id')
    if user_id:
        user_id = user_id.strip()
    username = request.args.get('username')
    if username:
        username = username.strip()
    full_name = request.args.get('full_name')
    if full_name:
        full_name = full_name.strip()
    email = request.args.get('email')
    if email:
        email = email.strip()
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return make_response(render_template("user_search.html",
                               valid_search_terms=False))
    
    limit = request.args.get('limit')
    if limit:
        limit = limit.strip()
    
    try:
        user_id = int(user_id) if user_id else None
        limit = int(limit) if limit else None
    except ValueError:
        abort(400, "user_id and limit must be integers")

    if not any([user_id, username, full_name, email]):
        html = render_template("user_search.html",
                               valid_search_terms=False)
        
    else:
        if not user_id:
            user_id = None

        if not limit:
            limit = None
            
        results = users.get_users(
            user_id=user_id, 
            username=username, 
            full_name=full_name, 
            email=email, 
            limit=limit
        )
        print(results)

        html = render_template("user_search.html",
                               valid_search_terms=True,
                               results=results)

    response = make_response(html)
    return response

@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """
    get user information by id
    returns user_id, username, full_name, email, phone,
    lists, reviews, following and followers
    """
    if not user_id:
        abort(400, "user not provided")

    user_dict = users.get_user_info(user_id)
    if user_dict:
        print(user_dict)
        if current_user.user_id == user_id:
            is_follower = False
        else:
            is_follower = users.is_a_follower(current_user.user_id, user_id)
        html = render_template('profile.html', 
            user=user_dict, 
            is_follower=is_follower)
    else:
        html = render_template('profile.html', user=None)
    response = make_response(html)
    return response

@app.route('/users', methods=['GET'])
@app.route('/users/', methods=['GET'])
@login_required
def wrong_route_users():
    """
    Providing for incorrect usages of the users endpoint
    """
    return get_error_page("Error: missing users id"), 404

@app.route('/users/<int:user_id>/followers', methods=['GET'])
@login_required
def get_followers(user_id):
    """
    returns a list of user_ids that follow the given user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.get_followers(user_id))

@app.route('/users/<int:user_id>/following', methods=['GET'])
@login_required
def get_following(user_id):
    """
    returns a list of user_ids that the given user is following
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    return jsonify(users.get_following(user_id))

@app.route('/users/update/username', methods=['POST'])
@login_required
def update_username():
    """
    update user's username.
    """
    current_user_id = current_user.get_id()
    user_id = request.form.get('user_id')
    if not user_id:
        abort(400, "user not provided")
    if current_user_id != user_id:
        abort(403, "Unauthorized access")
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    new_name = request.form.get('username')
    if new_name:
        users.update_user_name(int(user_id), new_name)

    return redirect(url_for('get_user_settings', user_id=user_id))

@app.route('/users/update/full_name', methods=['POST'])
@login_required
def update_full_name():
    """
    update user's full name.
    """
    current_user_id = current_user.get_id()
    user_id = request.form.get('user_id')
    if not user_id:
        abort(400, "user not provided")
    if current_user_id != user_id:
        abort(403, "Unauthorized access")
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    new_name = request.form.get('full_name')
    if new_name:
        users.update_full_name(int(user_id), new_name)

    return redirect(url_for('get_user_settings', user_id=user_id))

@app.route('/users/update/email', methods=['POST'])
@login_required
def update_user_email():
    """
    update user's email
    """
    current_user_id = current_user.get_id()
    user_id = request.form.get('user_id')
    if not user_id:
        abort(400, "user not provided")
    if current_user_id != user_id:
        abort(403, "Unauthorized access")
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    new_email = request.form.get('email')
    if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
            flash("Invalid email address.")
    if new_email:
        users.update_user_email(int(user_id), new_email)
    return redirect(url_for('get_user_settings', user_id=user_id))

@app.route('/users/update/phone', methods=['POST'])
@login_required
def update_user_phone():
    """
    update user's phone number
    """
    current_user_id = current_user.get_id()
    user_id = request.form.get('user_id')
    if not user_id:
        abort(400, "user not provided")
    if current_user_id != user_id:
        abort(403, "Unauthorized access")
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")

    new_phone = request.form.get('phone')
    if not re.match(r"\d", new_phone):
        flash("Invalid phone number.")
    if new_phone:
        users.update_user_phone(int(user_id), new_phone)
    return redirect(url_for('get_user_settings', user_id=user_id))

@app.route('/users/<int:user_id>/follow', methods=['POST', 'PUT'])
@login_required
def follow_user(user_id):
    """
    current user follows the given user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")
    
    users.follow_user(current_user.user_id, user_id)

    return redirect(url_for('get_user', user_id=user_id))

@app.route('/users/<int:user_id>/unfollow', methods=['POST', 'PUT'])
@login_required
def unfollow_user(user_id):
    """
    current user unfollows the given user
    """
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")
    
    users.unfollow_user(current_user.user_id, user_id)

    return redirect(url_for('get_user', user_id=user_id))

@app.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """
    delete the user
    """
    if current_user.user_id != user_id:
        abort(403, "Unauthorized access")
    try:
        user_id = int(user_id)
    except ValueError:
        abort(400, "user_id is not an integer")
    
    result = users.delete_user(current_user.user_id)
    if result:
        print("deleted user")
        flash("User deleted successfully", "success")
        return jsonify({"success": True, "message": "user successfully deleted"}), 200
    else:
        print("failed to delete user")
        flash("Failed to delete user", "error")
        return jsonify({"success": False, "message": "failed to delete user"}), 400

#-----------------------------------------------------------------------

# reviews endpoints

# @app.route('/reviews', methods=['GET', 'POST'])
# @app.route('/reviews/', methods=['GET', 'POST'])
# @login_required
# def wrong_route_reviews():
#     """
#     Providing for incorrect usages of the reviews endpoint
#     """
#     return get_error_page("Error: missing review id"), 404

# may not be needed
@app.route('/reviews', methods=['GET'])
@login_required
def get_reviews():
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

@app.route('/reviews/<int:review_id>', methods=['GET'])
@login_required
def get_review_info(review_id):
    """
    returns the HTML for the individual review page
    if it is current_user's review, will have the
    option to edit the review
    """
    if not review_id:
        abort(400, "review id not provided")
    
    result = reviews.get_review_info(review_id)

    print(result)

    html = render_template("review_page.html",
                           review=result)
    
    response = make_response(html)
    return response

@app.route('/reviews/create', methods=['GET', 'POST'])
@login_required
def get_create_review_page():
    """
    gets the create new review page, which will
    call create_review when info is submitted
    redirects to the review page if successful
    otherwise, back to the book page
    """
    # if the user has already reviewed this book, return review pg
    book_id = request.args.get('book_id')
    if book_id:
        book_id = book_id.strip()
    else:
        abort(400, "no book id provided")
    
    existing_reviews = reviews.get_reviews(user_id=current_user.user_id, book_id=book_id)
    print("existing reviews: ", existing_reviews)

    if existing_reviews:
        # in theory this should never happen - if the user has already
        # reviewed the book, they should just get a "view my review"
        # button on the book page
        return redirect(url_for('get_review_info', 
                                review_id=existing_reviews[0]['review_id']))
    
    book_info = books.get_edition_title_cover_authors(book_id)

    html = render_template("create_review.html", 
                           book_info=book_info, 
                           char_limit=reviews.REVIEW_CHARACTER_LENGTH)
    response = make_response(html)
    return response

@app.route('/reviews', methods=['POST'])
@login_required
def create_review():
    """
    creates a new review for the given book
    authored by curr user
    """
    book_id = request.form.get("book_id")
    
    if not book_id: 
        abort(400, "book_id not provided")

    # check that the book exists
    book_info = books.get_edition_title_cover_authors(book_id)
    if not book_info:
        abort(400, "book does not exist")

    summary = request.form.get("summary")
    rating = request.form.get("rating")

    if not summary and not rating:
        html = render_template("create_review.html", 
                           book_info=book_info, 
                           char_limit=reviews.REVIEW_CHARACTER_LENGTH)
        return make_response(html)

    if summary:
        summary = summary.strip()
    if rating:
        rating = rating.strip()

    try:
        rating = int(rating)
        if not 0 <= rating <= 10:
            abort(400, "rating must be an integer 1 to 10.")
    except ValueError:
        abort(400, "rating must be an integer 1 to 10.")

    result = reviews.create_review(
        book_id=book_id,
        user_id = current_user.user_id,
        summary=summary,
        rating=rating
    )

    print(f"created review: {result}")

    if result:
        return redirect(url_for('get_review_info', review_id = result['review_id']))
    else:
        abort(400, "failed to create review")

    # return jsonify(reviews.create_review(book_id, current_user.user_id, summary, note, rating))

@app.route('/reviews/<int:review_id>/update', methods=['GET', 'POST'])
@login_required
def get_update_review_page(review_id):
    try:
        review_id = int(review_id)
    except ValueError:
        abort(400, "review_id is not an integer")

    existing_review = reviews.get_review_info(review_id)
    if not existing_review:
        return get_error_page("Error: review does not exist"), 404
    
    print(existing_review)

    html = render_template("update_review.html", 
                           review=existing_review,
                           char_limit=reviews.REVIEW_CHARACTER_LENGTH)
    response = make_response(html)
    return response

@app.route('/reviews/<int:review_id>', methods=['POST'])
@login_required
def update_review(review_id):
    """
    update an existing review
    """
    try:
        review_id = int(review_id)
    except ValueError:
        abort(400, "review_id is not an integer")

    # check that this user has ownership of the review
    existing_review = reviews.get_review_info(review_id)
    if current_user.user_id != existing_review['reviewer_id']:
        return get_error_page("You are not the creator of this review.")
    
    summary = request.form.get("summary")
    rating = request.form.get("rating")

    if not summary and not rating:
        html = render_template("update_review.html", 
                           review=existing_review,
                           char_limit=reviews.REVIEW_CHARACTER_LENGTH)
        return make_response(html)

    if summary:
        summary = summary.strip()
    if rating:
        rating = rating.strip()

        try:
            rating = int(rating)
            if not 0 <= rating <= 10:
                abort(400, "rating must be an integer 1 to 10.")
        except ValueError:
            abort(400, "rating must be an integer 1 to 10.")

    result = reviews.update_review(
        review_id=review_id,
        user_id = current_user.user_id,
        summary=summary,
        rating=rating
    )

    if result:
        return redirect(url_for('get_review_info', review_id = result['review_id']))
    else:
        abort(400, "failed to update review")

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """
    delete a review
    """
    try:
        review_id = int(review_id)
    except ValueError:
        abort(400, "review_id is not an integer")
    
    existing_review = reviews.get_review_info(review_id)
    if current_user.user_id != existing_review['reviewer_id']:
        return get_error_page("You are not the creator of this review.")
    
    result = reviews.delete_review(review_id)
    if result:
        print("deleted review")
        flash("Review deleted successfully", "success")
        return jsonify({"success": True, "message": "review successfully deleted"}), 200
    else:
        print("failed to delete review")
        flash("Failed to delete review", "error")
        return jsonify({"success": False, "message": "failed to delete review"}), 400



#-----------------------------------------------------------------------

# lists endpoints
@app.route('/lists/search')
@login_required
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
@login_required
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
    
@app.route('/lists/<int:list_id>', methods=['GET'])
@login_required
def get_list_info(list_id):
    if not list_id:
        abort(400, "list id not provided")
    
    result = lists.get_list_info(list_id)

    print(result)

    html = render_template("list_page.html",
                           lst=result)
    
    response = make_response(html)
    return response

@app.route('/lists/create', methods=['GET', 'POST'])
@login_required
def get_create_list_page():
    """
    gets the create new list page, which will
    call create_list when info is submitted
    redirects to the list page if successful
    otherwise, back to create list page
    """

    html = render_template("create_list.html", 
                           char_limit=lists.DESCRIPTION_CHARACTER_LENGTH)
    response = make_response(html)
    return response

@app.route('/lists', methods=['POST'])
@login_required
def create_list():
    """
    creates a new list authored by curr user
    """
    title = request.form.get("title")
    description = request.form.get("description")

    if title:
        title = title.strip()
    if description:
        description = description.strip()

    result = lists.create_list(
        user_id = current_user.user_id,
        title=title,
        description=description
    )

    print(f"created list: {result}")

    if result:
        return redirect(url_for('get_list_info', list_id = result['list_id']))
    else:
        return redirect(url_for('get_create_list_page'))

@app.route('/lists/<int:list_id>/update', methods=['GET', 'POST'])
@login_required
def get_update_list_page(list_id):
    try:
        list_id = int(list_id)
    except ValueError:
        abort(400, "list_id is not an integer")

    existing_list = lists.get_list_info(list_id)
    if not existing_list:
        return get_error_page("Error: list does not exist"), 404
    
    print(existing_list)

    html = render_template("update_list.html",
                           lst=existing_list,
                           char_limit=lists.DESCRIPTION_CHARACTER_LENGTH)
    response = make_response(html)
    return response

@app.route('/lists/<int:list_id>', methods=['POST'])
@login_required
def update_list(list_id):
    """
    update an existing list
    """
    try:
        list_id = int(list_id)
    except ValueError:
        abort(400, "list_id is not an integer")

    # check that this user has ownership of the review
    existing_list = lists.get_list_info(list_id)
    if current_user.user_id != existing_list['creator_id']:
        return get_error_page("You are not the creator of this list.")
    
    title = request.form.get("title")
    description = request.form.get("description")

    if title:
        title = title.strip()
    if description:
        description = description.strip()

    if not title and not description:
        print("no title and no description provided")
        html = render_template("update_list.html", 
                           lst=existing_list,
                           char_limit=lists.DESCRIPTION_CHARACTER_LENGTH)
        return make_response(html)

    result = lists.update_list(
        user_id = current_user.user_id,
        list_id = list_id,
        title = title,
        description = description
    )

    print(result)

    if result:
        return redirect(url_for('get_list_info', list_id = result['list_id']))
    else:
        abort(400, "failed to update list")

@app.route('/lists/add/<string:book_id>', methods=['POST'])
@login_required
def add_list_book(book_id):
    """
    adds the book to the given list.
    """
    list_id = request.form.get('list_id')
    if not list_id:
        flash('List not selected', 'error')
        return redirect(url_for('get_edition_info', edition_id=book_id))

    result = lists.add_list_book(current_user.user_id, list_id, book_id)
    if result:
        flash('Book added to list successfully', 'success')
    else:
        flash('Failed to add book to list', 'error')

    return redirect(url_for('get_list_info', list_id=list_id))

@app.route('/lists/delete/<string:book_id>', methods=['DELETE'])
@login_required
def delete_book_from_list(book_id):
    """
    removes the specified book from the specified list.
    """
    list_id = request.form.get("list_id")
    if not list_id:
        return jsonify({"success": False, "message": "No list id provided"}), 400

    try:
        list_id = int(list_id)
    except ValueError:
        return jsonify({"success": False, "message": "List_id must be an integer"}), 400
    
    existing_list = lists.get_list_info(list_id)
    if current_user.user_id != existing_list['creator_id']:
        return get_error_page("You are not the creator of this list.")

    result = lists.remove_list_book(current_user.user_id, list_id, book_id)

    if result:
        return jsonify({"success": True, "message": "Book successfully removed from list"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to remove book from list"}), 400

@app.route('/lists/<int:list_id>', methods=['DELETE'])
@login_required
def delete_list(list_id):
    """
    delete a list
    """
    try:
        list_id = int(list_id)
    except ValueError:
        abort(400, "list_id is not an integer")
    
    existing_list = lists.get_list_info(list_id)
    if current_user.user_id != existing_list['creator_id']:
        return get_error_page("You are not the creator of this list.")
    
    result = lists.delete_list(list_id)
    if result:
        print("deleted list")
        flash("List deleted successfully", "success")
        return jsonify({"success": True, "message": "list successfully deleted"}), 200
    else:
        print("failed to delete list")
        flash("Failed to delete list", "error")
        return jsonify({"success": False, "message": "failed to delete list"}), 400



if __name__ == '__main__':
    app.run(debug=True)