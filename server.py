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

@app.route('/browse.json')  
def thumbnails():
    """Returns movie thumbnails for selected genres as json"""

    selected_genre = request.args.getlist("genre[]") 
        
    movies = db.session.\
    query(Movie).\
    distinct().\
    join(MovieGenre,MovieGenre.movie_id == Movie.movie_id).\
    join(Genre,MovieGenre.genre_id == Genre.genre_id).\
    filter(Genre.genre.in_(selected_genre)).\
    all()

    movie_thumbnails = {}

    for movie in movies:
        movie_thumbnails[movie.movie_id] = movie.thumbnail_url

 
    return jsonify(movie_thumbnails) 

@app.route('/movie.json/<movie_id>')
def movie_details(movie_id): 
    """ Returns movie details in json"""
    
    movie = Movie.query.filter(Movie.movie_id == movie_id).one() 
    
    genre_list = []
    sources = {}

    for genre in movie.genres:
        genre_list.append(genre.genre)

    for source in movie.movies_sources:
        sources[source.src_code] = source.source_url
        

    movie_details = {"title": movie.title,
                    "imdb_rating": movie.imdb_rating,
                    "plot": movie.plot,
                    "poster_url": movie.poster_url,
                    "released_at": movie.released_at,
                    "runtime": movie.runtime,
                    "actors": movie.actors,
                    "genres": genre_list,
                    "sources": sources}

    return jsonify(movie_details)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    
    app.run(host="0.0.0.0")
