__author__ = 'madhu'
from api.api_settings import FILM_URL_API
from api.api_settings import GOOGLE_MAP_NAME_LAT_LON_API
from api.api_settings import GOOGLE_MAP_NAME_LAT_LON_API_KEY
import urllib2
import json as simplejson
from django.http import HttpResponse
from django.core.cache import caches
from mongo_wrapper import MongoWrapper
from datetime import datetime
import time
from django.views.generic import ListView

mongo_obj = MongoWrapper()
film_mongo_connect = mongo_obj.get_connection()
rediscon = caches['localcache']


def current_time_to_string(systemtime):
    current_time = ('%s' % (systemtime)).split('.')[0]
    current_time_text = datetime.fromtimestamp(
        int(current_time)).strftime('%Y-%m-%d')
    return current_time_text


class FilmSearchAPI(ListView):
    def __init__(self):
        self.actor_list = []
        self.director_list = []
        self.production_house_list = []
        self.film_name_list = []
        self.writer_list = []

    def get_queryset(self):
        return self.film_data_limited()

    def get(self, params_wsgi):
        """
        Get URLS Dispatcher
        :param params_wsgi:
        :return:
        """
        if params_wsgi.path == '/filmSearchAPI/get_values_for_auto_suggest':
            return self.get_values_for_auto_suggest()

    def get_whole_film_data(self):
        req = urllib2.Request(FILM_URL_API)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def post(self):
        pass

    def film_data_limited(self):
        req = urllib2.Request(FILM_URL_API) + '?$limit=100'
        response = urllib2.urlopen(req).read()
        response_json = simplejson.loads(response)
        return HttpResponse(response_json)

    def search_params(self, column_name, column_val):
        req = urllib2.Request(FILM_URL_API) + '?$where=' + column_name + '=' + column_val + ''
        response = urllib2.urlopen(req).read()
        response_json = simplejson.loads(response)
        return HttpResponse(response_json)

    def get_auto_values_for_film(self, column_name, column_value):
        if column_name == 'title':
            # If user search by title , search through cache
            film_data = rediscon.get(column_value)
            if film_data:
                return HttpResponse(film_data)
        film_data = film_mongo_connect.find_one({column_name: column_value})
        return HttpResponse(film_data)

    def get_values_for_auto_suggest(self):
        current_time = current_time_to_string(time.time()
                                              )
        film_json = rediscon.get(current_time)
        if not film_json:
            film_json = film_mongo_connect.find()
        for film in film_json:
            actor_1_name = film.get('actor_1', '')
            actor_2_name = film.get('actor_2', '')
            actor_3_name = film.get('actor_3', '')
            production_company = film.get('production_company', '')
            director = film.get('director', '')
            writer = film.get('writer', '')
            film_name = film.get('title', '')
            if actor_1_name not in self.actor_list:
                self.actor_list.append(actor_1_name)
            if actor_2_name not in self.actor_list:
                self.actor_list.append(actor_2_name)
            if actor_3_name not in self.actor_list:
                self.actor_list.append(actor_3_name)
            if production_company not in self.production_house_list:
                self.production_house_list.append(production_company)
            if director not in self.director_list:
                self.director_list.append(director)
            if writer not in self.writer_list:
                self.writer_list.append(writer)
            if film_name not in self.film_name_list:
                self.film_name_list.append(film_name)
        result_dict = {'actor': self.actor_list, 'production_company': self.production_house_list,
                       'director': self.director_list,
                       'writer': self.writer_list, 'title': self.film_name_list
                       }
        return HttpResponse(simplejson.dumps(result_dict))

    def get_location_json(self, locations=[]):
        import pdb;
        pdb.set_trace()
        for location in locations:
            location = location.replace(' ', '%20')
            req = urllib2.Request(GOOGLE_MAP_NAME_LAT_LON_API + location + GOOGLE_MAP_NAME_LAT_LON_API_KEY)
            response = urllib2.urlopen(req)
        return (response.read())
