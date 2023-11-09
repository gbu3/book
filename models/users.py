from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, UserFollower, Review, Book, List, ListBook, Like, DB_URL

engine = create_engine(DB_URL)

def search_users(search_terms, limit):
    pass

def get_user(user_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        # classrooms = (session.query(user_classroom_association.c.classroom_id)
        #                  .filter(user_classroom_association.c.user_id==user_id)
        #                  .all()
        #                  )

        # admin_classrooms = (session.query(admin_classroom_association.c.classroom_id)
        #                  .filter(admin_classroom_association.c.user_id==user_id)
        #                  .all()
        #                  )

        session.close()
        engine.dispose()

        if not user:
            return None
        else:
            return {"user_name": user.user_name, "user_email": user.user_email, "user_phone": user.user_phone, "score": user.score, "classrooms": classrooms, "admin_classrooms": admin_classrooms}

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)

def get_followers(user_id):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        # TODO change
        print(f"{user.name} followers: {[follower.name for follower in user.followers]}, following: {[followee.name for followee in user.following]}")            

        session.close()
        engine.dispose()

        if not user:
            return None
        else:
            return {"user_name": user.user_name, "user_email": user.user_email, "user_phone": user.user_phone, "score": user.score, "classrooms": classrooms, "admin_classrooms": admin_classrooms}

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)

def is_a_follower(user2, user1):
    """
    checks whether user2 followers user1
    returns True or False
    """
    pass

def get_following(user_id):
    """
    returns a list of user_ids that the given user is following
    """
    pass

def create_user(user_data):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # username, full name, email, profile picture
        username = user_data['username']
        full_name = user_data['full_name']
        email = user_data['email']
        # profile_picture = user_data['profile_picture'] NOT SURE HOW TO DO THIS

        if not username:
            print ("Need to enter a username to create a new user") # something like that
            session.close()
            engine.dispose()
            return None
        
        if not full_name:
            print("Need to enter full name to create a new user")
            session.close()
            engine.dispose()
            return None

        if not email:
            print ("Need to enter a user email to create a new user")
            session.close()
            engine.dispose()
            return None

        new_user = User(username=username, full_name=full_name, email=email)
        session.add(new_user)
        session.commit()
        created_user_id = new_user.user_id

        print(f"User created with ID: {new_user.user_id}")
        session.close()
        engine.dispose()

        return {"user_id": created_user_id, "user_name": username} # not sure this is the best return type

    except Exception as ex:
        print(ex, file=stderr)
        session.close()
        engine.dispose()
        exit(1)

def update_user(user_id, user_data):
    pass

def follow_user(user1, user2):
    """
    make user 1 follow user 2
    """
    follower_id = user1
    user_id_to_follow = user2
    # TODO: add input validation

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        follower = session.query(User).filter_by(user_id=follower_id).first()
        user_to_follow = session.query(User).filter_by(user_id=user_id_to_follow).first()

        user_to_follow.followers.append(follower)
        follower.following.append(user_to_follow)

        session.commit()

        print(f"{follower.name} ({follower_id}) successfully followed {user_to_follow.name} ({user_id_to_follow})")

        session.close()
        engine.dispose()

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

def unfollow_user(user1, user2):
    """
    make user 1 unfollow user 2
    """

def delete_user(user_id):
    pass
