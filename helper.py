from random import choice
from model import T1Keyword, Movie, MovieKeywordRating

def form_question(movie_id):
    """Query Database for the most weighted keyword to form a question for user"""

    keywords = Movie.query.filter(Movie.movie_id == movie_id).one().movie_keywords

    top_keywords = [keyword for keyword in keywords if keyword.keyword_rating > 30]

    picked_keyword_row = choice(top_keywords)

    quest_keyword = T1Keyword.query.filter(T1Keyword.qk_id == picked_keyword_row.keyword_id).one().descriptive_keyword
    print quest_keyword, picked_keyword_row.keyword_rating

    if (quest_keyword[0] == 'A' or quest_keyword[0] == 'E' or quest_keyword[0] == 'I' or
        quest_keyword[0] == 'O' or quest_keyword[0] == 'U'):
        question = "Did you find the movie more of an " + quest_keyword + " movie?"
    else:    
        question = "Did you find the movie more of a " + quest_keyword + " movie?"

    return {'q': question, 'k_id': picked_keyword_row.keyword_id}


