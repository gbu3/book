from sys import argv, stderr, exit
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from model.database import Base, User, Review, List, user_follower_association, DB_URL
from model.reviews import user_review_to_dict
from model.lists import user_list_to_dict
import re

engine = create_engine(DB_URL)

def _user_to_dict(user):
    """
    convert a User to a dictionary to return
    """
    if not user:
        return None

    return {
        "user_id": user.user_id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        # "metadata_info": user.metadata_info,
        "lists": [user_list_to_dict(lst) for lst in user.lists[:5]],
        "reviews": [user_review_to_dict(review) for review in user.reviews[:5]],
        "following": [follower_to_dict(u) for u in user.following],
        "followers": [follower_to_dict(u) for u in user.followers]
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

def get_users(user_id=None, username=None, full_name=None, email=None, limit=100):
    """
    search users by id, username, full_name, or email
    """
    if all(arg is None for arg in [user_id, username, full_name, email]):
        return None
    
    try:
        if user_id:
            print(user_id)
            user_id = int(user_id)
        if username:
            print(username)
            if type(username) is not str:
                print("incorrect type for username")
                return None
        if full_name:
            print(full_name)
            if type(full_name) is not str:
                print("incorrect type for full name")
                return None
        if email:
            print(email)
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                print("incorrect format for email")
                return None
    except ValueError:
        print("incorrect type for search parameters")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Build the query
        query = session.query(User)

        if user_id:
            query = query.filter(User.user_id == user_id)
        else:
            if username:
                query = query.filter(User.username.ilike(f'%{username}%'))
            if full_name:
                query = query.filter(User.full_name.ilike(f'%{full_name}%'))
            if email:
                query = query.filter(User.email == email)

        search_results = query.limit(limit).all()
        
        if not search_results:
            return None

        users = [_user_to_dict(user) for user in search_results]

        session.close()

        return users

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_all_users(limit=100):
    """
    get all users. for testing purposes, not exposed.
    default limit is 100
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        all_users = session.query(User).limit(limit).all()

        if not all_users:
            ret = None
        else:
            ret = [_user_to_dict(user) for user in all_users]

        session.close()
        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_user_info(user_id):
    """
    get user information in a dict by user id
    """
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            ret = None
        else:
            ret = _user_to_dict(user)

        session.close()
        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_user_by_email(email):
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("incorrect format for email")
            return None
    else:
        print("no email provided")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(email=email).first()
        return user
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_user_by_username(username):
    if username:
        if type(username) is not str:
            print("incorrect type for username")
            return None
    else:
        print("no username provided")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(username=username).first()
        return user
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def is_a_follower(user2, user1):
    """
    checks whether user2 is a follower of user1
    given their user ids
    returns True or False
    """
    try:
        user2 = int(user2)
        user1 = int(user1)
    except ValueError:
        print("incorrect type for users")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user1 = session.query(User).filter_by(user_id=user1).first()

        if not user1:
            return False

        for follower in user1.followers:
            if follower.user_id == user2:
                return True
        
        return False

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_followers(user_id):
    """
    returns a list of user_id and usernames for all followers of
    the given user id.
    """
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            return None

        followers = []
        for follower in user.followers:
            followers.append(follower_to_dict(follower))

        return followers

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def get_following(user_id):
    """
    returns a list of user_id and usernames that the given user is following
    """
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            return None

        following = []
        for usr in user.following:
            following.append(follower_to_dict(usr))

        return following

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def create_user(username, full_name, email, phone, password):
    """
    creates a user with the required inputs of:
    username, full name, and email
    password is from flask_login
    """
    if username:
        if type(username) is not str:
            print("incorrect type for username")
            return None
    else: 
        print("username not provided")
        return None
    if full_name:
        if type(full_name) is not str:
            print("incorrect type for full name")
            return None
    else: 
        print("full name not provided")
        return None
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("incorrect format for email")
            return None
    else: 
        print("email not provided")
        return None
    try:
        if phone:
            phone = int(phone)
        else: 
            print("phone not provided")
            return None
    except ValueError:
        print("incorrect type for phone")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # profile_picture = user_data['profile_picture'] NOT SURE HOW TO DO THIS
        
        # check that the user doesn't already exist (by email)
        user_w_email = session.query(User).filter_by(email=email).first()
        if user_w_email:
            print("A User with that email already exists. Please sign in or try again.")
            return None

        user_w_username = session.query(User).filter_by(username=username).first()
        if user_w_username:
            print("That username is taken. Please choose another one.")
            return None

        new_user = User(username=username, full_name=full_name, email=email, phone=phone)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()

        print(f"User created with ID: {new_user.user_id}")

        return _user_to_dict(new_user)

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_user_name(user_id, username):
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    if username:
        if type(username) is not str:
            print("incorrect type for username")
            return None
    else: 
        print("username not provided")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user_id = int(user_id)

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.username = username
            session.commit()
            print(f"User {user_id} username updated successfully.")
            ret = _user_to_dict(user)
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_full_name(user_id, full_name):
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    if full_name:
        if type(full_name) is not str:
            print("incorrect type for full_name")
            return None
    else: 
        print("full_name not provided")
        return None
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.full_name = full_name
            session.commit()
            print(f"User {user_id} full name updated successfully.")
            ret = _user_to_dict(user)
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_user_email(user_id, email):
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("incorrect format for email")
            return None
    else: 
        print("email not provided")
        return None
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.email = email
            session.commit()
            print(f"User {user_id} email updated successfully.")
            ret = _user_to_dict(user)
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def update_user_phone(user_id, phone):
    try:
        user_id = int(user_id)
        if phone:
            phone = int(phone)
        else: 
            print("phone not provided")
            return None
    except ValueError:
        print("incorrect type for phone or user id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.phone = phone
            session.commit()
            print(f"User {user_id} phone updated successfully.")
            ret = _user_to_dict(user)
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def follow_user(user1, user2):
    """
    make user 1 follow user 2
    """
    try:
        user2 = int(user2)
        user1 = int(user1)
    except ValueError:
        print("incorrect type for users")
        return None
    
    follower_id = user1
    user_id_to_follow = user2

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        follower = session.query(User).filter_by(user_id=follower_id).first()
        user_to_follow = session.query(User).filter_by(user_id=user_id_to_follow).first()

        user_to_follow.followers.append(follower)
        follower.following.append(user_to_follow)

        session.commit()

        print(f"{follower.username} ({follower_id}) successfully followed {user_to_follow.username} ({user_id_to_follow})")
        return

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def unfollow_user(user1, user2):
    """
    make user 1 unfollow user 2
    """
    try:
        user2 = int(user2)
        user1 = int(user1)
    except ValueError:
        print("incorrect type for users")
        return None
    
    follower_id = user1
    user_id_to_unfollow = user2

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        follower = session.query(User).filter_by(user_id=follower_id).first()
        user_to_unfollow = session.query(User).filter_by(user_id=user_id_to_unfollow).first()

        if not follower or not user_to_unfollow:
            print("One of the users does not exist.")
            return

        if follower in user_to_unfollow.followers:
            user_to_unfollow.followers.remove(follower)

        if user_to_unfollow in follower.following:
            follower.following.remove(user_to_unfollow)

        session.commit()

        print(f"{follower.username} ({follower_id}) successfully unfollowed {user_to_unfollow.username} ({user_id_to_unfollow})")
        return
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()

def delete_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        print("incorrect type for user id")
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        session.query(user_follower_association).filter(
            or_(
                user_follower_association.c.user == user_id,
                user_follower_association.c.follower == user_id
            )
        ).delete(synchronize_session='fetch')

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"User {user_id} deleted successfully.")
            ret = user_id
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None
    finally:
        session.close()
