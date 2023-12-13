import model.reviews as review

user_id = 1 # grace
sanshiro = 'OL33968511M'
kundera = 'OL3187189M'

def test_create_review(book_id, summary, rating):
    print("test_create_review")
    new_review = review.create_review(book_id, user_id, summary, rating)
    print(f"successfully created review:\n {new_review}")
    print()

def test_get_reviews_user():
    print("test_get_reviews_user")
    reviews = review.get_reviews(user_id=user_id)
    for r in reviews:
        print(r)
    print()

def test_get_reviews_reviewid():
    print("test_get_reviews_reviewid")
    review_id = 1
    reviews = review.get_reviews(review_id=review_id)
    for r in reviews:
        print(r)
    print()

def test_get_reviews_book(book_id):
    print("test_get_reviews_book")
    reviews = review.get_reviews(book_id=book_id)
    for r in reviews:
        print(r)
    print()

def test_get_reviews_book_user(book_id):
    print("test_get_reviews_book_user")
    reviews = review.get_reviews(user_id=user_id, book_id=book_id)
    for r in reviews:
        print(r)
    print()

def test_update_review_summary(review_id, summary):
    print("test_update_review_summary")
    r = review.update_review_summary(review_id=review_id, user_id=user_id, summary=summary)
    print(r)
    print()

def test_update_review_rating(review_id, rating):
    print("test_update_review_rating")
    r = review.update_review_rating(review_id=review_id, user_id=user_id, rating=rating)
    print(r)
    print()

def test_delete_review(review_id):
    print("test_delete_review")
    id = review.delete_review(review_id)
    print(id)
    print()

if __name__ == '__main__':
    test_create_review(book_id=sanshiro,
                        summary = "I enjoyed this coming of age story as a college student myself. Soseki's reflections on radical political involvement are especially interesting and relevant.",
                        rating=7)
    test_create_review(book_id=kundera,
                        summary = "One of the best books I read this summer, masterful prose and incredible literary treatment of concepts like love, humanity, and politics",
                        rating=9)
    # test_get_reviews_user()
    test_get_reviews_book(sanshiro)
    # test_get_reviews_book_user()

    test_update_review_summary(4, "I enjoyed this coming of age story as a college student myself. Soseki's reflections on radical political involvement are especially interesting and relevant.")
    test_update_review_rating(4, 8)
