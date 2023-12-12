from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.database import Base, User, Review, List, DB_URL

engine = create_engine(DB_URL)

def search_lists(search_terms, limit):
    pass

def get_lists(user_id, book_id, list_id, limit):
    pass

def update_list(list_id, books, title, description):
    pass

def create_list(books, title='Untitled', description=None):
    pass

def add_book(book_id):
    pass


def delete_book(list_id, book_id):
    pass

def delete_list(list_id):
    pass

# ADD OPTIONAL ARGUMENTS

