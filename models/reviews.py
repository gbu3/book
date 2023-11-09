# reviews need to have global id numbers, irrespective of the user

from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, UserFollower, Review, Book, List, ListBook, Like, DB_URL

engine = create_engine(DB_URL)

def get_reviews(user_id, book_id, review_id, limit):
    pass

def update_review(review_id, user_id, summary, note, rating):
    pass

def create_review(book_id, user_id, summary, note, rating):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # TODO: add input validation

        # also for the review text, need to enforce the character limit somehow (probably in the frontend)
        # but just in case, here can truncate at the 300th character and only save that
        
        new_review = Review(reviewer_id=user_id, book_id=book_id, summary=summary, note=note, rating=rating)
        session.add(new_review)
        session.commit()

        print(f"User created with ID: {new_review.review_id}")
        session.close()
        engine.dispose()

        return {"review_id": new_review.review_id, "book_id": new_review.book_id, "user_id": new_review.reviewer_id} # not sure this is the best return type

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)

def delete_review(review_id):
    pass

