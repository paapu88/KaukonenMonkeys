# -*- coding: utf-8 -*-
"""
A demo version of a database application by markus.kaukonen@iki.fi
(python, flask, sql-alchemy, bootstrap) 
- To run tests: *py.test*  (file running is test_monkeys.py)
- To initialize the database: *python run_init_app_db.py*
- To run the actual server: *python run.py*
"""

# all the imports
import sqlite3, os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, render_template_string
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config import POSTS_PER_PAGE
from app import app, db
from models import Monkey, Friend
from forms import MonkeyForm, SelectOneMonkeyForm, SelectManyMonkeyForm

class config_pagination():
    """ class to memorize by which criteria we paginate """
    sort_by = 'name'

@app.route('/')
@app.route('/list_monkeys', methods=['GET', 'POST'])
@app.route('/list_monkeys/<int:page>', methods=['GET', 'POST'])
@app.route('/list_monkeys/<int:page>/<sort_by>', methods=['GET', 'POST'])
def list_monkeys(page=1, sort_by=None):
    """ 
    Main index, renders default layout which gives choice-bar 
    Additionally lists monkeys in the database 
    (name, best friend, # of friends)
    """
    from sqlalchemy import desc

    if sort_by:
        config_pagination.sort_by = sort_by
    else:
        sort_by = config_pagination.sort_by

    monkeys = Monkey.query.all()
    if sort_by == 'name':
        monkeys = Monkey.query.order_by(Monkey.name)
    elif sort_by == 'best_friend':
        #monkeys = Monkey.query.join(Friend, Monkey.best_friend).
        #order_by(Friend.name)
        monkeys = Monkey.query.order_by(Monkey.best_friend_name)
    else:
        #http://stackoverflow.com/questions/10831057/
        #flask-sqlalchemy-order-shows-by-number-of-followers
        monkeys = Monkey.query.order_by(desc(Monkey.lenfriends))
    if monkeys is None:
        flash('No monkeys in the database!' )
        return redirect(url_for('list_monkeys'))
    monkeypages = monkeys.paginate(page, POSTS_PER_PAGE, True)
    return render_template('list_monkeys.html', monkeypages = monkeypages)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """ Adds a monkey to the database """
    form = MonkeyForm()
    if form.validate_on_submit():
        u = Monkey(
            name=form.name.data, age=form.age.data, email=form.email.data)
        db.session.add(u)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect('/')
    return render_template('add.html', form=form)

@app.route('/edit', methods=['GET', 'POST'])
@app.route('/edit/<int:current_monkey_id>', methods=['GET', 'POST'])
def edit(current_monkey_id):
    """ Edit the data of a single monkey """
    form = MonkeyForm()
    monkey = Monkey.query.get(current_monkey_id)
    form = MonkeyForm(obj=monkey)
    if form.validate_on_submit():
        monkey.name=form.name.data
        monkey.age = form.age.data
        monkey.email = form.email.data
        db.session.commit()
        current_monkey_id = None
        flash('Entry modified successfully !')
        return redirect('/')
    return render_template('edit.html', form=form,
                           current_monkey_id=current_monkey_id)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    """ 
    Delete a monkey from the database.
    Additionally, remove all other references to the deleted monkey.
    """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    form = SelectManyMonkeyForm()
    form.example.choices=monkeynames
    form.example.label=u'Select a Monkey/ Monkeys for Deletion'    
    if request.method == 'POST':
        delete_monkey = Monkey.query.filter(
            Monkey.name.in_(form.example.data)).first()
        #1-remove the deleted monkey as 'best friend' of anybody
        monkeys = Monkey.query.filter(
            Monkey.best_friend_name.in_(form.example.data))
        for monkey in monkeys:
            monkey.best_friend_name = None
        #2-remove entries in the Friends-table that have the 
        #deleted monkey as a friend. Also update the counter of 
        #the number of friends.
        #monkey  = Monkey.query.filter(Monkey.name.in_(form.example.data))
        friends = Friend.query.filter_by(monkey_id=delete_monkey.id)
        for friend in friends:
            db.session.delete(friend)
        #3-remove entries in the friend table that have the deleted monkey.
        # Also update the counter of the number of friends.
        friends = Friend.query.filter(Friend.name.in_(form.example.data))
        for friend in friends:
            friend.to_monkey.lenfriends = friend.to_monkey.lenfriends - 1
            db.session.delete(friend)

        #4-remove the actual monkey
        db.session.delete(delete_monkey)
        db.session.commit()
        return redirect('/')
    return render_template('delete.html', form=form)

