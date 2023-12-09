# reviews need to have global id numbers, irrespective of the user

from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, UserFollower, Review, Book, List, ListBook, Like, DB_URL

engine = create_engine(DB_URL)

def _review_to_dict(review):
    """
    convert a Review to a dictionary to return
    """
    if not review:
        return None
    
    return {
        "review_id": review.review_id,
        "reviewer_id": review.reviewer_id,
        "book_id": review.book_id,
        "summary": review.summary,
        "note": review.note,
        "rating": review.rating
    }

def get_reviews(user_id, book_id, review_id, limit):
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
    
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def update_review(review_id, user_id, summary, note, rating):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("create review failed: incorrect user id")
            return None

        review = session.query(Review).filter(Review.review_id==review_id).first()

        if not review:
            print(f"Review {review_id} does not exist.")
            return None

        if summary:
            review.summary = summary
        
        if note:
            review.note = note

        if rating:
            review.rating = rating
        
        session.add(review)
        session.commit()

        print(f"Review updated: {review.review_id}")

        return _review_to_dict(review)
    
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def create_review(book_id, user_id, summary, note, rating):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the book is real and that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("create review failed: incorrect user id")
            return None

        book = session.query(Book).filter(Book.book_id==book_id).first()
        if not book:
            print("create review failed: incorrect book id")
            return None

        # also for the review text, need to enforce the character limit somehow (probably in the frontend)
        # but just in case, here can truncate at the 300th character and only save that
        
        new_review = Review(reviewer_id=user.user_id, book_id=book.book_id, summary=summary, note=note, rating=rating)
        session.add(new_review)
        session.commit()

        print(f"New review created: {new_review.review_id}")

        return _review_to_dict(new_review)
    
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def delete_review(review_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the book is real and that the user exists
        review = session.query(Review).filter(Review.review_id==review_id).first()
        if review:
            session.delete(review)
            session.commit()
            print(f"Review {review_id} deleted successfully.")
        else:
            print(f"No review found with the id {review_id}")

        return review_id
    
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

