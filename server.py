"""Movies Advisor"""

from flask import (Flask, jsonify, render_template, redirect,flash, session,request)
from jinja2 import StrictUndefined
from model import (connect_to_db, db)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db,db,User,Movie,Source,MovieSource,Genre,MovieGenre,MovieWatched)


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage"""

    return render_template("homepage.html")

@app.route('/browse',methods=['GET'])
def show_browse():
    """Displays the browse movies page"""

    genres = Genre.query.order_by('genre').all()

    return render_template("browse.html",genres=genres)  

@app.route('/browse.json',methods=['POST'])  
def thumbnails():
    """Returns movie thumbnails for selected genres as json"""

    selected_genre = request.form.getlist("genre[]") 
    final = set()

    for genre in selected_genre:
        genre = genre.replace("/","")
        genre_id = db.session.query(Genre.genre_id).filter(Genre.genre == genre).one()
        movies = Genre.query.filter(Genre.genre_id == genre_id).one().movies
        movies = set(movies)
        final = movies | final

    movie_thumbnails = {}

    for movie in final:
        movie_thumbnails[movie.movie_id] = movie.thumbnail_url

 
    return jsonify(movie_thumbnails) 


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    
    app.run(host="0.0.0.0")
