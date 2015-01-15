import os

# pagination
POSTS_PER_PAGE = 3
basedir = os.path.abspath(os.path.dirname(__file__))

USERNAME='admin'
PASSWORD='default'
DEBUG = False
SECRET_KEY = 'Laa12Kis3'

SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                           '?check_same_thread=False')

