import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open('books.csv') as csvfile:
        books = csv.DictReader(csvfile)
        for book in books:
            isbn = book["isbn"]
            title = book["title"]
            author = book["author"]
            year = book["year"]
            print(isbn, title, author, year)
            db.execute("INSERT INTO books (ISBN, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year": year})
        db.commit()

if __name__ == "__main__":
    main()
