from sqlalchemy import (
    Column, Integer, String,
    Date, Text,
    ForeignKey, UniqueConstraint, 
    )
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Book(Base):
    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    published = Column(Integer, nullable=False)
    date_added = Column(Date, nullable=False)
    date_deleted = Column(Date, nullable=True)
    __tablename__ = 'books'


class Borrow(Base):
    borrow_id = Column(Integer, primary_key=True)
    book_id = Column(ForeignKey('books.book_id'), nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    user_id = Column(Integer, nullable=False)
    __tablename__ = 'borrows'
