"""Movies Advisor"""

from flask import (Flask, jsonify, render_template, redirect,flash, session,request)
from jinja2 import StrictUndefined
from model import (connect_to_db, db)
from flask_debugtoolbar import DebugToolbarExtension
from model import (User,Movie,Source,MovieSource,Genre,MovieGenre,MovieWatched,
                  T1Keyword, MovieKeywordRating)
import bcrypt
from helper import form_question,update_movie_profile,add_update_user_preference,clustering
from helper import duplicates

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
    try:
        
        movies = db.session.\
        query(Movie).\
        distinct().\
        join(MovieGenre,MovieGenre.movie_id == Movie.movie_id).\
        join(Genre,MovieGenre.genre_id == Genre.genre_id).\
        filter(Genre.genre.in_(selected_genre), Movie.imdb_rating >= selected_rating).\
        all()

        for movie in movies:
                movie_thumbnails[movie.movie_id] = movie.thumbnail_url
    
    except:
        pass

    return jsonify(movie_thumbnails)        

@app.route('/movie.json/<movie_id>')
def movie_details(movie_id): 
    """ Returns movie details in json"""
    if movie_id.isdigit():
        try:
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
                
            date = movie.released_at
            date = date.strftime("%b %d, %Y")
            movie_details = {"title": movie.title,
                            "imdb_rating": movie.imdb_rating,
                            "plot": movie.plot,
                            "poster_url": movie.poster_url,
                            "released_at": date,
                            "runtime": movie.runtime,
                            "actors": movie.actors,
                            "genres": genre_list,
                            "sources": sources}

            return jsonify(movie_details)
        except NoResultFound:
            return "No movie found!" 
    else:
        return "Error! Not a valid movie Identification"           

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

        if bcrypt.checkpw(password.encode('utf-8'), verify_user_info.password.encode('utf-8')):
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
        flash("Please sign in to view your movie seen list") 
        return redirect('/')     


@app.route('/watchlist',methods=["POST"]) 
def add_movie_to_watchlist():  
    """Add a movie to user's watchlist and return json response""" 

    if 'user_id' in session:
        movie_to_add_id = request.form.get("movie_identifier")
        movie_add_id = int(movie_to_add_id.split("_")[-1])

        try:
            user_movies = User.query.filter(User.user_id == session['user_id']).one().movies
            for movie in user_movies:
                if movie_add_id == movie.movie_id:
                    text = "Movie already in watch list"
                    return jsonify(status="prevent", id=movie_add_id, text=text)
                else:
                    continue 

            movie_watched = MovieWatched(movie_id=movie_add_id,
                                         user_id=session['user_id'])
            db.session.add(movie_watched)

            db.session.commit() 

            question_params = form_question(movie_add_id)

            movie_question = question_params['q1']
            user_question = question_params['q2']

            print movie_question
            print user_question

            text = Movie.query.filter(Movie.movie_id == movie_add_id).one().title + " has been added to your watch list" 

            return jsonify(status="success", 
                           id=movie_add_id,
                           user_id=session['user_id'], 
                           text=text, 
                           mquest=movie_question, 
                           uquest=user_question, 
                           key_wrd1_id=question_params['k_id1'],
                           key_wrd2_id=question_params['k_id2'],
                           keywrd1=question_params['quest_keyword1'],
                           keywrd2=question_params['quest_keyword2'])

        except NoResultFound:
            text = "Sign up/Sign in again to add a movie to your watch list"
            return jsonify(status="fail", text=text)
                
    else:
        text = "Sign in to add a movie to your watch list"
        return jsonify(status="fail", text=text)
            

@app.route('/remove',methods=["POST"])
def remove_movie_from_watchlist():
    """Remove the movie from user's watchlist"""

    movie_remove_id = int(request.form.get("movie_remove_id"))
    MovieWatched.query.filter(MovieWatched.movie_id == movie_remove_id, MovieWatched.user_id == session['user_id']).delete()
    db.session.commit()

    return "container_" + str(movie_remove_id)

    
@app.route('/record-answers',methods=["POST"])
def record_user_response():
    """Records user's submitted response for the movie question in the database"""

    keyword_id_chosen = request.form.get("movie_quest")
    movie_id = request.form.get("movie_id")
    keyword_id1 = request.form.get("keyword_id1")
    keyword_id2 = request.form.get("keyword_id2")

    print keyword_id_chosen, movie_id, keyword_id1, keyword_id2

    # when user profiles a movie
    if keyword_id_chosen is not None:

        update_movie_profile(movie_id,keyword_id_chosen,keyword_id1,keyword_id2)

    else:
        pass    

    user_id = request.form.get("user_id")
    chosen_genre_id = request.form.get("user_quest")

    print user_id, chosen_genre_id, keyword_id1, keyword_id2

    if chosen_genre_id is not None:

        add_update_user_preference(user_id,chosen_genre_id,keyword_id1,keyword_id2)
    else:
        pass    

    return redirect("/watchlist")


@app.route('/recommendations')
def show_recommendations(): 
    """Show movie recommendations to user learning from his/her taste"""

    if 'user_id' in session:

        # Get user's ratings for various genres. To get user's most liked genre
        user_genre_ratings = User.query.filter(User.user_id == session['user_id']).one().genre_ratings

        if user_genre_ratings:
            user_genre_ratings.sort(key=lambda x: x.genre_rating, reverse=True)
            user_top_rated_genre = user_genre_ratings[0]

            print "top genre"
            print user_top_rated_genre

        # cluster the movies including most current feedbacks    
        clustered_data = clustering()

        # labels info which tells us which cluster each movie belongs to from datset of movies objects
        labels = clustered_data["labels"]
        dataset = clustered_data["movies"]
        mids = []
        print labels

        # creating a list of movie ids from dataset of movies.
        for movie in dataset:
            mids.append(movie.movie_id)

        print "movie ids list"    
        print mids    

        # Find the movie id with the user's preferred genre rated as highest
        highest_user_preferred_rating_on_movie = MovieKeywordRating.query.filter(MovieKeywordRating.keyword_id == user_top_rated_genre.keyword_id). \
                                                 order_by(MovieKeywordRating.keyword_rating.desc()).all() 

        highest_preferred_rating_mid = highest_user_preferred_rating_on_movie[0].movie_id

        print "movie id and its index"
        index = mids.index(highest_preferred_rating_mid)
        print highest_preferred_rating_mid, index

        # identifying the cluster to which the movie belongs to
        cluster_info_on_movie = labels[index] 
        print cluster_info_on_movie

        # get indices of all movies belonging to that cluster
        cluster_indices = duplicates(labels,cluster_info_on_movie)
        print cluster_indices
        cluster_movies = []

        # get movies from dataset based on indices info
        for i in cluster_indices:
            cluster_movies.append(dataset[i])

        return render_template("recommendations.html",cluster_movies=cluster_movies)
    else:
        flash("Please sign in to view movie suggestions for you!") 
        return redirect('/')     





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

    app.debug = True
    app.jinja_env.auto_reload = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    
    app.run(host="0.0.0.0")