@app.route('/friend2', methods=['GET', 'POST'])
@app.route('/friend2/<int:current_monkey_id>', methods=['GET', 'POST'])
def friend2(current_monkey_id):
    """ Select friends for a monkey """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    current_monkey = Monkey.query.get(current_monkey_id)
    oldfriends = current_monkey.friends
    oldfriendnames = [oldfriend.name for oldfriend in oldfriends]
    oldfriendnames.sort()
    oldfriendnames.append(None)
    form = SelectManyMonkeyForm(example=oldfriendnames)
    form.example.label='Select Friends for ' + current_monkey.name + \
        ' (old friends are pre-selected)'
    form.example.choices=monkeynames

    if request.method == 'POST':
        #update number of friends
        monkeys = Monkey.query.all()

        #check for no friends at all for this monkey
        for name in form.example.data:
            if (name.find('None')!=-1):
                current_monkey.lenfriends = 0
                form.example.data = []

        new_friends = Monkey.query.filter(Monkey.name.in_(form.example.data))
        old_friends = Monkey.query.filter(Monkey.name.in_(oldfriendnames))


        #Add new friends, this is a two way relation
        #that is friends are friends in both ways
        for new_friend in new_friends:
            if (new_friend.name not in oldfriendnames):
                friend = Friend(
                    name=new_friend.name, monkey_id = current_monkey_id)
                db.session.add(friend)
                # the other way round, but not doublecount
                #being friend with oneself
                if (new_friend.name != current_monkey.name):
                    friend2 = Friend(
                        name=current_monkey.name, monkey_id = new_friend.id)
                    db.session.add(friend2)
        #delete old friends that are not new friends
        deletenames = list((set(oldfriendnames) | set(form.example.data)) - \
            set(form.example.data))
        deletenames.remove(None)
        friends1 = Friend.query.filter(Friend.name.in_(deletenames))
        friends2 = Friend.query.filter_by(monkey_id=current_monkey.id)
        delete_friends = friends1.intersect(friends2)
        for friend in delete_friends:
            db.session.delete(friend)
        #also delete the other way round 
        del_friends = Monkey.query.filter(Monkey.name.in_(deletenames))
        deletefriend_ids = [delfriend.id for delfriend in del_friends]

        friends1 = Friend.query.filter(Friend.monkey_id.in_(deletefriend_ids))
        friends2 = Friend.query.filter_by(name=current_monkey.name)
        delete_friends = friends1.intersect(friends2)
        for friend in delete_friends:
            db.session.delete(friend)
        db.session.commit()
        #update number of friends
        monkeys = Monkey.query.all()
        for monkey in monkeys:
            monkey.lenfriends = len(monkey.friends)
        db.session.commit()
        #check whether we should delete best friend if a friend has been deleted
        deletenames = [dn.encode('utf8') for dn in deletenames]
        if current_monkey.best_friend_name in deletenames:
            current_monkey.best_friend_name = None
        for monkey in del_friends:
            if monkey.best_friend_name == current_monkey.name:
                monkey.best_friend_name = None
        db.session.commit()

        return redirect('/')
    return render_template('friend2.html', form=form, 
                           current_monkey_id=current_monkey_id)


@app.route('/best_friend2', methods=['GET', 'POST'])
@app.route('/best_friend2/<int:current_monkey_id>', methods=['GET', 'POST'])
def best_friend2(current_monkey_id):
    """ Select best friend for a given monkey """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    current_monkey = Monkey.query.get(current_monkey_id)
    form = SelectOneMonkeyForm()
    form.example.label='Select Best Friend for '+current_monkey.name    
    form.example.choices=monkeynames

    if request.method == 'POST':
        friend1 = Friend.\
                 query.filter(Friend.name==form.example.data, 
                              Friend.monkey_id==current_monkey_id).first()
        current_monkey.best_friend_name = form.example.data
        if not(friend1):
            #best friend was not in friends, we must add it there
            friend = Friend(name=form.example.data, 
                            monkey = current_monkey)
            db.session.add(friend)
            #also the other way round
            if (form.example.data != current_monkey.name):
                friend_monkey = \
                    Monkey.query.filter_by(name=friend.name).first()
                friend = Friend(name=current_monkey.name, 
                                monkey = friend_monkey)
                db.session.add(friend)
            #update number of friends
            monkeys = Monkey.query.all()
            for monkey in monkeys:
                monkey.lenfriends = len(monkey.friends)
        db.session.commit()
        return redirect('/')
    return render_template('best_friend2.html', form=form, 
                           current_monkey_id = current_monkey_id)







