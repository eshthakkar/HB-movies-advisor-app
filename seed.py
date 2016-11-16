"""Utility file to seed movies_advisor database"""

from sqlalchemy import func
from model import (Movie,Source,MovieSource,Genre,MovieGenre,User,MovieWatched,T1Keyword,
                   MovieKeywordRating)  


from model import connect_to_db, db
from server import app
from datetime import datetime

from sys import argv
import requests
import json
import os
import re
from sqlalchemy.orm.exc import NoResultFound




def load_movies():
    """Load movies into database"""

    # Movie.query.delete()
    Movie.query.delete()


    json_string = open(argv[1]).read()

    movie_info = json.loads(json_string)


    num_results = movie_info["total_returned"]

    guidebox_key = os.environ["GUIDEBOX_PRODUCTION_KEY"]

    keywrd_ids = get_keyword_ids()


    for i in range(num_results):
        movie_id = movie_info["results"][i].get("id")
        title = movie_info["results"][i].get("title")
        imdb_id = movie_info["results"][i].get("imdb")
        release_date = movie_info["results"][i].get("release_date")
        released_at = datetime.strptime(release_date,"%Y-%m-%d")

        poster_link = movie_info["results"][i].get("poster_400x570")
        thumbnail_link = movie_info["results"][i].get("poster_240x342")

        detail = requests.get("https://api-public.guidebox.com/v1.43/US/" + guidebox_key + "/movie/" + str(movie_id)).json()
        genres = detail["genres"]

        for source in detail["purchase_web_sources"]:
            if source["source"] == "amazon_buy":
                amazon_link = source["link"]
                break
            else:
                amazon_link = None                


        if len(detail["subscription_web_sources"]) != 0:
            netflix_hulu_link = detail["subscription_web_sources"][0]["link"]
        else:
            netflix_hulu_link = None    

        payload = {"i": imdb_id}
        imdb_resp = requests.get("http://www.omdbapi.com/?plot=short&r=json",params=payload).json()
        imdb_rating = imdb_resp["imdbRating"]
        plot = imdb_resp["Plot"]
        runtime = imdb_resp["Runtime"]
        actors = imdb_resp["Actors"]

        movie = Movie(movie_id=movie_id,
                      title=title,
                      imdb_rating=float(imdb_rating),
                      released_at=released_at,
                      poster_url=poster_link,
                      thumbnail_url=thumbnail_link,
                      plot=plot,
                      runtime=runtime,
                      actors=actors)

        db.session.add(movie)
        db.session.commit() 

        load_movie_source_links(movie_id,amazon_link,netflix_hulu_link)
        load_movie_genre_info(movie_id,genres)
        genres = get_genres(movie_id)
        load_movie_keywords(movie_id,keywrd_ids)
        update_keyword_rating(genres,movie_id)


def load_sources():
    """Loads the available sources"""

    # Source.query.delete() 
    Source.query.delete()  
 

    source1 = Source(src_code="AZN",
                    source="Amazon")

    source2 = Source(src_code="NFX",
                    source="Netflix")

    source3 = Source(src_code="HULU",
                    source="Hulu")

    db.session.add(source1)
    db.session.add(source2)
    db.session.add(source3)
    db.session.commit()  

def load_movie_source_links(movie_id,amazon_link,netflix_hulu_link):
    """Loads the source urls where the movie can be found"""

    if amazon_link is None:
        movie_src1 = MovieSource(movie_id=movie_id)
        db.session.add(movie_src1)

    elif re.search("amazon",amazon_link) is not None:
        movie_src1 = MovieSource(movie_id=movie_id,
                                src_code="AZN",
                                source_url=amazon_link)
        db.session.add(movie_src1)    


    if netflix_hulu_link is None:
        movie_src2 = MovieSource(movie_id=movie_id)
        db.session.add(movie_src2)

    elif re.search("netflix",netflix_hulu_link) is not None:
        movie_src2 = MovieSource(movie_id=movie_id,
                            src_code="NFX",
                            source_url=netflix_hulu_link)
        db.session.add(movie_src2)

    elif re.search("hulu",netflix_hulu_link) is not None:
        movie_src2 = MovieSource(movie_id=movie_id,
                            src_code="HULU",
                            source_url=netflix_hulu_link)
        db.session.add(movie_src2)

    
    db.session.commit()


def load_genres():
    """Loads genres available"""

    Genre.query.delete() 

    json_data = open("data/genres.json").read()

    genre_info = json.loads(json_data)


    results = genre_info["results"]   

    for i in range(len(results)):
        genre_id = results[i].get("id")
        genre = results[i].get("genre")

        genre_info = Genre(genre_id=genre_id,
                           genre=genre)
        db.session.add(genre_info)

    db.session.commit() 


def load_movie_genre_info(movie_id,genres):
    """Loads genres for movies"""

    for genre in genres:
        movie_genre = MovieGenre(movie_id=movie_id,
                                genre_id=genre["id"])
        db.session.add(movie_genre)

    db.session.commit()    
       

def load_keywords():
    """Loads T1 keywords for questions"""

    T1Keyword.query.delete() 


    for row in open("data/keywords.txt"):
        keyword = row.rstrip()
        qt = T1Keyword(descriptive_keyword=keyword)
        db.session.add(qt)
    db.session.commit()

def load_movie_keywords(movie_id,keyword_ids):
    """Loads movies, their keywords and ratings"""

    for keyword_id in keyword_ids:
        movie_key_rating = MovieKeywordRating(movie_id=movie_id,
                                             keyword_id=keyword_id)
        db.session.add(movie_key_rating)
    db.session.commit()    

    
def get_keyword_ids():
    """Return keywords id list"""
    
    keywords = T1Keyword.query.all()

    id_list = []

    for keywrd in keywords:
        id_list.append(keywrd.qk_id) 

    return id_list  


def get_genres(movie_id):
    """Return genres list for a movie based on its id"""

    genres = Movie.query.filter(Movie.movie_id == movie_id).one().genres

    genre_list = []

    for genre in genres:
        genre_list.append(genre.genre) 

    return genre_list  

def update_keyword_rating(genres,movie_id):
    """Update keyword rating based on genres""" 

    for gen in genres:
        try:
            keyword_update_row = db.session.\
            query(MovieKeywordRating).\
            join(Movie,MovieKeywordRating.movie_id == Movie.movie_id).\
            join(T1Keyword,MovieKeywordRating.keyword_id == T1Keyword.qk_id).\
            filter(MovieKeywordRating.movie_id == movie_id, 
            MovieKeywordRating.keyword_id == T1Keyword.query.filter(T1Keyword.descriptive_keyword.like(gen + '%')).one().qk_id).\
            one()

            keyword_update_row.keyword_rating = 50
            db.session.commit()

        except NoResultFound:
            continue    








if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    # load_genres()
    # load_sources()

    load_genres()
    load_sources()
    load_keywords()

    load_movies()

