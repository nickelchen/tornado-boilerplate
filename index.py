# coding: UTF-8
import re

import os
import sys
path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'bundle')
if path not in sys.path:
    sys.path.insert(0, path)
    
import tornado.web
import tornado.wsgi
import unicodedata
from jinja2 import Template, Environment, FileSystemLoader
import filter
import session

from mongoengine import *
from handlers import *


class Application(tornado.wsgi.WSGIApplication):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/login", LoginHandler),
            (r"/register", RegisterHandler),
            (r"/logout", LogoutHandler),
        ]
        settings = dict(
            app_name=u"YOUR WEBSITE NAME",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="YOUR COOKIE SECRET",
            login_url="/login",
            session_secret='YOUR SESSION SECRET',
            session_dir=os.path.join(os.path.dirname(__file__), "tmp/session"), # USE YOUR OWN SESSION DIR
        )
        self.session_manager = session.TornadoSessionManager(settings["session_secret"], settings["session_dir"])
        tornado.wsgi.WSGIApplication.__init__(self, handlers, **settings)

        mongo_port = 27017
        mongo_host = "localhost"
        mongo_database = "YOUR LOCAL MONGO DATABASE NAME"
        mongo_user = ''
        mongo_password = ''
        # Bae env
        if 'SERVER_SOFTWARE' in os.environ:
            from bae.core import const
            from bae.api import logging
            logging.info('booting...')
            mongo_port = int(const.MONGO_PORT)
            mongo_host = const.MONGO_HOST
            mongo_database = 'YOUR BAE MONGO DATABASE NAME'
            mongo_user = const.MONGO_USER
            mongo_password = const.MONGO_PASS
        # Connection MongoDB
        connect(mongo_database, host=mongo_host, port=mongo_port, username=mongo_user, password=mongo_password)

from bae.core.wsgi import WSGIApplication
application = WSGIApplication(Application())

