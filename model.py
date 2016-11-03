"""Models and database functions"""

from flask_sqlalchemy import SQLAlchemy
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

################################################################################################
# Model definitions

class Movie(db.Model):
    """Movies to watch."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    imdb_rating = db.Column(db.Float)
    released_at = db.Column(db.DateTime)
    description = db.Column(db.String(2000),nullable=False)
    poster_url = db.Column(db.String(200),nullable=False)
    thumbnail_url = db.Column(db.String(200),nullable=False)
    plot = db.Column(db.String(500))
    runtime = db.Column(db.String(20),nullable=False)
    actors = db.Column(db.String(300),nullable=False)

    genres = db.relationship("Genre",
                            secondary="movies_genres",
                            backref="movies")

    users = db.relationship("User",
                            secondary="movies_watched",
                            backref="movies")


    def __repr__(self):
        """ Provide helpful representation of movie when printed"""

        return "<Movie movie_id=%s title=%s imdb_rating=%s Cast=%s>" % (self.movie_id, self.title, self.imdb_rating,self.actors)


class Source(db.Model):
    """Sources for the movies"""

    __tablename__ = "sources" 
    
    src_code = db.Column(db.String(5),primary_key=True) 
    source = db.Column(db.String(10), nullable=False,unique=True) 

    def __repr__(self):
        """Provide helpful representation of source when printed"""

        return "<Source src_code=%s source=%s>" % (self.src_code, self.source) 


class MovieSource(db.Model):
    """Glue between movies and sources"""

    __tablename__ = "movies_sources"

    movie_source_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    movie_id = db.Column(db.Integer,
               db.ForeignKey("movies.movie_id"),
               nullable=False)
    src_code = db.Column(db.String(5),
               db.ForeignKey("sources.src_code"))
    source_url = db.Column(db.String(100))

    movie = db.relationship("Movie",backref="movies_sources")
    source = db.relationship("Source",backref="movies_sources")

    def __repr__(self):
        """ Provide helpful representation of movie source when printed"""

        return "<MovieSource movie_source_id=%s movie_id=%s src_code=%s source_url=%s>" % (self.movie_source_id, self.movie_id, self.src_code, 
               self.source_url)


class Genre(db.Model):
    """Genres for the movies"""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer,primary_key=True)
    genre = db.Column(db.String(50),nullable=False,unique=True)

    def __repr__(self):
        """Provide helpful representation of genre when printed"""

        return "<Genre genre_id=%s genre=%s>" % (self.genre_id, self.genre)



class MovieGenre(db.Model):
    """Genre information for movies"""

    __tablename__ = "movies_genres" 

    movie_genre_id = db.Column(db.Integer,autoincrement=True,primary_key=True) 
    movie_id = db.Column(db.Integer,
               db.ForeignKey("movies.movie_id"),
               nullable=False)
    genre_id = db.Column(db.Integer,
                         db.ForeignKey("genres.genre_id"),
                         nullable=False)

    def __repr__(self):
        """Provide helpful representation of movie genre when printed"""

        return "<MovieGenre movie_genre_id=%s movie_id=%s genre_id=%s>" % (self.movie_genre_id,
                                                                           self.movie_id,
                                                                           self.genre_id)


class User(db.Model):
    """User of the movies advisor App"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """ Provide helpful representation of user when printed"""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class MovieWatched(db.Model):
    """Movies watched by user"""

    __tablename__ = "movies_watched"

    movies_watched_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    movie_id = db.Column(db.Integer,
               db.ForeignKey("movies.movie_id"),
               nullable=False)
    user_id = db.Column(db.Integer,
              db.ForeignKey("users.user_id"),
              nullable=False)

    def __repr__(self):
        """Provide helpful representation of movie watched by user when printed"""

        return "<MovieWatched movies_watched_id=%s movie_id=%s user_id=%s>" % (self.movies_watched_id, self.movie_id,
                                                                               self.user_id)









##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movies_advisor'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."    