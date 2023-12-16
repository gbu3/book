from sys import argv, stderr, exit
from sqlalchemy import create_engine, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from model.database import DB_URL, Base, User, Review, List, Editions
from model.books import get_edition_title_cover_authors

engine = create_engine(DB_URL)

DESCRIPTION_CHARACTER_LENGTH = 500

def list_to_dict(list):
    """
    convert a List to a dictionary to return
    detailed information for a list page
    """
    if not list:
        return None
    
    return {
        "list_id": list.list_id,
        "creator_id": list.creator_id,
        "creator_name": list.creator.username,
        "description": list.description,
        "title": list.title,
        "books": [get_edition_title_cover_authors(edition.id) for edition in list.books],
        "liked_by": [follower_to_dict(user) for user in list.liked_by]
    }

def user_list_to_dict(lst):
    """
    convert a List to a dict for display
    on user page - more minimal
    """
    return {
        "list_id": lst.list_id,
        "title": lst.title,
        "description": lst.description
    }

def follower_to_dict(user):
    """
    creates a very minimal dict for follower/following display
    """
    if not user:
        return None
    
    return {
        "user_id": user.user_id,
        "username": user.username
    }

def get_lists(user_name=None, list_name=None, user_id=None, list_id=None, book_id=None, limit=100):
    """
    get a list by its list_id, or
    search lists for a particular book and/or user
    (filters will be layered)
    default limit on results is 100
    """
    if all(arg is None for arg in [user_name, list_name, user_id, list_id, book_id]):
        return None
    
    try:
        if user_id:
            user_id = int(user_id)
        if user_name:
            if type(user_name) is not str:
                print("incorrect type for user_name")
                return None
        if list_id:
            list_id = int(list_id)
        if list_name:
            if type(list_name) is not str:
                print("incorrect type for list_name")
                return None
        if book_id:
            if type(book_id) is not str:
                print("incorrect type for book id")
                return None
    except ValueError:
        print("incorrect type for search parameters")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        query = session.query(List)

        # parameters are treated like filters

        if list_id:
            # if list_id is provided, ignore other filters (just need 1)
            query = query.filter(List.list_id == list_id)
        else:
            if user_name:
                query = query.join(List.creator)
                query = query.filter(User.username.ilike(f'%{user_name}%'))
                # query = query.filter(List.creator.username.ilike(f'%{user_name}%'))
            if list_name:
                query = query.filter(List.title.ilike(f'%{list_name}%'))
            if user_id:
                query = query.filter(List.creator_id == user_id)
            if book_id:
                query = query.filter(List.books.any(id=book_id))

        # limit results
        results = query.limit(limit).all()

        lists = [list_to_dict(list_obj) for list_obj in results]
        session.close()
        return lists
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_all_lists(limit=100):
    """
    gets all lists. for testing purposes, not exposed.
    default limit is 100
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        all_lists = session.query(List).limit(limit).all()

        return [list_to_dict(lst) for lst in all_lists]
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_list_info(list_id):
    """
    get an individual list by id.
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        lst = session.query(List).filter_by(list_id=list_id).first()

        return list_to_dict(lst)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def create_list(user_id, title=None, description=None):
    """
    creates a new list (of books). new lists are empty, and
    their default title is "Untitled."
    lists are identified by their title, so there can be
    no duplicate titles.
    """
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # check that the user exists
        user = session.query(User).filter(User.user_id==user_id).first()
        if not user:
            print("create list failed: incorrect user id")
            return None 

        # if list already exists
        if title:
            list = session.query(List).filter(List.creator_id==user_id, List.title==title).first()
            if list:
                print("a list with this title already exists")
                return None
        else:
            title = 'Untitled' + str(len(user.lists) + 1)
        
        new_list = List(
            creator_id = user_id,
            title = title
        )

        if description:
            if len(description) > DESCRIPTION_CHARACTER_LENGTH:
                new_list.description = description[:500]
            else:
                new_list.description = description
        
        session.add(new_list)
        session.commit()

        print(f"New list created: {new_list.list_id}")

        return list_to_dict(new_list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_list(user_id, list_id, title, description):
    try:
        user_id = int(user_id)
        list_id = int(list_id)
    except ValueError:
        print("incorrect type for user or list id")
        return None
    
    if not title and not description:
        print(f"No title or description provided")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        list = session.query(List).filter(List.list_id==list_id).first()
        if not list:
            print(f"No list found with the id {list_id}")
            return None

        # check that user is correct
        if user_id != list.creator_id:
            print(f"user {user_id} does not have permission to modify this list")
            return None
        
        if title:
            list.title = title
        if description:
            list.description = description

        session.commit()

        print(f"list {list_id} successfully updated")

        return list_to_dict(list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def add_list_book(user_id, list_id, book_id):
    try:
        user_id = int(user_id)
        list_id = int(list_id)
        if type(book_id) is not str:
            print("incorrect type for book id")
            return None
    except ValueError:
        print("incorrect type for user or list id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        list = session.query(List).filter(List.list_id==list_id).first()
        if not list:
            print(f"No list found with the id {list_id}")
            return None

        # check that user is correct
        if user_id != list.creator_id:
            print(f"user {user_id} does not have permission to modify this list")
            return None
        
        # get the book
        edition = session.query(Editions).filter(Editions.id==book_id).first()
        if not edition:
            print("add book failed: incorrect book id")
            return None
        
        if edition in list.books:
            print("book already in list")
            return None
        
        list.books.append(edition)

        session.commit()

        return list_to_dict(list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def remove_list_book(user_id, list_id, book_id):
    try:
        user_id = int(user_id)
        list_id = int(list_id)
        if type(book_id) is not str:
            print("incorrect type for book id")
            return None
    except ValueError:
        print("incorrect type for user or list id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        list = session.query(List).filter(List.list_id==list_id).first()
        if not list:
            print(f"No list found with the id {list_id}")
            return None

        # check that user is correct
        if user_id != list.creator_id:
            print(f"user {user_id} does not have permission to modify this list")
            return None
        
        # get the book
        edition = session.query(Editions).filter(Editions.id==book_id).first()
        if not edition or edition not in list.books:
            print("remove book failed: incorrect book id or book not in list")
            return None
        
        list.books.remove(edition)

        session.commit()

        return list_to_dict(list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def delete_list(list_id):
    if not list_id:
        print("no list id provided")
        return None
    
    try:
        list_id = int(list_id)
    except ValueError:
        print("incorrect type for list id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        list = session.query(List).filter(List.list_id==list_id).first()
        if list:
            session.delete(list)
            session.commit()
            print(f"List {list_id} deleted successfully.")
        else:
            print(f"No list found with the id {list_id}")

        return list_id
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()
