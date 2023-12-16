import model.books as books
import model.reviews as reviews
import model.lists as lists

sanshiro = 'OL33968511M'
kundera = 'OL3187189M'

def test_search_all():
    # edition_id = 'OL1000302M'
    # work_id = 'OL11133293W'
    # author_name = 'soseki'
    # author_id = 'OL10004777A'
    title = 'the unbearable lightness of being'
    # publisher_name = 'harper'

    # keyword = 'Russia'
    # language = 'French'
    # start_year = 2000
    # end_year = 2002

    edition_id = None
    work_id = None
    author_name = None
    author_id = None
    # title = None
    publisher_name = None

    # keyword = None
    # language = None
    # start_year = None
    # end_year = None

    result = books.search_editions(edition_id=edition_id, work_id=work_id, author_name=author_name,
                                author_id=author_id, title=title, publisher_name=publisher_name)
    
    for book in result:
        print(book)

def test_search_title():
    title = 'the unbearable lightness of being'
    result = books.search_by_title(title)
    for book in result:
        print(book)

def test_get_book():
    # book_id = 'OL32396895M'
    # book_id = 'OL8005727M'
    # book_id = 'OL44230154M' # 2 authors
    book_id = 'OL22137678M' # genre
    result = books.get_book(book_id)
    print(result)

# def test_get_author_books():
#     author_id = 'OL23919A'
#     result = books.get_author_books(author_id)
#     for book in result:
#         print(book)

def test_get_author():
    author_id = 'OL23919A'
    result = books.get_author(author_id)
    print(result)

def test_search_author():
    author_name = 'soseki'
    result = books.search_author(author_name=author_name)
    for author in result:
        print(author)

def test_search_by_author():
    author_name = 'N. K. Mehrotra'
    author_id = 'OL23919A'
    # result = books.search_by_author(author_id=author_id)
    result = books.search_by_author(author_name=author_name)
    # result = books.search_by_author(author_id=author_id, author_name=author_name)
    for book in result:
        print(book)

def test_search_by_work():
    work_id = 'OL10000017W'
    result = books.search_by_work(work_id=work_id)
    for book in result:
        print(book)

# def test_search_by_keyword():
#     keyword = 'the gate'
#     result = books.search_by_keyword(keyword=keyword)
#     for book in result:
#         print(book)

def test_get_edition_title_cover_authors():
    # edition_id = 'OL33968511M' # kundera
    edition_id = 'OL44230154M'
    result = books.get_edition_title_cover_authors(edition_id=edition_id)
    print(result)

def test_get_reviews(edition_id):
    print("test_get_reviews")
    result = reviews.get_reviews(book_id=edition_id)
    print(result)
    print()

def test_get_lists(edition_id):
    print("test_get_lists")
    result = lists.get_lists(book_id=edition_id)
    print(result)
    print()

def test_get_edition_info(edition_id):
    print("test_get_edition_info")
    result = books.get_edition_info(edition_id)
    print(result)
    print()


if __name__ == '__main__':
    test_get_edition_info('OL33968511M')