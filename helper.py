from random import randint
from model import T1Keyword, Movie, MovieKeywordRating
from model import (connect_to_db, db)


def form_question(movie_id):
    """Query Database for the most weighted keyword to form a question for user"""

    # sorted keywords
    keywords = db.session.\
            query(MovieKeywordRating).\
            join(Movie,MovieKeywordRating.movie_id == Movie.movie_id).\
            filter(MovieKeywordRating.movie_id == movie_id).\
            order_by(MovieKeywordRating.keyword_rating).\
            all()

    quest_keyword1_elements = quest_keyword(keywords)        
    quest_keyword1 = quest_keyword1_elements['quest_keyword']
    picked_keyword_row1 = quest_keyword1_elements['picked_keyword_row']

    keywords.remove(picked_keyword_row1)
    quest_keyword2_elements = quest_keyword(keywords)        
    quest_keyword2 = quest_keyword2_elements['quest_keyword']
    picked_keyword_row2 = quest_keyword2_elements['picked_keyword_row']

    question1 = "Did you find the movie more of " + get_preposition(quest_keyword1) + " " + quest_keyword1 + " or " + get_preposition(quest_keyword2) + " " + quest_keyword2 + " movie?"

    question2 = "Do you like " + quest_keyword1 + " or " + quest_keyword2 + " movies?"
    
        
    return {'q1': question1, 'q2': question2, 'k_id1': picked_keyword_row1.keyword_id, 'k_id2': picked_keyword_row2.keyword_id,
           'quest_keyword1': quest_keyword1, 'quest_keyword2': quest_keyword2}




def quest_keyword(keywords):
    """calculate total score of all keywords in the keyword list,
    calculate cumulative scores for each keyword, pick a keyword based on these
    cum scores and randomly picked number between 1 and total score and return it
    along with its row object
    """

    total_score = 0
    keyword_cum_ratings = []

    # calculate total score of all keywords
    # and cumulative scores for each keyword

    for keyword in keywords:
        total_score += keyword.keyword_rating
        if keyword_cum_ratings:
            cum_score = keyword.keyword_rating + keyword_cum_ratings[-1]
        else:
            cum_score = keyword.keyword_rating
        keyword_cum_ratings.append(cum_score)
        
    pick = randint(1,total_score)

    for i,j in enumerate(keyword_cum_ratings):
        if j >= pick:
            picked_keyword_row = keywords[i]
            break
        else:
            continue 

    quest_keyword = T1Keyword.query.filter(T1Keyword.qk_id == picked_keyword_row.keyword_id).one().descriptive_keyword
        
    return {'quest_keyword':quest_keyword,
            'picked_keyword_row': picked_keyword_row}  


def get_preposition(keyword):
    """checks if the keyword startswith a vowel and returns the correct preposition for it"""

    vowels = ('a','e','i','o','u','A','E','I','O','U')

    if keyword.startswith(vowels):
        return 'an'
    else:
        return 'a'    


    


