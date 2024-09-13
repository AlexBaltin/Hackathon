import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

MY_KEY = os.getenv("MY_KEY")

# from tkinter import *
# import tkinter as tk 
# from tkinter import * 
# root = Tk() 







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
        params = {"apikey": "eeb934dd", "t": title}
        response = requests.get("https://www.omdbapi.com/", params=params)
        return response.json()

    def add_to_watchlist(self, title):
        cursor = self.connection.cursor()
        
        cursor.execute(f"UPDATE movie SET watchlist = 1 WHERE UPPER(title) = '{title.upper()}';")
        
        self.connection.commit()

    def check_watchlist(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT title, year, genre, rating FROM movie WHERE watchlist = 1 ORDER BY title;')
        rows = cursor.fetchall()
        return rows

    def delete_from_watchlist(self,title):
        print(f"The movie {title} removed from your watchlist!")
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE movie SET watchlist = 0 WHERE UPPER(title) = '{title.upper()}';" )
        self.connection.commit()

        # cursor = self.connection.cursor()
        
        # cursor.execute(f"UPDATE movie SET watchlist = 0 WHERE UPPER(title) = '{title.upper()}';")
        
        # self.connection.commit()
   
    def check_history(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT title, year, genre, rating FROM movie;')
        rows = cursor.fetchall()
        return rows
    


    def close(self):
        print("Closing connection to database")
        self.connection.close()

    def menu(self):
        while True:
            
            print("\n1. To see your watchlist press 1 ")
            print("2. To search a movie press 2")
            print("3. To see your searching history press 3\n")
            

            choice = input("Choose what you want to do: ")
            
            if choice == "1":
                print("\n\n\nYou choosed to see you watchlist\n")
                watchlist = self.check_watchlist()
                for movies in watchlist:
                    print(movies)
                
                watch_list_action = input("\n To delete a movie type 1\n*If you want to go back to the menu type wanttoquit \n")
                if watch_list_action == "wanttoquit":
                    my_app.menu

                if watch_list_action == '1':
                    title = input("Which movie to remove?\n")
                    my_app.delete_from_watchlist(title)
                    
                    
                

            if choice == "2":
                print("\n\n\nYou choosed to search a movie\n")
                
   
                movie_title = input("Which movie would you like to check?\n*If you want to go back to the menu type wanttoquit \n")
                if movie_title == "wanttoquit":
                    my_app.menu
                else:
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
                        print(f"{movie_title} added to your watchlist!\n")
                        
                    # movies_in_watchlist = my_app.check_watchlist()

                    # for movie in movies_in_watchlist:
                    #     print(movie)

                
                

            if choice == "3":
                print("\n\n\nYou choosed to see your history, here it is: \n")
                history = self.check_history()
                for movies in history:
                    print(movies)

            

     
my_app = MovieWatchListMaker()
my_app.menu()
my_app.check_history()

# my_app.close()

