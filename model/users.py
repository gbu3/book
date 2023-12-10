from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, UserFollower, Review, Book, List, ListBook, Like, DB_URL

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
        "email": user.email
        # "metadata_info": user.metadata_info,
        # "lists": [list_to_dict(lst) for lst in user.lists],
        # "reviews": [review_to_dict(review) for review in user.reviews],
        # "liked_lists": [list_to_dict(lst) for lst in user.liked_lists],
        # "following": [user_to_minimal_dict(u) for u in user.following],
        # "followers": [user_to_minimal_dict(u) for u in user.followers]
    }

def search_users(user_id, username, full_name, email, limit):
    """
    search users by id, username, full_name, or email
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Build the query
        query = session.query(User)

        if user_id:
            query = query.filter(User.user_id == user_id)
        else:
            if username:
                query = query.filter(User.username == username)
            if full_name:
                query = query.filter(User.full_name == full_name)
            if email:
                query = query.filter(User.email == email)

        users = query.limit(limit).all()
        
        if not users:
            return None

        # TODO: will likely want to add stuff about the lists/reviews/etc later
        # but I think those should go in separate functions
        return [_user_to_dict(user) for user in users]

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def get_user(user_id):
    """
    get user by user id
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        session.close()

        if not user:
            return None
        else:
            return _user_to_dict(user)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def is_a_follower(user2, user1):
    """
    checks whether user2 is a follower of user1
    given their user ids
    returns True or False
    """
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

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def get_followers(user_id):
    """
    returns a list of user dicts for all followers of
    the given user id.
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            return None

        followers = []
        for follower in user.followers:
            followers.append(_user_to_dict(follower))

        return followers

        # print(f"{user.username} followers: {[follower.username for follower in user.followers]}, following: {[followee.username for followee in user.following]}")            

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def get_following(user_id):
    """
    returns a list of user dicts that the given user is following
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            return None

        following = []
        for usr in user.following:
            following.append(_user_to_dict(usr))

        return following

        # print(f"{user.username} followers: {[follower.username for follower in user.followers]}, following: {[followee.username for followee in user.following]}")            

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def create_user(username, full_name, email, password):
    """
    creates a user with the required inputs of:
    username, full name, and email
    password is from flask_login
    """
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # profile_picture = user_data['profile_picture'] NOT SURE HOW TO DO THIS

        if not username:
            print ("Need to enter a username to create a new user") 
            return None
        
        if not full_name:
            print("Need to enter full name to create a new user")
            return None

        if not email:
            print ("Need to enter a user email to create a new user")
            return None

        new_user = User(username=username, full_name=full_name, email=email)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()
        created_user_id = new_user.user_id

        print(f"User created with ID: {created_user_id}")

        return {"user_id": created_user_id, "user_name": username}

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def update_user_name(user_id, username):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.username = username
            session.commit()
            print(f"User {user_id} username updated successfully.")
            ret = {"user_id": user.user_id,
                   "user_name": user.username}
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def update_full_name(user_id, full_name):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.full_name = full_name
            session.commit()
            print(f"User {user_id} full name updated successfully.")
            ret = {"user_id": user.user_id,
                   "full_name": user.full_name}
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def update_user_email(user_id, email):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.email = email
            session.commit()
            print(f"User {user_id} email updated successfully.")
            ret = {"user_id": user.user_id, "user_email": user.email}
        else:
            print(f"No user found with ID {user_id}")
            ret = None

        return ret

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

    finally:
        session.close()

def follow_user(user1, user2):
    """
    make user 1 follow user 2
    """
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

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def unfollow_user(user1, user2):
    """
    make user 1 unfollow user 2
    """
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

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()

def delete_user(user_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

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

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        session.close()
