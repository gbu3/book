import json
import requests
from urllib.parse import quote
from collections import OrderedDict


API_KEY = "AIzaSyCHFp2x-ag_SYN1iJLRHU1MtwN_8GqXw0s"

def search_book(keyword):
    # url = "https://www.googleapis.com/books/v1/volumes?q=search+terms"
    # headers = {
    #     "Authorization": API_KEY
    # }
    # params = {
    #     "q": quote(keyword),
    #     "maxResults": 10,
    # }

    # print(params)
    results_dict = OrderedDict()

    url = "https://www.googleapis.com/books/v1/volumes?q=" + quote(keyword) + "&key=" + API_KEY

    r = requests.get(url)
    result = r.json()
    items = result['items']
    for item in items:
        id = item['id']
        info = item['volumeInfo']
        # if the field exists and is not null
        if 'subtitle' in info.keys() and 'title' in info.keys():
            print("TITLE\t" + info['title'] + " : " + info['subtitle']) 
        elif 'title' in info.keys():
            print("TITLE\t" + info['title'])
        if 'authors' in info.keys():
            print("AUTHOR(S)\t", end="")
            print(*info['authors'], sep = ", ")
        if 'publishedDate' in info.keys():
            print("DATE\t" + info['publishedDate'])
        if 'averageRating' in info.keys(): #i'm assuming that ratingsCount will then exist as well
            print("RATING\t" + str(info['averageRating']) + f" (from {info['ratingsCount']} rating(s))")
        if 'description' in info.keys():
            print("DESCRIPTION\t" + info['description'])
        print()
        results_dict[id] = item['volumeInfo']
    # r = requests.get(url=url, params=params, headers=headers)

    # print(r.text)

def main():
    keyword = input("Keyword, title, author, etc. to search: ")
    search_book(keyword)

if __name__ == "__main__":
    main()
