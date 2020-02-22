import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import requests
import logging


from utilities import login_required, apology

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Getting the time
now = datetime.now()
timenow = now.strftime("%d/%m/%Y %H:%M:%S")



@app.route("/")
@login_required
def index():
    user_id = session['user_id']
    reviews = db.execute("SELECT review_id, review_title, created, title, author, isbn FROM reviews "
                         "INNER JOIN books ON reviews.book_id = books.book_id WHERE user_id = :user_id ",
                         {"user_id": user_id}).fetchall()
    return render_template("index.html", reviews = reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("You must provide a username")
        elif db.execute("SELECT user_id FROM users WHERE username = :username",
                        {"username": username}).fetchone() is not None:
            return apology("Username already exists")
        elif db.execute("SELECT user_id FROM users WHERE email = :email",
                        {'email': email}).fetchone() is not None:
            return apology("Email already exists")

        elif not password or password != confirmation:
            return apology("You must provide a password")

        elif password == confirmation:
            hashpassword = generate_password_hash(password)
            db.execute(
                'INSERT INTO users (username, password, email, created_on) VALUES (:username, :hashpassword, :email, :now)',
                {'username': username, 'hashpassword': hashpassword, 'email': email, 'now': now}
            )
            db.commit()
            flash("Welcome")
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = :username', {'username': username}).fetchone()

        if user is None:
            return apology("invalid username", 403)
        elif not check_password_hash(user[2], password):
            return apology("invalid password", 403)

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == 'GET':
        return render_template("search.html")
    else:
        if request.form.get("searchsimple"):
            searchsimple = "%" + request.form.get("searchsimple").replace(" ", "%") + "%"
            results = db.execute("SELECT isbn, title, author, year FROM books WHERE title LIKE :searchsimple",
                                    {"searchsimple": searchsimple}).fetchall()
        else:
            isbn = "%" + request.form.get("isbn") + "%"
            title = "%" + request.form.get("title").replace(" ", "%") + "%"
            author = "%" + request.form.get("author").replace(" ", "%") + "%"
            results = db.execute("SELECT isbn, title, author, year FROM books WHERE title "
                                 "ILIKE :title AND isbn ILIKE :isbn AND author ILIKE :author",
                                    {"title": title, "isbn": isbn, "author": author}).fetchall()

        return render_template("books.html", results = results)


def goodread(isbn):
    return requests.get("https://www.goodreads.com/book/review_counts.json",
                 params={"key": "hoRUeTOzPq7YGVYPD555Qg", "isbns": isbn}).json()


@app.route("/books/<string:isbn>", methods=["GET", "POST"])
@login_required
def books(isbn):
    book = db.execute("SELECT book_id, isbn, title, author, year FROM books WHERE isbn = :isbn",
                      {"isbn": isbn}).fetchone()


    if request.method == 'GET':
        #count_review = groupby to showo n book page
        #average our review = groupby avg on rating to show on book page
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
                             {"book_id": book[0]}).fetchall()
        goodreads = goodread(isbn)
        percentagereview = float(goodreads['books'][0]['average_rating']) * 20
        return render_template("book.html", book = book, reviews = reviews, goodreads = goodreads, percentagereview = percentagereview)
    else:
        title = request.form.get("title")
        review = request.form.get("review")
        rating = request.form.get("rating")
        user_id = session['user_id']
        db.execute(
            'INSERT INTO reviews (rating, user_id, book_id, review, created, review_title) VALUES '
            '(:rating, :user_id, :book_id, :review, :created, :review_title)',
            {'rating': rating, 'user_id': user_id, 'book_id': book_id, 'review': review, 'created': now, 'review_title': title}
        )
        db.commit()
        flash("Review inserted")
        return redirect("/")


@app.route("/books/<string:isbn>/<int:review_id>")
@login_required
def review(isbn, review_id):
    review = db.execute("SELECT rating, review, review_title, created, updated FROM reviews WHERE review_id = :review_id",
                        {"review_id": review_id}).fetchone()
    if not review:
        return apology("Review not found", 404)
    return render_template("review.html", review = review, review_id = review_id)



@app.route("/books/<string:isbn>/<int:review_id>/update", methods=["GET", "POST"])
@login_required
def update(isbn, review_id):
    user_id = session['user_id']
    checked = [0,0,0,0,0,0]
    review = db.execute(
        "SELECT rating, review, review_title, created, updated, user_id FROM reviews WHERE review_id = :review_id",
        {"review_id": review_id}).fetchone()
    for i in range(1,6):
        if i == review[0]:
            checked[i] = "checked"
    if request.method == "GET":
        if review[5] != user_id:
            return apology("not authorized", 403)
        return render_template("update.html", review = review, review_id = review_id, isbn = isbn, checked = checked)
    else:
        review = request.form.get("review")
        rating = request.form.get("rating")
        review_title = request.form.get("review_title")
        db.execute(
            'UPDATE reviews SET rating = :rating, review = :review, review_title = :review_title, updated = :updated '
            'WHERE review_id = :review_id',
            {'rating': rating, 'review': review, 'review_title': review_title, 'updated': now, 'review_id': review_id}
        )
        db.commit()
        return redirect("/")



@app.route("/books/<string:isbn>/<int:review_id>/delete", methods=["POST"])
@login_required
def delete(isbn, review_id):
    check_user = db.execute(
        "SELECT user_id FROM reviews WHERE review_id = :review_id",
        {"review_id": review_id}).fetchone()
    user_id = session['user_id']
    if check_user[0] != user_id:
        return apology("not authorized", 403)
    db.execute(
        'DELETE FROM reviews WHERE review_id = :review_id',
        {'review_id': review_id}
    )
    db.commit()
    return redirect("/")



@app.route("/api/<string:isbn>")
@login_required
def api(isbn):
    jsonapi = db.execute("SELECT title, author, year, isbn FROM books WHERE isbn = :isbn",
                         {"isbn": isbn}).fetchone()
    if jsonapi is None:
        return jsonify({"error": "Invalid ISBN"}), 422

    myavgreview = db.execute("SELECT AVG (rating) FROM reviews INNER JOIN books ON reviews.book_id = books.book_id WHERE isbn = :isbn",
                         {"isbn": isbn}).fetchone()
    myreviewers = db.execute("SELECT COUNT (rating) FROM reviews INNER JOIN books ON reviews.book_id = books.book_id WHERE isbn = :isbn",
                         {"isbn": isbn}).fetchone()
    return jsonify({
        "title": jsonapi[0],
        "author": jsonapi[1],
        "year": jsonapi[2],
        "isbn": jsonapi[3],
        "review_count": myreviewers[0],
        "average_score": myavgreview[0]
    })



