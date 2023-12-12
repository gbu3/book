from sys import argv, stderr, exit
from sqlalchemy import create_engine, or_, and_, func
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from model.database import DB_URL, Base, User, Review, List, Editions, editions_authors, editions_works, Authors, editions_genres, editions_subjects, Places, editions_publish_places, authors_locations, Author_Photos, Publishers, editions_publishers, Editions_Covers, Subjects, Genres, Works, DB_URL

"""
This module provides a set of functions to search a database of books.
There are two levels of granularity that can be accomplished; 
 - One for general search results, which returns: 
    - edition_id
    - title
    - author
    - place of publication
    - publisher name
    - publication date
    - cover integer for edition 
 - Another for more detailed information about a given book:
    - edition_id
    - title
    - author
    - place of publication
    - publisher name
    - publication date
    - edition name (if any)
    - volume number (if any)
    - description
    - cover integer for edition 
    - reviews
    - ratings (averaged)

So, the return body (dict) will either be top-level edition information:
simple_edition = {
    'edition_id',
    'title',
    'author',
    'publication_place',
    'publisher',
    'publish_date',
    'edition_cover'
}
or more detailed information for each edition:
edition_details = {
    'edition_id',
    'title',
    'author',
    'publication_place',
    'publisher',
    'publish_date',
    'edition_name',
    'volume_number',
    'description',
    'genres',
    'subjects',
    'edition_cover',
    'reviews',
    'average_rating'
}

FUNCTIONS
    search_books(edition_id, work_id, author_name, author_id,
                 title, keyword, language, start_year, end_year, limit):
        returns 
"""

engine = create_engine(DB_URL)

REVIEW_LIMIT = 10

def search_books(edition_id=None, work_id=None, author_name=None, 
                 author_id=None, title=None, keyword=None, language=None, 
                 start_year=None, end_year=None, limit=100): 
    """
    search by:
    - title
    - author: name or author id
    - work id or edition id
    OR a combination of these.
    FILTERS (advanced search) - STRETCH, not curr implemented
    - language
    - year (range)
    limit # results by limit. default 100
    """
    if all(arg is None for arg in [edition_id, work_id, author_name, author_id, 
                                   title, keyword, language, start_year, end_year]):
        return None

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(Editions)

        if edition_id:
            query = query.filter(Editions.id == edition_id)

        if work_id:
            query = query.filter(Editions.works.any(id=work_id))

        if author_name or author_id:
            # handle multiple filters
            AuthorAlias = aliased(Authors)
            query = query.join(AuthorAlias, Editions.authors)

            if author_name:
                query = query.filter(AuthorAlias.name.ilike(f'%{author_name}%'))

            if author_id:
                query = query.filter(AuthorAlias.id == author_id)

        if title:
            query = query.filter(Editions.title.ilike(f'%{title}%'))

        query = query.limit(limit).options(
            joinedload(Editions.authors),
            joinedload(Editions.publish_places),
            joinedload(Editions.publishers),
            joinedload(Editions.editions_covers)
        )

        query = query.limit(limit)

        results = query.all()
        books = [_edition_to_dict(edition) for edition in results]
        session.close()

        return books

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

########## smaller search APIs, may be slightly more efficient #############

def search_by_title(title, limit=100):
    """
    search book by title
    """
    if not title:
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.query(Editions)\
                        .filter(Editions.title.ilike(f'%{title}%'))\
                        .options(
                            joinedload(Editions.authors),
                            joinedload(Editions.publish_places),
                            joinedload(Editions.publishers),
                            joinedload(Editions.editions_covers)
                        ) \
                        .limit(limit)\
                        .all()

        books = [_edition_to_dict(edition) for edition in results]

        return books

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()


def search_by_author(author_name, limit=100):
    """
    find books by author name
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.query(Editions)\
                        .join(editions_authors, Editions.id == editions_authors.c.edition_id)\
                        .join(Authors, editions_authors.c.author_id == Authors.id)\
                        .options(joinedload(Editions.authors), 
                                                joinedload(Editions.publish_places), 
                                                joinedload(Editions.publishers), 
                                                joinedload(Editions.editions_covers))\
                        .filter(Authors.name.ilike(f'%{author_name}%'))\
                        .distinct()\
                        .all()

        books = [_edition_to_dict(edition) for edition in results]

        return books

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def search_by_work(work_id, limit=100):
    """
    search books by work_id
    """
    if not work_id:
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.query(Editions)\
                        .join(editions_works, Editions.id == editions_works.c.edition_id)\
                        .filter(editions_works.c.work_id == work_id)\
                        .options(
                            joinedload(Editions.authors),
                            joinedload(Editions.publish_places),
                            joinedload(Editions.publishers),
                            joinedload(Editions.editions_covers)
                        ) \
                        .limit(limit)\
                        .all()

        books = [_edition_to_dict(edition) for edition in results]

        return books

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

# def search_by_keyword(keyword, limit=100):
#     """
#     Search books by a keyword that can be in title or author's name.
#     Split the keyword into words and match each word against title and author.
#     """
#     if not keyword:
#         return []

#     try:
#         Session = sessionmaker(bind=engine)
#         session = Session()

