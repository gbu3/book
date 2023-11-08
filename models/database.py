from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'postgresql://gracebu@localhost:5432/book'

Base = declarative_base()

class UserFollower(Base):
    __tablename__ = 'user_followers'

    user_id = Column(Integer, ForeignKey('USERS.user_id'), primary_key=True)
    follower_id = Column(Integer, ForeignKey('USERS.user_id'), primary_key=True)

    # # Define a relationship to access the connected tables
    user = relationship('User', foreign_keys=[user_id], back_populates='following')
    follower = relationship('User', foreign_keys=[follower_id], back_populates='followers')

class User(Base):
    __tablename__ = 'USERS'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    metadata_info = Column(String)

    lists = relationship('List', back_populates='creator')
    reviews = relationship('Review', back_populates='reviewer')
    liked_lists = relationship('Like', back_populates='user')

    # should i add the followers/following back in here
    # Define a one-to-many relationship to UserFollower for users following this user
    following = relationship('UserFollower', foreign_keys=[UserFollower.user_id], back_populates='user')
    followers = relationship('UserFollower', foreign_keys=[UserFollower.follower_id], back_populates='follower')

class Review(Base):
    __tablename__ = 'REVIEWS'

    review_id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('USERS.user_id'))
    book_id = Column(Integer, ForeignKey('BOOKS.book_id'))
    summary = Column(String)
    note = Column(String)
    rating = Column(Integer)

    reviewer = relationship('User', back_populates='reviews')
    book = relationship('Book', back_populates='reviews')

class Book(Base):
    __tablename__ = 'BOOKS'

    book_id = Column(Integer, primary_key=True)
    # genre = Column(String)
    # metadata_info = Column(String)

    reviews = relationship('Review', back_populates='book')

class List(Base):
    __tablename__ = 'LISTS'

    list_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('USERS.user_id'))
    description = Column(String)
    title = Column(String)

    creator = relationship('User', back_populates='lists')
    liked_by = relationship('Like', back_populates='list')

class ListBook(Base):
    __tablename__ = 'list_books'

    list_id = Column(Integer, ForeignKey('LISTS.list_id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('BOOKS.book_id'), primary_key=True)

    # Define a relationship to access the connected tables
    book = relationship('Book')
    list = relationship('List') # ???

class Like(Base):
    __tablename__ = 'LIKES'

    like_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('USERS.user_id'))
    list_id = Column(Integer, ForeignKey('LISTS.list_id'))

    user = relationship('User', back_populates='liked_lists')
    list = relationship('List', back_populates='liked_by')
