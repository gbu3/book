import model.lists as lists

user_id = 1 # grace
sanshiro = 'OL33968511M'
kundera = 'OL3187189M'

def test_create_list(title, description):
    print("test_create_list")
    lst = lists.create_list(user_id=user_id, title=title, description=description)
    print(lst)
    print()


def test_update_title(list_id, title):
    print("test_update_title")
    lst = lists.update_list_title(user_id, list_id, title)
    print(lst)
    print()

def test_update_description(list_id, description):
    print("test_update_description")
    lst = lists.update_list_description(user_id, list_id, description)
    print(lst)
    print()


def test_add_book(list_id, book_id):
    print("test_add_book")
    lst = lists.add_list_book(user_id, list_id, book_id)
    print(lst)
    print()

def test_remove_book(list_id, book_id):
    print("test_remove_book")
    lst = lists.remove_list_book(user_id, list_id, book_id)
    print(lst)
    print()


def test_get_lists_user():
    print("test_get_lists_user")
    lsts = lists.get_lists(user_id=user_id)
    for r in lsts:
        print(r)
    print()

def test_get_lists_listid(list_id):
    print("test_get_lists_listid")
    lsts = lists.get_lists(list_id=list_id)
    for r in lsts:
        print(r)
    print()

def test_get_lists_book(book_id):
    print("test_get_lists_book")
    lsts = lists.get_lists(book_id=book_id)
    for r in lsts:
        print(r)
    print()

def test_get_lists_book_user(book_id):
    print("test_get_reviews_book_user")
    lsts = lists.get_lists(user_id=user_id, book_id=book_id)
    for r in lsts:
        print(r)
    print()

def test_delete_list(list_id):
    print("test_delete_list")
    lst = lists.delete_list(list_id)
    print(lst)
    print()


if __name__ == '__main__':
    # test_create_list(title="favorites", description="the best books i've read this year")
    # test_update_title(1, "to read")
    # test_update_description(1, "want to read these over winter break")

    # test_add_book(2, sanshiro)
    # test_add_book(2, kundera)

    # test_remove_book(2, sanshiro)
    
    # test_get_lists_user()

    # test_get_lists_listid(1)
    # test_get_lists_listid(2)

    # test_add_book(1, sanshiro)
    # test_get_lists_book(sanshiro)

    test_get_lists_book_user(sanshiro)

    # test_remove_book(1, sanshiro)

    # test_delete_list(1)
    # test_get_lists_user()
