from sys import argv, stderr, exit
from sqlalchemy import create_engine, or_, and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from model.database import DB_URL, Base, User, Review, List, Editions, editions_authors, editions_works, Authors, editions_genres, editions_subjects, Places, editions_publish_places, authors_locations, Author_Photos, Publishers, editions_publishers, Editions_Covers, Subjects, Genres, Works, DB_URL

"""
This module provides a set of functions to search a database of books
for editions and authors. The data is sourced from Open Library's data dumps.

There are two levels of granularity that can be accomplished for editions:
 - One for general search results, which returns a dict with
   top-level information about the edition: 
        simple_edition = {
            'edition_id': string, edition id,
            'title': string, title of the edition,
            'authors': list of tuples, in the form ('author.name', 'author.id'),
            'publication_place': list of strings, place(s) of publication,
            'publisher': list of strings, publisher(s) of the edition,
            'publish_date': string, publication date,
            'edition_cover': integer, cover_id for the edition (OL reference)
        }
 - Another for more detailed information about a given edition:
        edition_details = {
            'edition_id': string, edition id,
            'title': string, title of the edition,
            'authors': list of tuples, in the form ('author.name', 'author.id'),
            'publication_place': list of strings, place(s) of publication,
            'publisher': list of strings, publisher(s) of the edition,
            'publish_date': string, publication date,
            'edition_name': string, if any,
            'volume_number': integer, if any,
            'description': text (string), description of the edition,
            'genres': list of strings, genres of the edition,
            'subjects': list of strings, subjects of the edition,
            'edition_cover': integer, cover_id for the edition (OL reference),
            'reviews': Review objects, the top 10 (or some standard limit) user reviews of the edition,
            'average_rating': float, average of all user reviews of the edition
        }

For authors, one can search for specific authors or get a specific author. 
They will be returned in such a dict:
    author_details = {
        'author_id': string, author id,
        'name': string, author name,
        'fuller_name': string, author's fuller name (usually empty),
        'personal_name': string, author's personal name (usually same as name),
        'birth_date': string, author's birth date,
        'death_date': string, author's death date,
        'bio': string, biography of author,
        'locations': list of strings, places (cities, countries) the author is associated with,
        'author_photo': integer, photo_id for the author (OL reference)
    }

FUNCTIONS
    ** largest search API: layers filters on top of each other **
    search_editions(edition_id, work_id, author_name, author_id, 
                    title, publisher_name, publish_date, limit):
        returns [simple_editions]
    
    ** smaller search APIs, based on specific inputs **
    search_by_title(title, limit):
        returns [simple_editions]
    search_by_author(author_id, author_name, limit):
        returns [simple_editions]
    search_by_work(work_id, limit):
        returns [simple_editions]
    
    ** get edition details **
    get_edition_info(edition):
        returns edition_details
    get_edition_title_cover_authors(edition_id)
        returns edition_title_cover_authors_dict = {
            "edition_id": edition.id,
            "title": string,
            "cover": integer,
            "authors": string
        }
    
    ** authors: search author and get **
    search_author(author_name, author_id, limit):
        returns author_details
    get_author_info(author_id):
        returns author_details

    ** get reviews and lists by edition_id **
    get_reviews(edition_id, limit)
        returns review_dict {
            "review_id": integer, review.review_id,
            "reviewer_id": integer, user.user_id,
            "reviewer_username": string, user.username,
            "book_id": string,
            "book_name": string,
            "book_cover": integer,
            "book_authors": string,
            "summary": string,
            "rating": integer 1 to 10
        }
    get_lists(edition_id, limit)
        returns list_dict {
            "list_id": integer, list.list_id,
            "creator_id": integer, user.user_id,
            "creator_name": string, user.username,
            "description": string,
            "title": string,
            "books": list of edition_title_cover_authors_dicts,
            "liked_by": list of user.follower_dicts
        }
    
"""

engine = create_engine(DB_URL)

REVIEW_LIMIT = 10

