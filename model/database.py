from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Date, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

DB_URL = 'postgresql://gracebu@localhost:5432/all_books'

Base = declarative_base()

user_follower_association = Table('user_followers', Base.metadata,
    Column('user', Integer, ForeignKey('users.user_id')),
    Column('follower', Integer, ForeignKey('users.user_id'))
)

like_association = Table('likes', Base.metadata,
    Column('user', Integer, ForeignKey('users.user_id')),
    Column('list', Integer, ForeignKey('lists.list_id'))
)

class User(UserMixin, Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    metadata_info = Column(String)
    password_hash = Column(String)

    lists = relationship('List', back_populates='creator')
    reviews = relationship('Review', back_populates='reviewer')
    liked_lists = relationship('List', secondary='likes', back_populates='liked_by')

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): # for flask_login
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(String, ForeignKey('editions.id'))
    book_title = Column(String)
    book_cover = Column(Integer)
    author_names = Column(String)
    summary = Column(String)
    note = Column(String)
    rating = Column(Integer)

    reviewer = relationship('User', back_populates='reviews')
    book = relationship('Editions', back_populates='reviews')

list_book_association = Table('list_books', Base.metadata,
    Column('list_id', Integer, ForeignKey('lists.list_id')),
    Column('book_id', String, ForeignKey('editions.id'))
)

class List(Base):
    __tablename__ = 'lists'

    list_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('users.user_id'))
    description = Column(String)
    title = Column(String)

    creator = relationship('User', back_populates='lists')
    liked_by = relationship('User', secondary='likes', back_populates='liked_lists')
    books = relationship('Editions', secondary='list_books', back_populates='lists')

# ---------------- EDITIONS ----------------

class Editions(Base):
    __tablename__ = 'editions'
    id = Column(String, primary_key=True)
    created = Column(Date)
    last_modified = Column(Date)
    revision = Column(Integer)
    latest_revision = Column(Integer)
    title = Column(String)
    subtitle = Column(String)
    title_prefix = Column(String)
    full_title = Column(String)
    copyright_date = Column(String)
    publish_date = Column(String)
    by_statement = Column(String)
    edition_name = Column(String)
    volume_number = Column(Integer)
    description = Column(Text)
    number_of_pages = Column(Integer)
    pagination = Column(String)
    translation_of = Column(String)
    dewey_decimal_class = Column(String)
    # lccn = Column(Integer) # need to convert from string

    # assoc tables
    authors = relationship("Authors", secondary="editions_authors", back_populates="editions")
    works = relationship("Works", secondary="editions_works", back_populates="editions")
    # classifications = relationship("Classifications", secondary="editions_classifications", back_populates="editions")
    contributors = relationship("Contributors", secondary="editions_contributors", back_populates="editions")
    genres = relationship("Genres", secondary="editions_genres", back_populates="editions")
    languages = relationship("Languages", secondary="editions_languages", back_populates="editions")
    lc_classifications = relationship("LC_Classifications", secondary="editions_lc_class", back_populates="editions")
    lccn = relationship("LCCN", secondary="editions_lccn", back_populates="editions")
    publishers = relationship("Publishers", secondary="editions_publishers", back_populates="editions")
    # publish_countries = relationship("Publish_Countries", secondary="editions_publish_countries", back_populates="editions")
    publish_places = relationship("Places", secondary="editions_publish_places", back_populates="editions")
    series = relationship("Series", secondary="editions_series", back_populates="editions")
    subjects = relationship("Subjects", secondary="editions_subjects", back_populates="editions")
    translated_from_languages = relationship("Languages", secondary="edition_translated_from_language", back_populates="editions")
    work_titles = relationship("Work_Titles", secondary="editions_work_titles", back_populates="editions")
    reviews = relationship('Review', back_populates='book')
    lists = relationship('List', secondary='list_books', back_populates='books')

editions_authors = Table('editions_authors', Base.metadata,
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('author_id', String, ForeignKey('authors.id'))
)

