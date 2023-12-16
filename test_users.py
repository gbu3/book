import model.users as users

password = '1234'
grace = 1
juliet = 3

def test_create_user(username, full_name, email, phone, password='1234'):
    print("test_create_user")
    new_user = users.create_user(username, full_name, email, phone, password)
    print(new_user)
    print()

def test_update_username(user_id, new_username):
    print("test_update_username")
    user = users.update_user_name(user_id, new_username)
    print(user)
    print()

def test_update_full_name(user_id, new_full_name):
    print("test_update_full_name")
    user = users.update_full_name(user_id, new_full_name)
    print(user)
    print()

def test_update_email(user_id, new_email):
    print("test_update_email")
    user = users.update_user_email(user_id, new_email)
    print(user)
    print()

def test_update_phone(user_id, new_phone):
    print("test_update_phone")
    user = users.update_user_phone(user_id, new_phone)
    print(user)
    print()


def test_follow_user(user1, user2):
    print(f"test user {user1} follow user {user2}")
    users.follow_user(user1, user2)
    print()

def test_is_a_follower(user1, user2):
    print(f"test if user {user1} is a follower of user {user2}")
    print(users.is_a_follower(user1, user2))
    print()

def test_get_followers(user_id):
    print(f"test_get_followers for user {user_id}")
    usrs = users.get_followers(user_id)
    for user in usrs:
        print(user)
    print()

def test_get_following(user_id):
    print(f"test_get_following for user {user_id}")
    usrs = users.get_following(user_id)
    for user in usrs:
        print(user)
    print()


def test_get_all_users():
    print("ALL USERS:")
    all = users.get_all_users()
    for user in all:
        print(user)
    print()


def test_get_users_userid(user_id):
    print("test_get_users_userid")
    user = users.get_users(user_id=user_id)
    print(user)
    print()

def test_get_users_username(username):
    print("test_get_users_username")
    usrs = users.get_users(username=username)
    for user in usrs:
        print(user)
    print()

def test_get_users_full_name(full_name):
    print("test_get_users_full_name")
    usrs = users.get_users(full_name=full_name)
    for user in usrs:
        print(user)
    print()

def test_get_users_email(email):
    print("test_get_users_email")
    usrs = users.get_users(email=email)
    for user in usrs:
        print(user)
    print()

def test_get_user_info(user_id):
    print("test_get_user_info")
    user = users.get_user_info(user_id=user_id)
    print(user)
    print()

def test_delete_user(user_id):
    print("test_delete_user")
    user = users.delete_user(user_id=user_id)
    print(user)
    print()

if __name__ == '__main__':
    # test_create_user("juliet", "Juliet Bu", "juliet@gmail.com", "1234")
    

    # test_follow_user(juliet, grace)
    # test_delete_user(juliet)

    # test_is_a_follower(juliet, grace)
    # test_is_a_follower(grace, juliet)

    # test_get_followers(juliet)
    # test_get_following(juliet)

    # test_update_username(juliet, "julietbu")

    # test_update_full_name(juliet, "Juliet Bu")

    # test_update_email(juliet, "julietbu@gmail.com")

    # test_update_phone(juliet, "5678")

    # test_get_users_userid(grace)
    # test_get_users_username("grace")
    # test_get_users_full_name("Bu")
    # test_get_users_email("julietbu@gmail.com")
    # test_get_user_info(juliet)

    test_get_all_users()


