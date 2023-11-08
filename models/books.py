from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, UserFollower, Review, Book, List, ListBook, Like, DB_URL

engine = create_engine(DB_URL)

def search_books(search_terms, limit):
    pass

def get_book(book_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        book = session.query(Book).filter_by(book_id=book_id).first()

        session.close()
        engine.dispose()

        if not book:
            return None
        else:
            return {} # fill this in w the relevant info

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)

def create_book(cover_image, rating, book_data):
    pass

def update_book(book_id, cover_image, rating, book_data):
    pass

def delete_book(book_id):
    pass
