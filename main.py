import requests
import sqlite3

import os
from dotenv import load_dotenv

load_dotenv()

MY_KEY = os.getenv("MY_KEY")


class MovieWatchListMaker:
    def __init__(self) -> None:
        self.connection = sqlite3.connect("movies.db")

    def connect_to_db(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(1000) NOT NULL,
                year INT NOT NULL,
                genre VARCHAR(250),
                plot TEXT,
                rating FLOAT,
                watchlist BOOL DEFAULT FALSE
            );
        """)
        self.connection.commit()
        # cursor.close()
        # connection.close()


    def insert_movie_to_db(self, id, title, year, genre, plot, rating):
        print(f"Adding movie {title} to database")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO movie (id, title, year, genre, plot, rating)
                VALUES (?, ?, ?, ?, ?, ?)
                       
        """, (id, title, int(year.split("–")[0]), genre, plot, float(rating)))
        # year = "1998-2004" --> year.split("-") = ["1998", "2024"]  --> year.split("-")[0] = "1998" --> int(year.split("-")[0]) = 1998
        # year = "2001" --> year.split("-") = ["2001"]  --> year.split("-")[0] = "2001" --> int(year.split("-")[0]) = 2001

        self.connection.commit()


    def get_movie_by_title_from_db(self, title):
        cursor = self.connection.cursor()
        
        cursor.execute(f"SELECT * FROM movie WHERE UPPER(title) = '{title.upper()}';")
        row = cursor.fetchone()

        return row

    @staticmethod
    def get_movie_by_title_from_api(title):
        params = {"apikey": MY_KEY, "t": title}
        response = requests.get("https://www.omdbapi.com/", params=params)
        return response.json()

    def add_to_watchlist(self, title):
        cursor = self.connection.cursor()
        
        cursor.execute(f"UPDATE movie SET watchlist = 1 WHERE UPPER(title) = '{title.upper()}';")
        
        self.connection.commit()

    def check_watchlist(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM movie WHERE watchlist = 1;')
        rows = cursor.fetchall()
        return rows
    
    # new function checking all the movies in database
    def check_history(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM movie;')
        rows = cursor.fetchall()
        return rows
    


    def close(self):
        print("Closing connection to database")
        self.connection.close()



my_app = MovieWatchListMaker()
while True:

    

    movie_title = input("Which movie would you like to check? ")

    my_app.connect_to_db()
    movie_in_db = my_app.get_movie_by_title_from_db(title = movie_title)

    if not movie_in_db:
        movie_dict = my_app.get_movie_by_title_from_api(title = movie_title)
        print(f"The movie {movie_title} is not in database")
        print(movie_dict["Title"], movie_dict["Year"], movie_dict["Genre"], movie_dict["Plot"], movie_dict["imdbRating"])

        if movie_dict["Response"] == "True":

            my_app.insert_movie_to_db(id = movie_dict["imdbID"], 
                                        title = movie_dict["Title"], 
                                        year = movie_dict["Year"], 
                                        genre = movie_dict["Genre"], 
                                        plot = movie_dict["Plot"], 
                                        rating = movie_dict["imdbRating"])
        else:
            print(movie_dict["Error"])

    else:
        print(f"The movie {movie_title} is in database")
        print(movie_in_db)

    add_to_watchlist = input(f"Add {movie_title} to a watchlist? Y or N: ")

    if add_to_watchlist.upper() == "Y":
        my_app.add_to_watchlist(title = movie_title)
        print(f"{movie_title} added to your watchlist")

    movies_in_watchlist = my_app.check_watchlist()

    for movie in movies_in_watchlist:
        print(movie)


# my_app.close()


# menu():
    #     print("Welcome to your watchlist!\n")
    #     print("1. To see your watchlist press 1 ")
    #     print("2. To search a movie press 2")
    #     print("3. To see your searching history press 3")
    #     choice = input("Choose what you want to do: ")
    #     if choice == "1":
    #         print("You choosed to see you watchlist")
    #         my_app.check_watchlist()

    #     if choice == "2":
    #         print("You choosed to search a movie")
    #         my_app.check_watchlist()