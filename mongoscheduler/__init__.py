"""
A celerybeat scheduler that uses MongoDB for remembering when it ran what.
"""

import logging

from celery.beat import Scheduler
from django.conf import settings
import pymongo

try:
    import cPickle as pickle
except ImportError:
    import pickle


class MongoScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        self.uri = settings.CELERY_MONGO_SCHEDULER_URI
        logging.debug('MongoScheduler connecting to %s' % self.uri)
        parsed = pymongo.uri_parser.parse_uri(self.uri)
        conn = pymongo.Connection(*parsed['nodelist'][0])
        db = conn[parsed['database']]
        self.collection = db[parsed['collection']]

        # No two documents may have the same 'key'
        self.collection.ensure_index('key', unique=True)

        # If there's not already an 'entries' key, create one.
        entries = self.collection.find_one({'key': 'entries'})
        if not entries:
            self.entries = {}
            self.sync()
        else:
            self.entries = pickle.loads(str(entries['entries']))
        Scheduler.__init__(self, *args, **kwargs)

    def setup_schedule(self):
        self.merge_inplace(self.app.conf.CELERYBEAT_SCHEDULE)
        self.install_default_entries(self.schedule)
        self.sync()

    def get_schedule(self):
        return self.entries

    def set_schedule(self, schedule):
        self.entries = schedule
        self.sync()
    schedule = property(get_schedule, set_schedule)

    def sync(self):
        self.collection.update({'key': 'entries'},
                               {'key': 'entries', 'entries':
                                pickle.dumps(self.entries)},
                                upsert=True)

    def close(self):
        self.sync()
        self.collection.database.connection.close()

    @property
    def info(self):
        return self.uri
