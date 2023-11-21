from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ---------------- EDITIONS ----------------

class Editions(Base):
    __tablename__ = 'editions'
    id = Column(String, primary_key=True)
    created = Column(Date)
    copyright_date = Column(Date)
    subtitle = Column(String)
    revision = Column(Integer)
    title = Column(String)
    publish_date = Column(Date)
    description = Column(Text)
    last_modified = Column(Date)
    number_of_pages = Column(Integer)
    by_statement = Column(String)
    edition_name = Column(String)
    volume_number = Column(Integer)
    translation_of = Column(String)
    dewey_decimal_class = Column(String)
    title_prefix = Column(String)
    pagination = Column(String)
    full_title = Column(String)
    lccn = Column(Integer) # need to convert from string
    latest_revision = Column(Integer)

    # assoc tables
    authors = relationship("Authors", secondary="editions_authors")
    works = relationship("Works", secondary="editions_works")
    classifications = relationship("Classifications", secondary="editions_classifications")
    work_titles = relationship("Work_Titles", secondary="editions_works_titles")
    covers = relationship("Editions_Covers", backref="edition")
    publish_countries = relationship("Publish_Countries", secondary="editions_publish_countries")
    lc_classifications = relationship("LC_Classifications", secondary="editions_lc_class")
    contributors = relationship("Contributors", secondary="editions_contributors")
    languages = relationship("Languages", secondary="editions_languages")
    translated_from_languages = relationship("Languages", secondary="edition_translated_from_language")
    publishers = relationship("Publishers", secondary="editions_publishers")
    publish_places = relationship("Places", secondary="editions_publish_places")
    subjects = relationship("Subjects", secondary="editions_subjects")
    genres = relationship("Genres", secondary="editions_genres")
    notes = relationship("Notes", backref="edition")
    isbn_10 = relationship("ISBN_10", backref="edition")
    isbn_13 = relationship("ISBN_13", backref="edition")
    series = relationship("Series", secondary="editions_series")

class Classifications(Base):
    __tablename__ = 'classifications'
    id = Column(Integer, primary_key=True)
    classification = Column(String)
    editions = relationship("Editions", secondary="editions_classifications")

editions_classifications = Table('editions_classifications', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('classification_id', Integer, ForeignKey('classifications.id'))
)

class Work_Titles(Base):
    __tablename__ = 'work_titles'
    id = Column(Integer, primary_key=True)
    work_title = Column(String)
    editions = relationship("Editions", secondary="editions_work_titles")

editions_work_titles = Table('editions_work_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('work_title_id', Integer, ForeignKey('work_titles.id'))
)

class Editions_Covers(Base):
    __tablename__ = 'editions_covers'
    id = Column(Integer, primary_key=True)
    cover = Column(Integer)
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions") # MAYBE??

class Publish_Countries(Base):
    __tablename__ = 'publish_countries'
    id = Column(Integer, primary_key=True)
    publish_country = Column(String)
    editions = relationship("Editions", secondary="editions_publish_countries")

editions_publish_countries = Table('editions_publish_countries', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('publish_country_id', Integer, ForeignKey('publish_countries.id'))
)

class LC_Classifications(Base):
    # based on fields “lc_classifications” AND “lc_classification” 
    # and, from works, “lc_classifications”
    __tablename__ = 'lc_classifications'
    id = Column(Integer, primary_key=True)
    lc_classification = Column(String)
    editions = relationship("Editions", secondary="editions_lc_class")
    works = relationship("Works", secondary="works_lc_class")

editions_lc_class = Table('editions_lc_class', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('lc_classification_id', Integer, ForeignKey('lc_classifications.id'))
)

class Contributors(Base):
    # based on fields contributors and contributions
    __tablename__ = 'contributors'
    id = Column(Integer, primary_key=True)
    contributor = Column(String)
    editions = relationship("Editions", secondary="editions_contributors")

editions_contributors = Table('editions_contributors', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('contributor_id', Integer, ForeignKey('contributors.id'))
)

class Languages(Base):
    # based on languages in fields in 
    # editions: language, languages, translated_from; 
    # and authors->’languages’; 
    # and works->’original_languages’
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    language = Column(String)
    editions = relationship("Editions", secondary="editions_languages")
    authors = relationship("Authors", secondary="authors_languages")
    works = relationship("Works", secondary="works_original_languages")

