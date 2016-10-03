__author__ = 'madhu'
from django.core.management.base import BaseCommand
import time
from challenge.views import FilmSearchAPI
from django.core.cache import caches
from challenge.mongo_wrapper import MongoWrapper
rediscon = caches['localcache']
from datetime import datetime
import copy
from challenge.views import current_time_to_string
import logging
logger = logging.getLogger('whiz_challenge')
logger_stats = logging.getLogger('whiz_challenge_stats')

def daily_read_film_data():
    """
    This function runs on daily basis and grab and reads all the data from remote server
    :return:
    """
    mongo_obj= MongoWrapper()
    film_mongo_connect = mongo_obj.get_connection()
    current_time_text = current_time_to_string(time.time())
    import pdb; pdb.set_trace()
    filmsearch_obj = FilmSearchAPI()
    film_json = filmsearch_obj.get_whole_film_data()
    # Deletes the old redis data if it missed from without time
    #out operation
    delete_old_cache_item(film_json)
    # Writes the whole json data
    rediscon.set(current_time_text, film_json)
    # Writing it into redis cache
    for filmobj in film_json:
        locations = []
        title_name = filmobj.get('title', '')
        if rediscon.get(title_name):
            place_name = rediscon.get(title_name).get('locations')
            location = filmobj.get('locations')
            if location:
                if isinstance(place_name, unicode):
                    locations.append(location)
                    place_name = copy.copy(locations)
                else:
                    if not place_name:
                        place_name = []
                    place_name.append(location)
                filmobj['locations'] = copy.copy(place_name)
            rediscon.set(title_name, copy.copy(filmobj))
            film_mongo_connect.update({"title": title_name},{ "$set":{'locations': filmobj.get('locations', [])}})
        else:
            filmobj['location_dict'] = copy.copy(
                filmsearch_obj.get_location_json(locations=[filmobj.get('locations', '')]))
            rediscon.set(title_name, copy.copy(filmobj))
            film_mongo_connect.insert_one(copy.copy(filmobj))

def delete_old_cache_item(film_json):
    for filmobj in film_json:
        title_name = filmobj.get('title', '')
        logger_stats.info('%s\t%s\t%s\t%s\t'%(title_name, 'Deleting from Redis', '',''))
        rediscon.delete(title_name)

class Command(BaseCommand):
    def handle(self, *args, **options):
        daily_read_film_data()


