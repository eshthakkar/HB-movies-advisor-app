"""Utility file to seed movies_advisor database"""

from sqlalchemy import func
from model import Movie
from model import Source
from model import MovieSource

from model import connect_to_db, db
from server import app
from datetime import datetime

from sys import argv
import requests
import json
import os
import re



def load_movies():
    """Load movies into database"""

    Movie.query.delete()

    json_string = open(argv[1]).read()

    movie_info = json.loads(json_string)


    num_results = movie_info["total_returned"]

    guidebox_key = os.environ["GUIDEBOX_PRODUCTION_KEY"]

    for i in range(num_results):
        movie_id = movie_info["results"][i].get("id")
        title = movie_info["results"][i].get("title")
        imdb_id = movie_info["results"][i].get("imdb")
        release_date = movie_info["results"][i].get("release_date")
        released_at = datetime.strptime(release_date,"%Y-%m-%d")

        poster_link = movie_info["results"][i].get("poster_400x570")
        thumbnail_link = movie_info["results"][i].get("poster_240x342")

        detail = requests.get("https://api-public.guidebox.com/v1.43/US/" + guidebox_key + "/movie/" + str(movie_id)).json()
        overview_text = detail["overview"]
        genres = detail["genres"]
        amazon_link = detail["purchase_web_sources"][1]["link"]
        netflix_hulu_link = detail["subscription_web_sources"][0]["link"]

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
                      description=overview_text,
                      poster_url=poster_link,
                      thumbnail_url=thumbnail_link,
                      plot=plot,
                      runtime=runtime,
                      actors=actors)

        print movie_id, amazon_link, netflix_hulu_link

        db.session.add(movie)
        db.session.commit() 
        load_movie_source_links(movie_id,amazon_link,netflix_hulu_link)



def load_sources():
    """Loads the available sources"""

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

    movie_src1 = MovieSource(movie_id=movie_id,
                            src_code="AZN",
                            source_url=amazon_link)

    if re.search("netflix",netflix_hulu_link) is not None:
        movie_src2 = MovieSource(movie_id=movie_id,
                            src_code="NFX",
                            source_url=netflix_hulu_link)
        db.session.add(movie_src2)

    if re.search("hulu",netflix_hulu_link) is not None:
        movie_src2 = MovieSource(movie_id=movie_id,
                            src_code="HULU",
                            source_url=netflix_hulu_link)
        db.session.add(movie_src2)



    db.session.add(movie_src1)
    db.session.commit()


                   
        



    

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_sources()
    load_movies()
