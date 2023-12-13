from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from model.database import DB_URL, Base, User, Review, List, Editions
from model.books import get_edition_title_cover_authors
from model.users import follower_to_dict

engine = create_engine(DB_URL)

DESCRIPTION_CHARACTER_LENGTH = 500

def _list_to_dict(list):
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

def get_lists(user_id=None, book_id=None, list_id=None, limit=100):
    """
    get a list by its list_id, or
    search lists for a particular book and/or user
    (filters will be layered)
    default limit on results is 100
    """
    if all(arg is None for arg in [user_id, book_id, list_id]):
        return None
    
    try:
        if user_id:
            user_id = int(user_id)
        if list_id:
            list_id = int(list_id)
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
            if user_id:
                query = query.filter(List.creator_id == user_id)
            if book_id:
                query = query.filter(List.books.any(id=book_id))

        # limit results
        results = query.limit(limit).all()

        lists = [_list_to_dict(list_obj) for list_obj in results]
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

        return _list_to_dict(new_list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_list_title(user_id, list_id, title):
    try:
        user_id = int(user_id)
        list_id = int(list_id)
    except ValueError:
        print("incorrect type for user or list id")
        return None
    
    if not title:
        print(f"No title provided")
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
        
        list.title = title

        session.commit()

        print(f"list {list_id} title successfully modified to {title}")

        return _list_to_dict(list)
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_list_description(user_id, list_id, description):
    try:
        user_id = int(user_id)
        list_id = int(list_id)
    except ValueError:
        print("incorrect type for user or list id")
        return None
    
    if not description:
        print(f"No description provided")
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
        
        list.description = description

        session.commit()

        print(f"list {list_id} description successfully modified to {description}")

        return _list_to_dict(list)
    
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

        return _list_to_dict(list)
    
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

        return _list_to_dict(list)
    
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
