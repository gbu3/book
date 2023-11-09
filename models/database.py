from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'postgresql://gracebu@localhost:5432/book'

Base = declarative_base()

# class UserFollower(Base):
#     __tablename__ = 'user_followers'

#     user_id = Column(Integer, ForeignKey('USERS.user_id'), primary_key=True)
#     follower_id = Column(Integer, ForeignKey('USERS.user_id'), primary_key=True)

#     # # Define a relationship to access the connected tables
#     user = relationship('User', foreign_keys=[user_id], back_populates='following')
#     follower = relationship('User', foreign_keys=[follower_id], back_populates='followers')

user_follower_association = Table('user_followers', Base.metadata,
    Column('user', Integer, ForeignKey('users.user_id')),
    Column('follower', Integer, ForeignKey('users.user_id'))
)

like_association = Table('likes', Base.metadata,
    Column('user', Integer, ForeignKey('users.user_id')),
    Column('list', Integer, ForeignKey('lists.list_id'))
)

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    metadata_info = Column(String)

    lists = relationship('List', back_populates='creator')
    reviews = relationship('Review', back_populates='reviewer')
    liked_lists = relationship('Like', back_populates='user')

    # Define a one-to-many relationship for users following this user
    following = relationship('User', secondary=user_follower_association, back_populates='user')
    followers = relationship('User', secondary=user_follower_association, back_populates='follower')
    # following = relationship('UserFollower', foreign_keys=[UserFollower.user_id], back_populates='user')
    # followers = relationship('UserFollower', foreign_keys=[UserFollower.follower_id], back_populates='follower')

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('USERS.user_id'))
    book_id = Column(Integer, ForeignKey('BOOKS.book_id'))
    summary = Column(String)
    note = Column(String)
    rating = Column(Integer)

    reviewer = relationship('User', back_populates='reviews')
    book = relationship('Book', back_populates='reviews')

list_book_association = Table('list_books', Base.metadata,
    Column('list_id', Integer, ForeignKey('Lists.list_id')),
    Column('book_id', Integer, ForeignKey('Books.book_id'))
)

class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    # genre = Column(String)
    # metadata_info = Column(String)

    reviews = relationship('Review', back_populates='book')
    lists = relationship('List', secondary=list_book_association, back_populates='books')

class List(Base):
    __tablename__ = 'lists'

    list_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('USERS.user_id'))
    description = Column(String)
    title = Column(String)

    creator = relationship('User', back_populates='lists')
    liked_by = relationship('Like', back_populates='list')
    books = relationship('Book', secondary=list_book_association, back_populates='lists')

# class ListBook(Base):
#     __tablename__ = 'list_books'

#     list_id = Column(Integer, ForeignKey('LISTS.list_id'), primary_key=True)
#     book_id = Column(Integer, ForeignKey('BOOKS.book_id'), primary_key=True)

#     # Define a relationship to access the connected tables
#     book = relationship('Book', back_populates='lists')
#     list = relationship('List') # ???


# class Like(Base):
#     __tablename__ = 'LIKES'

#     like_id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.user_id'))
#     list_id = Column(Integer, ForeignKey('lists.list_id'))

#     user = relationship('User', back_populates='liked_lists')
#     list = relationship('List', back_populates='liked_by')
