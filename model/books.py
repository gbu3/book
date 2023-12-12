from sys import argv, stderr, exit
from sqlalchemy import create_engine, or_, and_, func
from sqlalchemy.orm import sessionmaker, joinedload
from model.database import DB_URL, Base, User, Review, List, Editions, editions_authors, editions_works, Authors, Places, editions_publish_places, authors_locations, Author_Photos, Publishers, editions_publishers, Editions_Covers, Subjects, Genres, Works, DB_URL

engine = create_engine(DB_URL)

REVIEW_LIMIT = 10

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
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        authors_names = session.query(Authors.name)\
                        .join(editions_authors, Authors.id == editions_authors.c.author_id)\
                        .filter(editions_authors.c.edition_id == edition.id)\
                        .distinct()\
                        .all()
        
        print(authors_names)

        places = session.query(Places.place)\
                        .join(editions_publish_places, Places.id == editions_publish_places.c.place_id)\
                        .filter(editions_publish_places.c.edition_id == edition.id)\
                        .distinct()\
                        .all()
        
        print(places)

        publishers = session.query(Publishers.publisher)\
                            .join(editions_publishers, Publishers.id == editions_publishers.c.publisher_id)\
                            .filter(editions_publishers.c.edition_id == edition.id)\
                            .all()
        
        print(publishers)

        cover = session.query(Editions_Covers.cover)\
                        .filter(Editions_Covers.edition_id == edition.id)\
                        .first()
        
        return {
            'edition_id': edition.id,
            'title': edition.title,
            'author': authors_names,
            'publication_place': places,
            'publisher': [publisher.publisher for publisher in edition.publishers],
            'publish_date': edition.publish_date,
            'edition_cover': cover
        }

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def _edition_details_dict(edition):
    # return {
    #     'edition_id': edition.id,
    #     'title': edition.title,
    #     'author': [author.name for author in edition.authors],
    #     'publication_place': [place.place for place in edition.publish_places],
    #     'publisher': [publisher.publisher for publisher in edition.publishers],
    #     'publish_date': edition.publish_date,
    #     'edition_cover': edition.editions_covers[0].cover if edition.editions_covers else None
    # }
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
            'edition_cover': cover[0] if cover else None,
            'reviews': reviews,
            'average_rating': average_rating
        }

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def search_books(edition_id=None, work_id=None, author_name=None, 
                 author_id=None, title=None, keyword=None, language=None, 
                 start_year=None, end_year=None, limit=100): 
    """
    search by:
    - work id or edition id
    - author: name or author id
    - title
    - keyword (includes title, author name, subject, genre)
    FILTERS (advanced search)
    - language
    - year (range)
    limit # results by limit. default 1000

    this is too slow because it's doing too many table joins
    """
    if all(arg is None for arg in [edition_id, work_id, author_name, author_id, 
                                   title, keyword, language, start_year, end_year]):
        return None

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(Editions).options(joinedload(Editions.authors), 
                                                joinedload(Editions.publish_places), 
                                                joinedload(Editions.publishers), 
                                                joinedload(Editions.editions_covers))
        
        if edition_id:
            query = query.filter(Editions.id == edition_id)

        if work_id:
            query = query.filter(Editions.works.any(id=work_id))

        if author_name or author_id:
            query = query.join(Editions.authors)
            if author_name:
                query = query.filter(Authors.name.ilike(f'%{author_name}%'))
            if author_id:
                query = query.filter(Authors.id == author_id)

        if title:
            query = query.filter(Editions.title.ilike(f'%{title}%'))

        if keyword:
            query = query.join(Editions.publish_places).join(Editions.publishers)
            query = query.filter(or_(
                Editions.title.ilike(f'%{keyword}%'),
                Authors.name.ilike(f'%{keyword}%'),
                Editions.subjects.any(Subjects.subject.ilike(f'%{keyword}%')),
                Editions.genres.any(Genres.genre.ilike(f'%{keyword}%'))
            ))

        query = query.limit(limit)
        print(query)

        results = query.all()

        search_results = []
        for edition in results:
            # PYTHON solution, but might not work. move the rest up
            # if author_name and not any(author_name in author.name for author in edition.authors):
            #     continue
            # if author_id and not any(author_id == author.id for author in edition.authors):
            #     continue
            # if title and title not in edition.title:
            #     continue
            # if keyword and not any(keyword in field for field in [edition.title, 
            #                                                       ', '.join(author.name for author in edition.authors)]):
            #     continue
            if language and not any(language == lang.language for lang in edition.languages):
                continue
            if start_year and end_year and not (start_year <= edition.publish_date <= end_year):
                continue

            search_results.append(_edition_to_dict(edition))

        session.close()
        return search_results

        query = session.query(
            Editions.id.label('edition_id'),
            Editions.title,
            Editions.publish_date,
            Editions_Covers.cover.label('edition_cover')
        ).outerjoin(Editions_Covers, Editions.id == Editions_Covers.edition_id)

        if edition_id:
            query = query.filter(Editions.id == edition_id)

        if work_id:
            query = query.join(Editions.works).filter(Works.id == work_id)

        if author_name or author_id:
            query = query.join(Editions.authors)
            if author_name:
                query = query.filter(Authors.name.ilike(f'%{author_name}%'))
            if author_id:
                query = query.filter(Authors.id == author_id)

        if title:
            query = query.filter(Editions.title.ilike(f'%{title}%'))

        if keyword:
            query = query.join(Editions.publish_places).join(Editions.publishers)
            query = query.filter(or_(
                Editions.title.ilike(f'%{keyword}%'),
                Authors.name.ilike(f'%{keyword}%'),
                Editions.subjects.any(Subjects.subject.ilike(f'%{keyword}%')),
                Editions.genres.any(Genres.genre.ilike(f'%{keyword}%'))
            ))

        if language:
            query = query.join(Editions.languages).filter(Languages.language == language)

        if start_year and end_year:
            query = query.filter(Editions.publish_date.between(start_year, end_year))

        query = query.limit(limit)

        print(query)

        results = query.all()
        search_results = []
        
        for result in results:
            search_results.append(_edition_to_dict(result))

        session.close()
        return search_results

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
