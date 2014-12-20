""" 
    Setting up a new database with name app.db
    using values defined in file init_db.py
"""

import os.path
from config import basedir
from app import app
from init_db import init_db

# generating database with name 'app.db' 
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'app.db')
init_db(remove_file=os.path.join(basedir, 'app.db'))
