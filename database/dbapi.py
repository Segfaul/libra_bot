from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from datetime import datetime,date,time
from sqlalchemy import (
    Column, Integer, String,
    Date, Text,
    ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import func
import pandas as pd
from database.models import Book, Borrow


class DatabaseConnector:
    def __init__(self):
        USERNAME = "agentric"
        connection_string = f"postgresql+psycopg2://{USERNAME}:@localhost:5432/{USERNAME}"
        engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)

    def add(self, title, author, published) -> Book.book_id:
        try:
            session = self.Session()
            today = datetime.now().strftime('%Y-%m-%d')
            book = Book(title = title, author = author, published = published, date_added = today, date_deleted = None)
            session.add(book)
            session.commit()
            return book.book_id
        except Exception as ex: return str(ex)
        finally: session.close()

    def list_books(self) -> list[Book]:
        books = []
        try:
            session = self.Session()
            books = session.query(Book.book_id, Book.title, Book.author, Book.published, Book.date_added, Book.date_deleted).all()
            books = [book for book in books]
            return books
        except Exception as ex: return str(ex)
        finally: session.close()            

    def get_book(self, title, author) -> Book.book_id:
        try:
            session = self.Session()
            book = session.query(Book).where(func.lower(Book.title) == title.lower(), func.lower(Book.author)  == author.lower(), Book.date_deleted == None).first()
            return book.book_id
        except Exception as ex: return str(ex)
        finally: session.close()            

    def borrow(self, book_id, user_id) -> Borrow.book_id | False:
        try:
            session = self.Session()
            #check if book is not deleted
            book = session.query(Book).where(Book.book_id == book_id).first()
            if book.date_deleted is not None:
                print('book is deleted')
                return False
            #check if book is not borrowed now
            book_borrows = session.query(Borrow.borrow_id).where(Borrow.book_id == book_id, Borrow.date_end == None).all()
            if len(book_borrows) > 0:
                print('book is borrowed')
                return False
            #check if user have not returned book
            user_borrows = session.query(Borrow.borrow_id).where(Borrow.user_id == user_id, Borrow.date_end == None).all()
            if len(user_borrows) > 0:
                print('user didnt return a book')
                return False
            #now it's ok and ready to borrow
            today = datetime.now().strftime('%Y-%m-%d')
            borrow = Borrow(book_id = book_id, date_start = today, user_id = user_id)
            session.add(borrow)
            session.commit()
            return borrow.borrow_id            
        except Exception as ex: print(repr(ex)); return str(ex)
        finally: session.close()  
   
    def get_borrow(self,user_id) -> Borrow.borrow_id:
        try:
            session = self.Session()
            user_borrow = session.query(Borrow).where(Borrow.user_id == user_id, Borrow.date_end == None).first()
            return user_borrow.borrow_id
        except Exception as ex: return str(ex)
        finally: session.close()

    def retrieve(self, borrow_id) -> None:
        try:
            session = self.Session()
            today = datetime.now().strftime('%Y-%m-%d')
            borrow = session.query(Borrow).where(Borrow.borrow_id == borrow_id).first()
            borrow.date_end = today
            session.commit()
        except Exception as ex: return str(ex)
        finally: session.close()
    
    def delete(self, book_id) -> bool:
        try:
            session = self.Session()
            book = session.query(Book).filter(Book.book_id == book_id).first()
            if book is None: return False
            borrow = session.query(Borrow).filter(Borrow.book_id == book_id, Borrow.date_end == None).first()
            if borrow is not None: return False
            today = datetime.now().strftime('%Y-%m-%d')
            book.date_deleted = today
            session.commit()
            return True
        except Exception as ex: return str(ex)
        finally: session.close()

# if __name__ == "__main__":
#     x = DatabaseConnector()
#     print(x.borrow(9, 12))