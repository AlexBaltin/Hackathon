import requests
import sqlite3
import os
from dotenv import load_dotenv
from tabulate import tabulate
# import tkinter as tk
# from tkinter import messagebox, scrolledtext

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
        cursor.execute('SELECT title, year, genre, rating FROM movie WHERE watchlist = 1 ORDER BY title;')
        rows = cursor.fetchall()
        return rows
    

    def check_plot(self, title):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT plot FROM movie WHERE UPPER(title) = '{title.upper()}';")
        row = cursor.fetchone()
        return row


    def delete_from_watchlist(self, title):
        print(f"The movie {title} removed from your watchlist!")
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE movie SET watchlist = 0 WHERE UPPER(title) = '{title.upper()}';" )
        self.connection.commit()
   

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
            print("\n To see your watchlist press 1 ")
            print(" To search a movie press 2")
            print(" To see your searching history press 3\n")
            print(" To exit press 4\n")
            
            choice = input("Choose what you want to do:\n")
            
            if choice == "1":
                while True: 
                    print("\n\nYou chose to see your watchlist\n")
                    watchlist = self.check_watchlist()

                    if watchlist:
                        print(tabulate(watchlist, headers=["Title", "Year", "Genre", "Rating"], tablefmt="grid"))
                    else:
                        print("Your watchlist is empty")
                    
                    watch_list_action = input("\n To delete a movie type 1\nTo read the plot type the name of the movie\n*If you want to go back to the menu type gotomenu \n")
                    if watch_list_action == "gotomenu":
                        break

                    elif watch_list_action == '1':
                        title = input("Which movie to remove?\n")
                        self.delete_from_watchlist(title)

                    else:
                        plot = self.check_plot(watch_list_action)
                        if plot:
                            print(f"Here is the plot of the movie:\n{plot[0]}")
                        else:
                            print("Movie not found in the database.")

                    
            elif choice == "2":
                while True:
                    print("\nYou choosed to search a movie\n")
                    
                    movie_title = input("Which movie would you like to check?\n*If you want to go back to the menu type gotomenu\n ")
                    if movie_title == "gotomenu":
                        my_app.menu
                        break
                        
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
                            print(f"\nThe movie {movie_title} is in database")
                            print(movie_in_db)

                        add_to_watchlist = input(f"Add {movie_title} to a watchlist? Y or N: ")
                            

                        if add_to_watchlist.upper() == "Y":
                            my_app.add_to_watchlist(title = movie_title)
                            print(f"\n{movie_title} added to your watchlist!\n")
                        
                        elif add_to_watchlist.upper() == "N":
                             print(f"\n '{movie_title}' was not added to your watchlist.\n Lets search something else")

                        else:
                            print("Invalid choice, please enter 'Y' or 'N'.")   

            elif choice == "3":
                print("\nYou choosed to see your history, here it is: \n")
                history = self.check_history()
                if history:
                    print(tabulate(history, headers=["Title", "Year", "Genre", "Rating"], tablefmt="grid"))
                else:
                    print("Your search history is empty.")
                
                while True:
                    history_action = input("\nTo go back to menu type gotomenu\n")
                    if history_action == "gotomenu":
                        my_app.menu
                        break
                    else:
                        print(f"Invalid choice '{history_action}', please try again!")  
                    

            elif choice == "4":
                print("\nExiting the application.\n")
                self.close()
                break

            else:
                print("Invalid choice, please try again!")
                
               
my_app = MovieWatchListMaker()
my_app.menu()
