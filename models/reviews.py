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
    pass

def delete_review(review_id):
    pass

