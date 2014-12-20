#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import Monkey, Friend
from init_db import init_db

class TestCase(unittest.TestCase):
    def setUp(self):
        test_db_name = 'test.db'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'sqlite:///' + os.path.join(basedir, test_db_name)
        self.app = app.test_client()
        #generate data for testing, the name of the database is given above as 
        #'test.db'
        init_db(os.path.join(basedir, test_db_name))

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_add(self):
        """ 
        Test that the number of users has increased by one and the 
        last user has the email address 'Jack@gmail.com',
        after we have added one user 
        """

        len_before = len(Monkey.query.all())
        u = Monkey(name='Jack', age=4, email='Jack@gmail.com')
        db.session.add(u)
        db.session.commit()
        len_after = len(Monkey.query.all())
        email = Monkey.query.get(len_after).email

        assert email == 'Jack@gmail.com'
        assert (len_after - len_before) == 1

    def test_delete(self):
        """ 
        Test deleting a monkey with a name 'veeti'.
        Number of monkeys should decrease by one and the
        deleted monkey should not be found in the database anymore.
        """

        len_before = len(Monkey.query.all())
        monkey_before = Monkey.query.filter_by(name='veeti').first().name
        records = Monkey.query.filter(Monkey.name.in_([u'veeti']))
        for record in records:
            print "deleting record", record
            db.session.delete(record)
            db.session.commit()
        len_after = len(Monkey.query.all())
        monkey_after = Monkey.query.filter_by(name='veeti').first()

        assert monkey_before == 'veeti'
        assert monkey_after == None
        assert (len_after - len_before) == -1



if __name__ == '__main__':
    unittest.main()


