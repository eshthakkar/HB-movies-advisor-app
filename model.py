"""Models and database functions"""

from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime


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


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    Genre.query.delete()
    Source.query.delete()
    Movie.query.delete()
    MovieSource.query.delete()
    MovieGenre.query.delete()

    movie_id = 112659

    # Add sample employees and departments
    g1 = Genre(genre='Crime')
    g2 = Genre(genre='Adventure')

    db.session.add_all([g1,g2])
    db.session.commit()

    release_date = "2006-09-09"
    released_at = datetime.strptime(release_date,"%Y-%m-%d")


    movie1 = Movie(movie_id=movie_id,title='Interstellar',
                    imdb_rating=8.6,
                    poster_url='http://static-api.guidebox.com/022615/thumbnails_movies/-alt--112659-7058153888-2123715375-9311010409-large-400x570-alt-.jpg',
                    thumbnail_url='http://static-api.guidebox.com/022615/thumbnails_movies_medium/112659-2890660241-7792228088-5750318360-medium-240x342-alt-.jpg',
                    plot='A  team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
                    runtime='169 min',
                    actors='Ellen Burstyn, Matthew McConaughey, Mackenzie Foy, John Lithgow',
                    released_at=released_at)
    db.session.add(movie1)
    db.session.commit()


    source1 = Source(src_code="AZN",
                    source="Amazon")

    source2 = Source(src_code="NFX",
                    source="Netflix")

    source3 = Source(src_code="HULU",
                    source="Hulu")

    db.session.add_all([source1,source2,source3])
    db.session.commit()


    movie_src1 = MovieSource(movie_id=movie_id,
                            src_code="AZN",
                            source_url='http://www.amazon.com/gp/product/B00TU9UFTS')

    movie_src2 = MovieSource(movie_id=movie_id,
                            src_code="NFX",
                            source_url='http://www.hulu.com/watch/876132')

    movie_genre = MovieGenre(movie_id=movie_id,
                            genre_id=g2.genre_id)

    db.session.add_all([movie_src1,movie_src2,movie_genre])
    db.session.commit()




##############################################################################
# Helper functions

def connect_to_db(app,db_uri="postgresql:///movies_advisor"):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."    