import os
# pagination
POSTS_PER_PAGE = 4
basedir = os.path.abspath(os.path.dirname(__file__))

USERNAME='admin'
PASSWORD='default'
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                           '?check_same_thread=False')

#if os.environ.get('DATABASE_URL') is None:
#    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
#                               '?check_same_thread=False')
#else:
#    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
