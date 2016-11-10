"""Movies Advisor"""

from flask import (Flask, jsonify, render_template, redirect,flash, session,request)
from jinja2 import StrictUndefined
from model import (connect_to_db, db)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db,db,User,Movie,Source,MovieSource,Genre,MovieGenre,MovieWatched)
import bcrypt


from sqlalchemy.orm.exc import NoResultFound



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

    if 'user_id' in session:
        return redirect("/browse")
    else:    
        return render_template("homepage.html")

@app.route('/browse')
def show_browse():
    """Displays the browse movies page"""

    genres = Genre.query.order_by('genre').all()

    return render_template("browse.html",genres=genres)  

@app.route('/browse.json')  
def thumbnails():
    """Returns movie thumbnails for selected genres as json"""

    selected_genre = request.args.getlist("genre[]") 
    selected_rating = request.args.get("rating")
    
    movie_thumbnails = {}

    # Query based on genre and rating
    if selected_genre:
        
        movies = db.session.\
        query(Movie).\
        distinct().\
        join(MovieGenre,MovieGenre.movie_id == Movie.movie_id).\
        join(Genre,MovieGenre.genre_id == Genre.genre_id).\
        filter(Genre.genre.in_(selected_genre), Movie.imdb_rating >= selected_rating).\
        all()

    # Query just based on rating
    else:
        movies = db.session.\
        query(Movie).\
        distinct().\
        filter(Movie.imdb_rating >= selected_rating).\
        all()

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
        if source.src_code is not None:
            sources[source.src_code] = source.source_url
        else:
            continue    
        

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

@app.route('/signup',methods=["POST"])
def register_process():
    """ User added to database"""

    email = request.form.get("email")
    password = request.form.get("password")
    ROUNDS = 10

    # Hash a password for the first time
    password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(ROUNDS))



    try:
        User.query.filter(User.email == email).one()
        flash("User already exists!")
    except NoResultFound:
        new_user = User(email=email,password=password) 
        db.session.add(new_user)
        db.session.commit() 
        flash("You have signed up successfully")  

    return redirect("/")

@app.route('/signin',methods=["POST"])
def signin_process():
    """ Sign the user in. """

    email = request.form.get("email")
    password = request.form.get("password")


    try: 
        verify_user_info = User.query.filter(User.email == email).one()
        if bcrypt.hashpw(password.encode('utf-8'), verify_user_info.password.encode('utf-8')) == verify_user_info.password:
            session['user_id'] = verify_user_info.user_id
            flash("Logged in as %s" % email)
            print session['user_id']
            return redirect("/browse")
        else:
            flash("Incorrect password!") 
            return redirect("/") 

    except NoResultFound:
        flash("Invalid email! Please sign up!")
        return redirect("/") 


@app.route('/signout')
def signout():
    """Sign out user"""

    if 'user_id' in session:
        del session['user_id']
        flash("Logged Out!") 
        return redirect('/') 


@app.route('/watchlist',methods=["GET"])
def show_watch_list():
    """Show movie watch list for the user"""

    if 'user_id' in session:
        user_movies = User.query.filter(User.user_id == session['user_id']).one().movies
        return render_template("mymovies.html",user_movies=user_movies)
    else:
        flash("Please sign in to view your watch list") 
        return redirect('/')     


@app.route('/watchlist',methods=["POST"]) 
def add_movie_to_watchlist():  
    """Add a movie to user's watchlist""" 

    if 'user_id' in session:
        movie_to_add_id = request.form.get("movie_identifier")
        movie_add_id = int(movie_to_add_id.split("_")[-1])

        user_movies = User.query.filter(User.user_id == session['user_id']).one().movies
        for movie in user_movies:
            if movie_add_id == movie.movie_id:
                return "Movie already in watch list"
            else:
                continue 

        movie_watched = MovieWatched(movie_id=movie_add_id,
                                     user_id=session['user_id'])
        db.session.add(movie_watched)

        db.session.commit() 
        return Movie.query.filter(Movie.movie_id == movie_add_id).one().title + " has been added to your watch list" 

    else:
        return "Sign in to add a movie to your watch list"
            

@app.route('/remove',methods=["POST"])
def remove_movie_from_watchlist():
    """Remove the movie from user's watchlist"""

    movie_remove_id = int(request.form.get("movie_remove_id"))
    MovieWatched.query.filter(MovieWatched.movie_id == movie_remove_id, MovieWatched.user_id == session['user_id']).delete()
    db.session.commit()
    
    return "container_" + str(movie_remove_id)
    
       

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

    app.debug = True
    app.jinja_env.auto_reload = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    
    app.run(host="0.0.0.0")
