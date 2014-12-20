# -*- coding: utf-8 -*-
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

current_monkey_id = None

heroku = Heroku(app)

@app.route('/')
@app.route('/list_monkeys', methods=['GET', 'POST'])
@app.route('/list_monkeys/<int:page>', methods=['GET', 'POST'])
@app.route('/list_monkeys/<int:page>/<sort_by>', methods=['GET', 'POST'])
def list_monkeys(page=1, sort_by="name"):
    """ 
    Main index, renders default layout which gives choice-bar 
    Additionally lists monkeys in the database 
    (name, best friend, # of friends)
    """
    if sort_by == 'name':
        monkeys = Monkey.query.order_by(Monkey.name)
    elif sort_by == 'best_friend':
        #monkeys = Monkey.query.join(Friend, Monkey.best_friend).
        #order_by(Friend.name)
        monkeys = Monkey.query.order_by(Monkey.best_friend_name)
    else:
        #http://stackoverflow.com/questions/10831057/
        #flask-sqlalchemy-order-shows-by-number-of-followers
        monkeys = Monkey.query.order_by(Monkey.lenfriends)
    if monkeys is None:
        flash('No monkeys in the database!' )
        return redirect(url_for('list_monkeys'))
    monkeypages = monkeys.paginate(page, POSTS_PER_PAGE, True)
    return render_template('list_monkeys.html', monkeypages = monkeypages)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """ Adds a monkey to the database """
    if not session.get('logged_in'):
        abort(401)
    form = MonkeyForm()
    if form.validate_on_submit():
        u = Monkey(
            name=form.name.data, age=form.age.data, email=form.email.data)
        db.session.add(u)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect('/')
    return render_template('add.html', form=form)

@app.route('/view_profile', methods=['GET', 'POST'])
def view_profile():
    """ Select a monkey for viewing """
    global current_monkey_id 

    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    form = SelectOneMonkeyForm()
    form.example.choices=monkeynames
    form.example.label=u'Select a Monkey for Viewing'

    if request.method == 'POST':
        monkey = Monkey.query.filter_by(name=form.example.data).first()
        current_monkey_id = monkey.id
        return redirect('/view')
    else:
        return render_template('view_profile.html', form=form)

@app.route('/view')
def view():
    """ View  monkey  profile. The profile page shows 
    the name, age and email of a monkey.
    """
    monkey = Monkey.query.get(current_monkey_id)
    entry = dict(name=monkey.name, age=monkey.age, email=monkey.email)
    return render_template('list_single_monkey.html', entry=entry)


@app.route('/select_one_from_list', methods=['GET', 'POST'])
def select_one_from_list():
    """ Select one monkey for editing """
    global current_monkey_id

    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    form = SelectOneMonkeyForm()
    form.example.choices=monkeynames
    form.example.label=u'Select a Monkey'

    if request.method == 'POST':
        monkey = Monkey.query.filter_by(name=form.example.data).first()
        current_monkey_id = monkey.id
        return redirect('/edit')
    else:
        return render_template('select_one_from_list.html', form=form)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    """ Edit the data of a single monkey """
    global current_monkey_id
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
    return render_template('edit.html', form=form)

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
            print "friend", friend
            db.session.delete(friend)
        #3-remove entries in the friend table that have the deleted monkey.
        # Also update the counter of the number of friends.
        friends = Friend.query.filter(Friend.name.in_(form.example.data))
        for friend in friends:
            print "friend", friend
            friend.to_monkey.lenfriends = friend.to_monkey.lenfriends - 1
            db.session.delete(friend)

        #4-remove the actual monkey
        db.session.delete(delete_monkey)
        db.session.commit()
        return redirect('/')
    return render_template('delete.html', form=form)

@app.route('/friend1', methods=['GET', 'POST'])
def friend1():
    """ Select a monkey for which one defines its friends """
    global current_monkey_id 

    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    form = SelectOneMonkeyForm()
    form.example.choices=monkeynames
    form.example.label=u'Select a Monkey for Adding Friends'

    if request.method == 'POST':
        monkey = Monkey.query.filter_by(name=form.example.data).first()
        current_monkey_id = monkey.id
        return redirect('/friend2')
    else:
        return render_template('friend1.html', form=form)

@app.route('/friend2', methods=['GET', 'POST'])
def friend2():
    """ Select friends for a monkey """
    global current_monkey_id 
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    current_monkey = Monkey.query.get(current_monkey_id)
    friends = current_monkey.friends
    friendnames = [friend.name for friend in friends]
    friendnames.sort()
    form = SelectManyMonkeyForm(example=friendnames)
    form.example.label='Select Friends for ' + current_monkey.name + \
        ' (old friends are pre-selected)'
    form.example.choices=monkeynames

    #First delete old friends of the monkey.
    if request.method == 'POST':
        records = Monkey.query.filter(Monkey.name.in_(form.example.data))
        for delete in current_monkey.friends:
            db.session.delete(delete)
        db.session.commit()
        current_monkey.lenfriends = records.count()
        #check also is the old best friend among the new friends,
        #if not set best friend to None
        found = False
        for record in records:
            print "recc:", record.name
            friend = Friend(name=record.name, monkey_id = current_monkey_id)
            if current_monkey.best_friend_name == record.name:
                found = True
            db.session.add(friend)
        if not(found):
            current_monkey.best_friend_name = None
        db.session.commit()
        return redirect('/')
    return render_template('friend2.html', form=form)

@app.route('/best_friend1', methods=['GET', 'POST'])
def best_friend1():
    """ Select a monkey for which one defines its best friend """
    global current_monkey_id 

    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    form = SelectOneMonkeyForm()
    form.example.choices=monkeynames
    form.example.label=u'Select a Monkey for Adding a Best Friend'

    if request.method == 'POST':
        monkey = Monkey.query.filter_by(name=form.example.data).first()
        current_monkey_id = monkey.id
        return redirect('/best_friend2')
    else:
        return render_template('best_friend1.html', form=form)

@app.route('/best_friend2', methods=['GET', 'POST'])
def best_friend2():
    """ Select best friend for a given monkey """
    global current_monkey_id 
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
        if friend1:
            #if best friend is already a friend we do not touch friends
            current_monkey.best_friend_name = form.example.data
        else:
            #best friend was not in friends, we must add it there
            friend = Friend(name=form.example.data, 
                            monkey = current_monkey)
            db.session.add(friend)
            current_monkey.best_friend_name = form.example.data
            if current_monkey.lenfriends:
                current_monkey.lenfriends = current_monkey.lenfriends + 1
            else:
                current_monkey.lenfriends = 1
        db.session.commit()
        return redirect('/')
    return render_template('best_friend2.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('list_monkeys'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('/'))