editions_works = Table('editions_works', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('work_id', String, ForeignKey('works.id'))
)

class Contributors(Base):
    # based on fields contributors and contributions
    __tablename__ = 'contributors'
    id = Column(Integer, primary_key=True)
    contributor = Column(String)
    editions = relationship("Editions", secondary="editions_contributors", back_populates="contributors")

editions_contributors = Table('editions_contributors', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('contributor_id', Integer, ForeignKey('contributors.id'))
)

class Editions_Covers(Base):
    __tablename__ = 'editions_covers'
    id = Column(Integer, primary_key=True)
    cover = Column(Integer)
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions", foreign_keys=[edition_id], backref="editions_covers") # MAYBE??

class Genres(Base):
    # from editions and authors
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    genre = Column(String)
    editions = relationship("Editions", secondary="editions_genres", back_populates="genres")
    # authors = relationship("Authors", secondary="authors_genres", back_populates="genres")

editions_genres = Table('editions_genres', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class ISBN_10(Base):
    __tablename__ = 'isbn_10'
    id = Column(Integer, primary_key=True)
    isbn_10 = Column(Integer) # CONVERT FROM STRING
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions")

class ISBN_13(Base):
    __tablename__ = 'isbn_13'
    id = Column(Integer, primary_key=True)
    isbn_10 = Column(Integer) # CONVERT FROM STRING
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions")

class Languages(Base):
    # based on languages in fields in 
    # editions: language, languages, translated_from; 
    # and authors->’languages’; 
    # and works->’original_languages’
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    language = Column(String)
    editions = relationship("Editions", secondary="editions_languages", back_populates="languages")
    # authors = relationship("Authors", secondary="authors_languages", back_populates="languages")
    works = relationship("Works", secondary="works_original_languages", back_populates="original_languages")

editions_languages = Table('editions_languages', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

edition_translated_from_language = Table('edition_translated_from_language', Base.metadata,
    # from "translated_from"
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

class LC_Classifications(Base):
    # based on fields “lc_classifications” AND “lc_classification” 
    # and, from works, “lc_classifications”
    __tablename__ = 'lc_classifications'
    id = Column(Integer, primary_key=True)
    lc_classification = Column(String)
    editions = relationship("Editions", secondary="editions_lc_class", back_populates="lc_classifications")
    works = relationship("Works", secondary="works_lc_class", back_populates="lc_classifications")

editions_lc_class = Table('editions_lc_class', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('lc_classification_id', Integer, ForeignKey('lc_classifications.id'))
)

class LCCN(Base):
    __tablename__ = 'lccn'
    id = Column(Integer, primary_key=True)
    lccn = Column(String)
    editions = relationship("Editions", secondary="editions_lccn", back_populates="lccn")

editions_lccn = Table('editions_lccn', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('lccn_id', Integer, ForeignKey('lccn.id'))
)

class Places(Base):
    # from editions->publish_places and authors->location
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    place = Column(String)
    editions = relationship("Editions", secondary="editions_publish_places", back_populates="publish_places")
    authors = relationship("Authors", secondary="authors_locations", back_populates="locations")

editions_publish_places = Table('editions_publish_places', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('place_id', Integer, ForeignKey('places.id'))
)

class Publishers(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    publisher = Column(String)
    editions = relationship("Editions", secondary="editions_publishers", back_populates="publishers")

editions_publishers = Table('editions_publishers', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('publisher_id', Integer, ForeignKey('publishers.id'))
)

class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    series = Column(String)
    editions = relationship("Editions", secondary="editions_series", back_populates="series")

editions_series = Table('editions_series', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('series_id', Integer, ForeignKey('series.id'))
)

class Subjects(Base):
    # from editions, authors, and works
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    subject = Column(String)
    editions = relationship("Editions", secondary="editions_subjects", back_populates="subjects")
    # authors = relationship("Authors", secondary="authors_subjects", back_populates="subjects")
    works = relationship("Works", secondary="works_subjects", back_populates="subjects")

editions_subjects = Table('editions_subjects', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

class Work_Titles(Base):
    __tablename__ = 'work_titles'
    id = Column(Integer, primary_key=True)
    work_title = Column(String)
    editions = relationship("Editions", secondary="editions_work_titles", back_populates="work_titles")

editions_work_titles = Table('editions_work_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('work_title_id', Integer, ForeignKey('work_titles.id'))
)

# class Classifications(Base):
#     __tablename__ = 'classifications'
#     id = Column(Integer, primary_key=True)
#     classification = Column(String)
#     editions = relationship("Editions", secondary="editions_classifications", back_populates="classifications")

# editions_classifications = Table('editions_classifications', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('edition_id', String, ForeignKey('editions.id')),
#     Column('classification_id', Integer, ForeignKey('classifications.id'))
# )

# class Publish_Countries(Base):
#     __tablename__ = 'publish_countries'
#     id = Column(Integer, primary_key=True)
#     publish_country = Column(String)
#     editions = relationship("Editions", secondary="editions_publish_countries", back_populates="publish_countries")

# editions_publish_countries = Table('editions_publish_countries', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('edition_id', String, ForeignKey('editions.id')),
#     Column('publish_country_id', Integer, ForeignKey('publish_countries.id'))
# )

# class Notes(Base):
#     __tablename__ = 'notes'
#     id = Column(Integer, primary_key=True)
#     note = Column(String)
#     edition_id = Column(String, ForeignKey('editions.id'))
#     edition = relationship("Editions")

# ---------------- AUTHORS ----------------

class Authors(Base):
    __tablename__ = 'authors'
    id = Column(String, primary_key=True)
    created = Column(Date)
    last_modified = Column(Date)
    revision = Column(Integer)
    latest_revision = Column(Integer)
    name = Column(String)
    fuller_name = Column(String)
    personal_name = Column(String)
    birth_date = Column(String)
    death_date = Column(String)
    date = Column(String)
    entity_type = Column(String)  # Combined entity_type and entiy_type
    bio = Column(Text)
    # lccn = Column(Integer) # CONVERT FROM STRING

    # assoc tables
    editions = relationship("Editions", secondary="editions_authors", back_populates="authors")
    works = relationship("Works", secondary="works_authors", back_populates="authors")
    # alternate_names = relationship("Alternate_Names", secondary="authors_alternate_names", back_populates="authors")
    # genres = relationship("Genres", secondary="authors_genres", back_populates="authors")
    # languages = relationship("Languages", secondary="authors_languages", back_populates="authors")
    locations = relationship("Places", secondary="authors_locations", back_populates="authors")
    # subjects = relationship("Subjects", secondary="authors_subjects", back_populates="authors")

authors_locations = Table('authors_locations', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('location_id', Integer, ForeignKey('places.id'))
)

# photos
class Author_Photos(Base):
    __tablename__ = 'authors_photos'
    id = Column(Integer, primary_key=True)
    photo = Column(Integer)
    author_id = Column(String, ForeignKey('authors.id'))
    author = relationship("Authors")

################# UNUSED ##################

# # alternate names
# class Alternate_Names(Base):
#     __tablename__ = 'alternate_names'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     authors = relationship("Authors", secondary="authors_alternate_names", back_populates="alternate_names")

# authors_alternate_names = Table('authors_alternate_names', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('author_id', String, ForeignKey('authors.id')),
#     Column('alternate_name_id', Integer, ForeignKey('alternate_names.id'))
# )

# authors_genres = Table('authors_genres', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('author_id', String, ForeignKey('authors.id')),
#     Column('genre_id', Integer, ForeignKey('genres.id'))
# )

# authors_languages = Table('authors_languages', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('author_id', String, ForeignKey('authors.id')),
#     Column('language_id', Integer, ForeignKey('languages.id'))
# )

# authors_subjects = Table('authors_subjects', Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('author_id', String, ForeignKey('authors.id')),
#     Column('subject_id', Integer, ForeignKey('subjects.id'))
# )


# ---------------- WORKS ----------------

class Works(Base):
    __tablename__ = 'works'
    id = Column(String, primary_key=True)
    created = Column(Date)
    last_modified = Column(Date)
    revision = Column(Integer)
    latest_revision = Column(Integer)
    title = Column(String)
    subtitle = Column(String)
    first_publish_date = Column(String)
    description = Column(Text)
    number_of_editions = Column(Integer)
    works2 = Column(String)

    # assoc tables
    editions = relationship("Editions", secondary="editions_works", back_populates="works")
    authors = relationship("Authors", secondary="works_authors", back_populates="works")
    cover_editions = relationship("Editions", secondary="works_cover_editions", back_populates="works")
    dewey_number = relationship("Dewey_Numbers", secondary="works_dewey_number", back_populates="works")
    lc_classifications = relationship("LC_Classifications", secondary="works_lc_class", back_populates="works")
    original_languages = relationship("Languages", secondary="works_original_languages", back_populates="works")
    other_titles = relationship("Other_Work_Titles", secondary="works_other_titles", back_populates="works")
    subjects = relationship("Subjects", secondary="works_subjects", back_populates="works")
    translated_titles = relationship("Translated_Titles", secondary="works_translated_titles", back_populates="works")

works_authors = Table('works_authors', Base.metadata,
    Column('author_id', String, ForeignKey('authors.id')),
    Column('work_id', String, ForeignKey('works.id'))
)

class Works_Covers(Base):
    __tablename__ = 'works_covers'
    # from works.covers
    id = Column(Integer, primary_key=True)
    cover = Column(Integer)
    work_id = Column(String, ForeignKey('works.id'))
    work = relationship("Works") # MAYBE??

cover_editions = Table('works_cover_editions', Base.metadata,
    # from works.cover_edition
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('edition_id', String, ForeignKey('editions.id'))
)

class Dewey_Numbers(Base):
    __tablename__ = 'dewey_numbers'
    id = Column(Integer, primary_key=True)
    dewey_number = Column(String)
    works = relationship("Works", secondary="works_dewey_number", back_populates="dewey_number")

works_dewey_number = Table('works_dewey_number', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('dewey_number_id', Integer, ForeignKey('dewey_numbers.id'))
)

works_lc_class = Table('works_lc_class', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('lc_classification_id', Integer, ForeignKey('lc_classifications.id'))
)

works_original_languages = Table('works_original_languages', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

class Other_Work_Titles(Base):
    # from works.other_titles
    __tablename__ = 'other_work_titles'
    id = Column(Integer, primary_key=True)
    other_title = Column(String)
    works = relationship("Works", secondary="works_other_titles", back_populates="other_titles")

works_other_titles = Table('works_other_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('other_work_title_id', Integer, ForeignKey('other_work_titles.id'))
)

works_subjects = Table('works_subjects', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

class Translated_Titles(Base):
    __tablename__ = 'translated_titles'
    id = Column(Integer, primary_key=True)
    translated_title = Column(String)
    language = Column(String)
    works = relationship("Works", secondary="works_translated_titles", back_populates="translated_titles")

works_translated_titles = Table('works_translated_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('translated_title_id', Integer, ForeignKey('translated_titles.id'))
)




if __name__ == '__main__':
    engine = create_engine(DB_URL)
            
    Session = sessionmaker(bind=engine)
    session = Session()

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, tables=[Base.metadata.tables['users'],
                                             Base.metadata.tables['user_followers'],
                                             Base.metadata.tables['likes'],
                                         Base.metadata.tables['reviews'],
                                         Base.metadata.tables['lists'],
                                         Base.metadata.tables['list_books']])
