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
    username = Column(String)
    full_name = Column(String)
    email = Column(String)
    metadata_info = Column(String)

    lists = relationship('List', back_populates='creator')
    reviews = relationship('Review', back_populates='reviewer')
    liked_lists = relationship('List', secondary=like_association, back_populates='liked_by')

    # Define a one-to-many relationship for users following this user
    following = relationship(
        'User',
        secondary=user_follower_association,
        primaryjoin=user_id == user_follower_association.c.follower,
        secondaryjoin=user_id == user_follower_association.c.user,
        back_populates='followers'
    )

    followers = relationship(
        'User',
        secondary=user_follower_association,
        primaryjoin=user_id == user_follower_association.c.user,
        secondaryjoin=user_id == user_follower_association.c.follower,
        back_populates='following'
    )

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))
    summary = Column(String)
    note = Column(String)
    rating = Column(Integer)

    reviewer = relationship('User', back_populates='reviews')
    book = relationship('Book', back_populates='reviews')

list_book_association = Table('list_books', Base.metadata,
    Column('list_id', Integer, ForeignKey('lists.list_id')),
    Column('book_id', Integer, ForeignKey('books.book_id'))
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
    creator_id = Column(Integer, ForeignKey('users.user_id'))
    description = Column(String)
    title = Column(String)

    creator = relationship('User', back_populates='lists')
    liked_by = relationship('User', secondary=like_association, back_populates='liked_lists')
    books = relationship('Book', secondary=list_book_association, back_populates='lists')


if __name__ == '__main__':
    engine = create_engine(DB_URL)
            
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

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