#         results = session.query(Editions)\
#                         .join(editions_authors, Editions.id == editions_authors.c.edition_id)\
#                         .join(Authors, editions_authors.c.author_id == Authors.id)\
#                         .filter(or_(
#                                 Editions.title.ilike(f'%{keyword}%'),
#                                 Authors.name.ilike(f'%{keyword}%'),
#                                 Editions.subjects.any(Subjects.subject.ilike(f'%{keyword}%')),
#                                 Editions.genres.any(Genres.genre.ilike(f'%{keyword}%'))
#                         ))\
#                         .options(
#                             joinedload(Editions.authors),
#                             joinedload(Editions.publish_places),
#                             joinedload(Editions.publishers),
#                             joinedload(Editions.editions_covers)
#                         ) \
#                         .limit(limit)\
#                         .all()

#         books = [_edition_to_dict(edition) for edition in results]

#         session.close()
#         return books

#     except Exception as ex:
#         print(ex, file=stderr)
#         exit(1)
#     finally:
#         session.close()


def get_book(book_id):
    """
    get book details by its id
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Build the query
        book = session.query(Editions)\
                        .filter_by(id=book_id)\
                        .first()

        return _edition_details_dict(book)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()


def get_author_books(author_id, limit=100):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        editions = session.query(Editions)\
                        .join(editions_authors, Editions.id == editions_authors.c.edition_id)\
                        .options(joinedload(Editions.authors), 
                                                joinedload(Editions.publish_places), 
                                                joinedload(Editions.publishers), 
                                                joinedload(Editions.editions_covers))\
                        .filter(editions_authors.c.author_id == author_id)\
                        .distinct()\
                        .all()

        books = [_edition_to_dict(edition) for edition in editions]

        return books

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def _author_to_dict(author):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
    
        locations = session.query(Places.place)\
                        .join(authors_locations, Places.id == authors_locations.c.location_id)\
                        .filter(authors_locations.c.author_id == author.id)\
                        .distinct()\
                        .all()

        photo = session.query(Author_Photos.photo)\
                        .filter(Author_Photos.author_id == author.id)\
                        .first()
        
        return {
            "author_id": author.id,
            "name": author.name,
            "fuller_name": author.fuller_name,
            "personal_name": author.personal_name,
            "birth_date": author.birth_date,
            "death_date": author.death_date,
            "entity_type": author.entity_type,
            "bio": author.bio,
            "locations": [item[0] for item in locations],
            "author_photo": photo[0] if photo else None
        }
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def search_author(author_name=None, author_id=None, limit=100):
    if not author_id and not author_name:
        return None
    
    if author_id:
        return get_author(author_id)
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        results = session.query(Authors)\
                        .filter(or_(
                            Authors.name.ilike(f'%{author_name}%'),
                            Authors.fuller_name.ilike(f'%{author_name}%'),
                            Authors.personal_name.ilike(f'%{author_name}%'),
                            ))\
                        .limit(limit)\
                        .all()

        authors = [_author_to_dict(author) for author in results]

        return authors

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def get_author(author_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        author = session.query(Authors)\
                        .filter_by(id=author_id)\
                        .first()

        return _author_to_dict(author)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

# def create_book(cover_image, rating, book_data):
#     pass

# def update_book(book_id, cover_image, rating, book_data):
#     pass

# def delete_book(book_id):
#     pass


def _edition_to_dict(edition):
    return {
        'edition_id': edition.id,
        'title': edition.title,
        'author': [(author.name, author.id) for author in edition.authors],
        'publication_place': [place.place for place in edition.publish_places],
        'publisher': [publisher.publisher for publisher in edition.publishers],
        'publish_date': edition.publish_date,
        'edition_cover': edition.editions_covers[0].cover if edition.editions_covers else None
    }

def _edition_details_dict(edition):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        authors_names_ids = session.query(Authors.name, Authors.id)\
                                    .join(editions_authors, Authors.id == editions_authors.c.author_id)\
                                    .filter(editions_authors.c.edition_id == edition.id)\
                                    .distinct()\
                                    .all()

        places = session.query(Places.place)\
                        .join(editions_publish_places, Places.id == editions_publish_places.c.place_id)\
                        .filter(editions_publish_places.c.edition_id == edition.id)\
                        .distinct()\
                        .all()

        publishers = session.query(Publishers.publisher)\
                            .join(editions_publishers, Publishers.id == editions_publishers.c.publisher_id)\
                            .filter(editions_publishers.c.edition_id == edition.id)\
                            .all()
        
        genres = session.query(Genres.genre)\
                        .join(editions_genres, Genres.id == editions_genres.c.genre_id)\
                        .filter(editions_genres.c.edition_id == edition.id)\
                        .all()
        
        subjects = session.query(Subjects.subject)\
                            .join(editions_subjects, Subjects.id == editions_subjects.c.subject_id)\
                            .filter(editions_subjects.c.edition_id == edition.id)\
                            .all()

        cover = session.query(Editions_Covers.cover)\
                        .filter(Editions_Covers.edition_id == edition.id)\
                        .first()
        
        reviews = session.query(Review.summary, Review.note)\
                         .filter(Review.book_id == edition.id)\
                         .limit(REVIEW_LIMIT)\
                         .all()

        average_rating = session.query(func.avg(Review.rating))\
                                .filter(Review.book_id == edition.id)\
                                .scalar()
        
        return {
            'edition_id': edition.id,
            'title': edition.title,
            'author': authors_names_ids,
            'publication_place': [item[0] for item in places],
            'publisher': [item[0] for item in publishers],
            'publish_date': edition.publish_date,
            'edition_name': edition.edition_name,
            'volume_number': edition.volume_number,
            'description': edition.description,
            'genres': [item[0] for item in genres],
            'subjects': [item[0] for item in subjects],
            'edition_cover': cover[0] if cover else None,
            'reviews': reviews,
            'average_rating': average_rating
        }

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()