def search_editions(edition_id=None, work_id=None, author_name=None, 
                 author_id=None, title=None, publisher_name=None,
                 publish_date=None, limit=100): 
    """
    search by:
    - title
    - author: name, fuller_name, personal_name, or author id
    - work id 
    - edition id
    search will be filtered by a combination of the given parameters
    default limit is 100
    """
    if all(arg is None for arg in [edition_id, work_id, author_name, author_id, title]):
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
                query = query.filter(or_(AuthorAlias.name.ilike(f'%{author_name}%'),
                                         AuthorAlias.fuller_name.ilike(f'%{author_name}%'),
                                         AuthorAlias.personal_name.ilike(f'%{author_name}%')))

            if author_id:
                query = query.filter(AuthorAlias.id == author_id)

        if title:
            query = query.filter(Editions.title.ilike(f'%{title}%'))

        if publish_date:
            query = query.filter(Editions.publish_date.ilike(f'%{publish_date}%'))

        if publisher_name:
            PublisherAlias = aliased(Publishers)
            query = query.join(PublisherAlias, Editions.publishers).filter(PublisherAlias.publisher.ilike(f'%{publisher_name}%'))


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

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

########## smaller search APIs, may be slightly more efficient #############

def search_by_title(title, limit=100):
    """
    search edition by title
    default limit is 100
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

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def search_by_author(author_id=None, author_name=None, limit=100):
    """
    find books by author id XOR name (faster to do by id)
    if given both parameters, will prioritize author_id (more specific)
    default limit is 100
    """
    if not author_name and not author_id:
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        if author_id:
            results = session.query(Editions)\
                        .join(editions_authors, Editions.id == editions_authors.c.edition_id)\
                        .options(joinedload(Editions.authors), 
                                                joinedload(Editions.publish_places), 
                                                joinedload(Editions.publishers), 
                                                joinedload(Editions.editions_covers))\
                        .filter(editions_authors.c.author_id == author_id)\
                        .distinct()\
                        .limit(limit)\
                        .all()
            
        else: # author_name
            results = session.query(Editions)\
                            .join(editions_authors, Editions.id == editions_authors.c.edition_id)\
                            .join(Authors, editions_authors.c.author_id == Authors.id)\
                            .options(joinedload(Editions.authors), 
                                                    joinedload(Editions.publish_places), 
                                                    joinedload(Editions.publishers), 
                                                    joinedload(Editions.editions_covers))\
                            .filter(or_(Authors.name.ilike(f'%{author_name}%'),
                                        Authors.fuller_name.ilike(f'%{author_name}%'),
                                        Authors.personal_name.ilike(f'%{author_name}%')))\
                            .distinct()\
                            .limit(limit)\
                            .all()

        books = [_edition_to_dict(edition) for edition in results]

        return books

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def search_by_work(work_id, limit=100):
    """
    search editions by work_id 
    (many-to-one relationship for editions to works)
    default limit is 100
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

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_edition_info(edition_id):
    """
    get book details by an edition_id
    returns an edition_details dict
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        edition = session.query(Editions)\
                        .filter_by(id=edition_id)\
                        .first()

        if not edition:
            print(f"Edition {edition_id} not found")
            return None

        return _edition_details_dict(edition)

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_edition_title_cover_authors(edition_id):
    """
    for use by reviews module: get all the basic information
    about a book, title and cover, to store
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        edition = session.query(Editions)\
                        .filter_by(id=edition_id)\
                        .first()
        
        if not edition:
            print(f"Edition {edition_id} not found")
            return None
        
        cover = session.query(Editions_Covers.cover)\
                        .filter(Editions_Covers.edition_id == edition.id)\
                        .first()
        
        authors_names = session.query(Authors.name)\
                                .join(editions_authors, Authors.id == editions_authors.c.author_id)\
                                .filter(editions_authors.c.edition_id == edition.id)\
                                .distinct()\
                                .all()

        return {
            "edition_id": edition.id,
            "title": edition.title,
            "cover": cover[0] if cover else None,
            "authors": ', '.join(t[0] for t in authors_names)
        }

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()


