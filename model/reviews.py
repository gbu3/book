# reviews need to have global id numbers, irrespective of the user

from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from model.database import DB_URL, Base, User, Review, List, Editions, Authors
from model.books import get_edition_title_cover_authors

engine = create_engine(DB_URL)

REVIEW_CHARACTER_LENGTH = 500

def _review_to_dict(review):
    """
    convert a Review to a dictionary to return
    detailed information for a review page
    """
    if not review:
        return None
    
    return {
        "review_id": review.review_id,
        "reviewer_id": review.reviewer_id,
        "reviewer_username": review.reviewer.username,
        "book_id": review.book_id,
        "book_name": review.book_title,
        "book_cover": review.book_cover,
        "book_authors": review.author_names,
        "summary": review.summary,
        # "note": review.note,
        "rating": review.rating
    }

def user_review_to_dict(review):
    """
    convert a Review to a dict for display
    on user page - more minimal
    """
    return {
        "review_id": review.review_id,
        "book_id": review.book_id,
        "book_title": review.book_title,
        "author_names": review.author_names,
        "rating": review.rating,
        "summary": review.summary
    }

def get_reviews(user_id=None, book_id=None, review_id=None, limit=100):
    """
    get a review by its review_id, or
    search reviews for a particular book and/or user
    (filters will be layered)
    default limit on results is 100
    """
    if all(arg is None for arg in [user_id, book_id, review_id]):
        return None
    
    try:
        if user_id:
            user_id = int(user_id)
        if review_id:
            review_id = int(review_id)
        if book_id:
            if type(book_id) is not str:
                print("incorrect type for book id")
                return None
        else:
            print("no book id provided")
            return None
    except ValueError:
        print("incorrect type for search parameters")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(Review)

        # parameters are treated like filters
        if review_id:
            # if review_id is provided, ignore other filters (just need 1)
            query = query.filter(Review.review_id == review_id)
        else:
            if user_id:
                query = query.filter(Review.reviewer_id == user_id)
            if book_id:
                query = query.filter(Review.book_id == book_id)

        # limit results
        reviews = query.limit(limit).all()

        return [_review_to_dict(review) for review in reviews]
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def create_review(book_id, user_id, summary, rating, note=None):
    """
    creates a new review by the given user for the given book
    includes summary and rating - note not implemented 
    summary will be truncated at 500 characters
    rating is out of 10 (integer values)
    """
    try:
        user_id = int(user_id)
        if type(book_id) is not str:
            print("incorrect type for book id")
            return None
    except ValueError:
        print("incorrect type for user id")
        return None
    
    try:
        rating = int(rating)
        if not 0 <= rating <= 10:
            print("rating must be an integer 1 to 10.")
            return None
    except ValueError:
        print("rating must be an integer 1 to 10.")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # if review already exists
        review = session.query(Review).filter(Review.reviewer_id==user_id, Review.book_id==book_id).first()
        if review:
            print("review already exists")
            return None

        # check that the book is real and that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("create review failed: incorrect user id")
            return None

        edition = session.query(Editions).filter(Editions.id==book_id).first()
        if not edition:
            print("create review failed: incorrect book id")
            return None
        
        edition_info = get_edition_title_cover_authors(edition.id)
        
        new_review = Review(
            reviewer_id=user.user_id, 
            book_id=edition.id, 
            book_title=edition_info['title'], 
            book_cover=edition_info['cover'],
            author_names=edition_info['authors'],
            rating=rating)

        # also for the review text, need to enforce the character limit somehow (probably in the frontend)
        # but just in case, here can truncate at the 300th character and only save that
        if summary:
            if len(summary) > REVIEW_CHARACTER_LENGTH:
                new_review.summary = summary[:500]
            else:
                new_review.summary = summary
        
        session.add(new_review)
        session.commit()

        print(f"New review created: {new_review.review_id}")

        return _review_to_dict(new_review)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_review_summary(review_id, user_id, summary):
    try:
        user_id = int(user_id)
        review_id = int(review_id)
    except ValueError:
        print("incorrect type for user or review id")
        return None
    
    if not summary:
        print("summary not provided")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("update review failed: incorrect user id")
            return None

        review = session.query(Review).filter(Review.review_id==review_id).first()

        if not review:
            print(f"Review {review_id} does not exist.")
            return None

        if summary:
            if len(summary) > REVIEW_CHARACTER_LENGTH:
                review.summary = summary[:500]
            else:
                review.summary = summary
        
        session.commit()

        print(f"Review summary updated: {review.review_id}")

        return _review_to_dict(review)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_review_rating(review_id, user_id, rating):
    try:
        user_id = int(user_id)
        review_id = int(review_id)
    except ValueError:
        print("incorrect type for user or review id")
        return None
    
    if not rating:
        print("rating not provided")
        return None
    
    try:
        rating = int(rating)
        if not 0 <= rating <= 10:
            print("rating must be an integer 1 to 10.")
            return None
    except ValueError:
        print("rating must be an integer 1 to 10.")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("update review failed: incorrect user id")
            return None

        review = session.query(Review).filter(Review.review_id==review_id).first()

        if not review:
            print(f"Review {review_id} does not exist.")
            return None

        review.rating = rating
        
        session.commit()

        print(f"Review rating updated: {review.review_id}")

        return _review_to_dict(review)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def delete_review(review_id):
    if not review_id:
        print("no review id given")
        return None
    
    try:
        review_id = int(review_id)
    except ValueError:
        print("incorrect type for review id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        review = session.query(Review).filter(Review.review_id==review_id).first()
        if review:
            session.delete(review)
            session.commit()
            print(f"Review {review_id} deleted successfully.")
        else:
            print(f"No review found with the id {review_id}")

        return review_id
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()
