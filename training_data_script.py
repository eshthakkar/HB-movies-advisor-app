from helper import form_question,update_movie_profile,add_update_user_preference, clustering
from server import app
from model import connect_to_db,User
from random import choice

connect_to_db(app)

def pick_keyword_for_movie(movie_id, keywords_id):

    if movie_id == 1308 and (6 in keywords_id and 18 in keywords_id):
        movie_genre_id_pick = choice(keywords_id[1:])
    elif movie_id == 1308 and (6 in keywords_id):
        movie_genre_id_pick = 6
    elif movie_id == 1308 and (18 in keywords_id):
        movie_genre_id_pick = 18
    
    elif movie_id == 1713 and (6 in keywords_id and 15 in keywords_id):
        movie_genre_id_pick = choice(keywords_id[1:])
    elif movie_id == 1713 and (6 in keywords_id):
        movie_genre_id_pick = 6
    elif movie_id == 1713 and (15 in keywords_id):
        movie_genre_id_pick = 15  

    elif movie_id == 79969 and (6 in keywords_id and 7 in keywords_id):
        movie_genre_id_pick = choice(keywords_id[1:])
    elif movie_id == 79969 and (6 in keywords_id):
        movie_genre_id_pick = 6
    elif movie_id == 79969 and (7 in keywords_id):
        movie_genre_id_pick = 7

    elif movie_id == 112659 and (2 in keywords_id and 19 in keywords_id):
        movie_genre_id_pick = choice(keywords_id[1:])
    elif movie_id == 112659 and (2 in keywords_id):
        movie_genre_id_pick = 2
    elif movie_id == 112659 and (19 in keywords_id):
        movie_genre_id_pick = 19    
        
    elif movie_id == 26106 and (19 in keywords_id and 17 in keywords_id):
        movie_genre_id_pick = choice(keywords_id[1:])
    elif movie_id == 26106 and (17 in keywords_id):
        movie_genre_id_pick = 17
    elif movie_id == 26106 and (19 in keywords_id):
        movie_genre_id_pick = 19 
    elif movie_id == 26106 and (18 in keywords_id):
        movie_genre_id_pick = 18        
            
    else:
        movie_genre_id_pick = -1           


    return movie_genre_id_pick     



def movie_user_profiling(movie_id,user_id):
    """profiling a movie by multiple users, profiling a user's taste
    """

    data = form_question(movie_id)
    keywords_id = [-1,data['k_id1'],data['k_id2']]


    movie_genre_id_pick = pick_keyword_for_movie(movie_id,keywords_id)      

    update_movie_profile(movie_id,movie_genre_id_pick,data['k_id1'],data['k_id2'])

    user_rated_genre = choice(keywords_id)
    print user_rated_genre
    add_update_user_preference(user_id,user_rated_genre,data['k_id1'],data['k_id2'])




users = User.query.all()

for i in range(100):
    for user in users:

        # romantic comedy. Punch drunk love. 3 genres given. Strongly fits in 2.
        movie_user_profiling(1308,user.user_id) 

        # Tremors. Comedy/Horror. strongly. 
        movie_user_profiling(1713,user.user_id)
        
        # [<Genre genre_id=7 genre=Crime>, <Genre genre_id=9 genre=Drama>],
        # needs to be categorized as comedy, thriller, 
        # Tier 2 : violent, tarantino, great plot
        movie_user_profiling(79969,user.user_id)  #pulp fiction 

        # Interstellar, genres: Adventure, Drama, Sci-fi,
        # Strong, adventure, scifi
        movie_user_profiling(112659, user.user_id)

        # Upstream color, drama, mystery, scifi
        # strong romantic, sci fi, mystery
        movie_user_profiling(26106, user.user_id)

clustering()        








    




    