def search_author(author_name=None, author_id=None, limit=100):
    """
    search author details by name, fuller_name, personal_name,
    or author_id
    returns a list of author_details dicts
    limit is default 100
    """
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

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_author_info(author_id):
    """
    get individual author details by id
    returns an author_details dict
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        author = session.query(Authors)\
                        .filter_by(id=author_id)\
                        .first()

        return _author_to_dict(author)

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

# def create_book(cover_image, rating, book_data):
#     pass

# def update_book(book_id, cover_image, rating, book_data):
#     pass

# def delete_book(book_id):
#     pass

def _edition_to_dict(edition):
    """
    helper function for creating a simple_edition dict
    given an edition
    """
    return {
        'edition_id': edition.id,
        'title': edition.title,
        'authors': [(author.name, author.id) for author in edition.authors],
        'publication_place': [place.place for place in edition.publish_places],
        'publisher': [publisher.publisher for publisher in edition.publishers],
        'publish_date': edition.publish_date,
        'edition_cover': edition.editions_covers[0].cover if edition.editions_covers else None
    }

def _edition_details_dict(edition):
    """
    helper function for creating an edition_details dict
    given an edition
    """
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
        
        reviews_results = session.query(Review)\
                                .filter(Review.book_id == edition.id)\
                                .limit(REVIEW_LIMIT)\
                                .all()

        average_rating = session.query(func.avg(Review.rating))\
                                .filter(Review.book_id == edition.id)\
                                .scalar()
        
        if average_rating is not None:
            average_rating = float(f"{average_rating:.2f}")
        
        return {
            'edition_id': edition.id,
            'title': edition.title,
            'authors': authors_names_ids,
            'publication_place': [item[0] for item in places],
            'publisher': [item[0] for item in publishers],
            'publish_date': edition.publish_date,
            'edition_name': edition.edition_name,
            'volume_number': edition.volume_number,
            'description': edition.description,
            'genres': [item[0] for item in genres],
            'subjects': [item[0] for item in subjects],
            'edition_cover': cover[0] if cover else None,
            'reviews': [_review_to_dict_books(review) for review in reviews_results],
            'average_rating': average_rating
        }

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def _review_to_dict_books(review):
    """
    convert a Review to a dictionary to return
    minimal information for a book page
    """
    if not review:
        return None
    
    return {
        "review_id": review.review_id,
        "reviewer_id": review.reviewer_id,
        "reviewer_username": review.reviewer.username if review.reviewer else None,
        "summary": review.summary,
        "rating": review.rating
    }

def _author_to_dict(author):
    """
    helper function for creating an author_details dict
    given an author
    """
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
            "bio": author.bio,
            "locations": [item[0] for item in locations],
            "author_photo": photo[0] if photo else None
        }
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

##### GET REVIEWS OR LISTS FOR A PARTICULAR BOOK #####

# def get_reviews(edition_id, limit=100):
#     """
#     get reviews by edition id. default result limit is 100
#     """
#     if not edition_id:
#         print("book id not provided")
#         return None
#     if type(edition_id) is not str:
#         print("incorrect type for book id")
#         return None

#     try:
#         Session = sessionmaker(bind=engine)
#         session = Session()

#         reviews = session.query(Review).filter(Review.book_id==edition_id)\
#                                         .limit(limit)\
#                                         .all()

#         return [review_to_dict(review) for review in reviews]
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         print(f"Database error: {e}")
#         return None
#     except Exception as ex:
#         print(f"Error: {ex}")
#         return None
#     finally:
#         session.close()

# def get_lists(edition_id, limit=100):
#     """
#     get lists by edition id. default result limit is 100
#     """
#     if not edition_id:
#         print("book id not provided")
#         return None
#     if type(edition_id) is not str:
#         print("incorrect type for book id")
#         return None

#     try:
#         Session = sessionmaker(bind=engine)
#         session = Session()

#         lists = session.query(List).filter(List.books.any(id=edition_id))\
#                                     .limit(limit)\
#                                     .all()

#         return [list_to_dict(lst) for lst in lists]
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         print(f"Database error: {e}")
#         return None
#     except Exception as ex:
#         print(f"Error: {ex}")
#         return None
#     finally:
#         session.close()