editions_languages = Table('editions_languages', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

edition_translated_from_language = Table('editions_languages', Base.metadata,
    # from "translated_from"
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

class Publishers(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    publisher = Column(String)
    editions = relationship("Editions", secondary="editions_publishers")

editions_publishers = Table('editions_publishers', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('publisher_id', Integer, ForeignKey('publishers.id'))
)

class Places(Base):
    # from editions->publish_places and authors->location
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    place = Column(String)
    editions = relationship("Editions", secondary="editions_publish_places")
    authors = relationship("Authors", secondary="authors_locations")

editions_publish_places = Table('editions_publish_places', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('place_id', Integer, ForeignKey('places.id'))
)

class Subjects(Base):
    # from editions, authors, and works
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    subject = Column(String)
    editions = relationship("Editions", secondary="editions_subjects")
    authors = relationship("Authors", secondary="authors_subjects")
    works = relationship("Works", secondary="works_subjects")

editions_subjects = Table('editions_subjects', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

class Genres(Base):
    # from editions and authors
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    genre = Column(String)
    editions = relationship("Editions", secondary="editions_genres")
    authors = relationship("Authors", secondary="authors_genres")

editions_genres = Table('editions_genres', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Notes(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    note = Column(String)
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions") # MAYBE??

class ISBN_10(Base):
    __tablename__ = 'isbn_10'
    id = Column(Integer, primary_key=True)
    isbn_10 = Column(Integer) # CONVERT FROM STRING
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions") # MAYBE??

class ISBN_13(Base):
    __tablename__ = 'isbn_13'
    id = Column(Integer, primary_key=True)
    isbn_10 = Column(Integer) # CONVERT FROM STRING
    edition_id = Column(String, ForeignKey('editions.id'))
    edition = relationship("Editions") # MAYBE??

class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    series = Column(String)
    editions = relationship("Editions", secondary="editions_series")

editions_series = Table('editions_series', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('series_id', Integer, ForeignKey('series.id'))
)

editions_authors = Table('editions_authors', Base.metadata,
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('author_id', String, ForeignKey('authors.id'))
)

editions_works = Table('editions_works', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('edition_id', String, ForeignKey('editions.id')),
    Column('work_id', String, ForeignKey('works.id'))
)

# ---------------- AUTHORS ----------------

class Authors(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    created = Column(Date)
    fuller_name = Column(String)
    name = Column(String)
    entity_type = Column(String)  # Combined entity_type and entiy_type
    last_modified = Column(Date)
    lccn = Column(Integer) # CONVERT FROM STRING
    date = Column(String)
    latest_revision = Column(Date)
    revision = Column(Integer)
    personal_name = Column(String)
    birth_date = Column(String)
    death_date = Column(String)
    bio = Column(Text)

    # assoc tables
    editions = relationship("Editions", secondary="editions_works")
    works = relationship("Works", secondary="authors_works")
    locations = relationship("Places", secondary="authors_locations")
    subjects = relationship("Subjects", secondary="authors_subjects")
    languages = relationship("Languages", secondary="authors_languages")
    genres = relationship("Genres", secondary="authors_genres")
    alternate_names = relationship("Alternate_Names", secondary="authors_alternate_names")
    photos = relationship("Author_Photos", backref="author")

# Association tables for Authors
authors_locations = Table('authors_locations', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('place_id', Integer, ForeignKey('places.id'))
)

authors_subjects = Table('authors_subjects', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

authors_languages = Table('authors_languages', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

authors_genres = Table('authors_genres', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Alternate_Names(Base):
    __tablename__ = 'alternate_names'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    authors = relationship("Authors", secondary="authors_alternate_names")

authors_alternate_names = Table('authors_alternate_names', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', String, ForeignKey('authors.id')),
    Column('alternate_name_id', Integer, ForeignKey('alternate_names.id'))
)

class Author_Photos(Base):
    __tablename__ = 'author_photos'
    id = Column(Integer, primary_key=True)
    photo = Column(Integer)
    author_id = Column(String, ForeignKey('authors.id'))
    author = relationship("Authors") # MAYBE??

authors_works = Table('authors_works', Base.metadata,
    Column('author_id', String, ForeignKey('authors.id')),
    Column('work_id', String, ForeignKey('works.id'))
)

# ---------------- WORKS ----------------

class Works(Base):
    __tablename__ = 'works'
    id = Column(String, primary_key=True)
    created = Column(Date)
    last_modified = Column(Date)
    latest_revision = Column(Integer)
    subtitle = Column(String)
    revision = Column(Integer)
    dewey_number = Column(String)
    title = Column(String)
    description = Column(Text)
    number_of_editions = Column(Integer)
    first_publish_date = Column(Date)
    works2 = Column(String)

    # assoc tables
    editions = relationship("Editions", secondary="editions_works")
    authors = relationship("Authors", secondary="authors_works")
    original_languages = relationship("Languages", secondary="works_original_languages")
    lc_classifications = relationship("LC_Classifications", secondary="works_lc_class")
    subjects = relationship("Subjects", secondary="works_subjects")
    other_titles = relationship("Other_Work_Titles", secondary="works_other_titles")
    translated_titles = relationship("Translated_Titles", secondary="works_translated_titles")
    covers = relationship("Works_Covers", backref="work")
    cover_editions = relationship("Editions", secondary="works_cover_editions")

works_original_languages = Table('works_original_languages', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('language_id', Integer, ForeignKey('languages.id'))
)

works_lc_class = Table('works_lc_class', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('lc_classification_id', Integer, ForeignKey('lc_classifications.id'))
)

works_subjects = Table('works_subjects', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

class Other_Work_Titles(Base):
    # from works.other_titles
    __tablename__ = 'other_work_titles'
    id = Column(Integer, primary_key=True)
    other_title = Column(String)
    works = relationship("Works", secondary="works_other_titles")

works_other_titles = Table('works_other_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('other_work_title_id', Integer, ForeignKey('other_work_titles.id'))
)

class Translated_Titles(Base):
    __tablename__ = 'translated_titles'
    id = Column(Integer, primary_key=True)
    translated_title = Column(String)
    works = relationship("Works", secondary="works_translated_titles")

works_translated_titles = Table('works_translated_titles', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('work_id', String, ForeignKey('works.id')),
    Column('translated_title_id', Integer, ForeignKey('translated_titles.id'))
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

