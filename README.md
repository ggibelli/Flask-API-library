# Project 1

Web Programming with Python and JavaScript

Welcome to the project1, the book review web application.

The website follow this logic, when the user open the url /, if not already logged in they're moved to the login page.

If the user doesn't have an account yet they can register clicking on the navbar (/register), the register page is gonna open, the user has no choose an username and email(both unique key, the availability is checked with AJAX to avoid error 500), then has to choose the password, confirm it, (minimum requirements checked with Javascript, the password is hashed).

Once they're registered the real homepage (/) in gonna open, where the user is welcome by name, and two tables show the top rated and top reviewed books on the website, they can click on the book to check the book page.

The user to find a book can look for it in the navbar for a quick search (only by title), or open the advanced research page where they can look for book through ISBN, author and title in combination (ILIKE query and AND operator).

The results page (/books) is a table where are shown all the books result of the query, the whole row (<tr>) is clickable and not only the cell (<td>). Clicking on a row make the book page open.

The book page (/book) contains info about the book, the author, title, year and ISBN, it also contains the average review and the number of reviews from Goodread and from this website itself. It's also possible to read other's people review's previews, rating, name of the user and when they left it, and clicking on them the full one is gonna open.
From this page if the user never left a review for that book they can also make a new one, writing a title of the review and giving a rating from 1 star to 5 stars.

In the navbar the user can also open their reviews (/myreviews) where they can edit or delete a review.

The last link in the navbar is api info where the user can see how to use this website API.

The website is currently online at this address: https://project1-cs50w-giovanni.herokuapp.com/


File list:
import.py: script to import to the DB the books.cvs containing all the books.
application.py: flask application .
utilities.py: contains the apology function (from the finance project CS50).
books.csv: books list.
requirements.txt: contains all the packages required for this application to run.
static/styles.scss: sass version of the styles.
static/styles.css: compiled version in css of the styles.
static/styles.css.map: compiling map.
templates/api_info.html: is the api istruction page.
templates/apology.html: rendered by the apology function changes dinamically with the error.
templates/book.html: is the single book page, used to see the book's info or post a review.
templates/books.html: is the search result page.
templates/index.html: is the homepage of the website showing the top 10 books.
templates/layout.html: is the layout of all the pages.
templates/login.html: is the login page.
templates/myreviews.html: is the page that shows the user's reviews.
templates/register.html: is the registration page.
templates/search.html: is the advanced search page.
templates/update.html is the edit/delete page.