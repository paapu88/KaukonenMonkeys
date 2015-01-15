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
from app.models import Monkey, Friend
from app.forms import MonkeyForm, SelectOneMonkeyForm, SelectManyMonkeyForm

def list_monkeys(page=1, sort_by="name"):
    """ 
    Main index, renders default layout which gives choice-bar 
    Additionally lists monkeys in the database 
    (name, best friend, # of friends)
    """
    from sqlalchemy import desc

    monkeys = Monkey.query.all()
    for monkey in monkeys:
        print "MNAAalku, LEN", monkey.name, len(monkey.friends), monkey.friends
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

def add(name, age, email):
    """ Adds a monkey to the database """
    if (1==1):
        u = Monkey(
            name=name, age=age, email=email)
        db.session.add(u)
        db.session.commit()
    return 

def edit(current_monkey_id, name, age, email):
    """ Edit the data of a single monkey """
    monkey = Monkey.query.get(current_monkey_id)
    if (True):
        monkey.name=name
        monkey.age = age
        monkey.email = email
        db.session.commit()
        current_monkey_id = None
    return 

def delete(name):
    """ 
    Delete a monkey from the database.
    Additionally, remove all other references to the deleted monkey.
    """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    print monkeynames
    if 1 == 1:
        delete_monkey = Monkey.query.filter(
            Monkey.name.in_(name)).first()

        print delete_monkey
        #1-remove the deleted monkey as 'best friend' of anybody
        monkeys = Monkey.query.filter(
            Monkey.best_friend_name.in_(name))
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
        friends = Friend.query.filter(Friend.name.in_(name))
        for friend in friends:
            print "FF", friend.name
            friend.to_monkey.lenfriends = friend.to_monkey.lenfriends - 1
            db.session.delete(friend)

        #4-remove the actual monkey
        db.session.delete(delete_monkey)
        db.session.commit()
    return

def friend2(current_monkey_id, new_friend_names):
    """ Select friends for a monkey """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    current_monkey = Monkey.query.get(current_monkey_id)
    oldfriends = current_monkey.friends
    oldfriendnames = [oldfriend.name for oldfriend in oldfriends]
    oldfriendnames.sort()
    oldfriendnames.append(None)
    #form = SelectManyMonkeyForm(example=oldfriendnames)
    #form.example.label='Select Friends for ' + current_monkey.name + \
    #    ' (old friends are pre-selected)'
    #form.example.choices=monkeynames

    if True:
        #update number of friends
        monkeys = Monkey.query.all()
        for monkey in monkeys:
            print "MNalku, LEN", monkey.name, len(monkey.friends), monkey.friends

        #check for no friends at all for this monkey
        for name in new_friend_names:
            if (name.find('None')!=-1):
                current_monkey.lenfriends = 0
                new_friend_names = []

        new_friends = Monkey.query.filter(Monkey.name.in_(new_friend_names))
        old_friends = Monkey.query.filter(Monkey.name.in_(oldfriendnames))

        for new_friend in new_friends:
            print "new_friend", new_friend.name
        for old_friend in old_friends:
            print "old_friend", old_friend.name


        #Add new friends, this is a two way relation
        #that is friends are friends in both ways
        for new_friend in new_friends:
            if (new_friend.name not in oldfriendnames):
                friend = Friend(
                    name=new_friend.name, monkey_id = current_monkey_id)
                print "new friend to", current_monkey.name, current_monkey_id
                print "new friend is", friend.name
                print "pointing to", friend.monkey_id
                db.session.add(friend)
                # the other way round, but not doublecount
                #being friend with oneself
                if (new_friend.name != current_monkey.name):
                    print "adding friend2"
                    friend2 = Friend(
                        name=current_monkey.name, monkey_id = new_friend.id)
                    db.session.add(friend2)
        #delete old friends that are not new friends
        deletenames = list((set(oldfriendnames) | set(new_friend_names)) - \
            set(new_friend_names))
        deletenames.remove(None)
        print "aa:",list((set(oldfriendnames) | set(new_friend_names)))
        print "dd:",oldfriendnames, new_friend_names
        print "deletenames", deletenames
        friends1 = Friend.query.filter(Friend.name.in_(deletenames))
        friends2 = Friend.query.filter_by(monkey_id=current_monkey.id)
        delete_friends = friends1.intersect(friends2)
        for friend in delete_friends:
            print "1friend--del", friend.name, friend.monkey_id
            db.session.delete(friend)
        #also delete the other way round 
        del_friends = Monkey.query.filter(Monkey.name.in_(deletenames))
        deletefriend_ids = [delfriend.id for delfriend in del_friends]

        print "deletefriend_ids", deletefriend_ids
        friends1 = Friend.query.filter(Friend.monkey_id.in_(deletefriend_ids))
        friends2 = Friend.query.filter_by(name=current_monkey.name)
        for fr in friends1:
            print "del21::",fr.name, fr.monkey_id
        for fr in friends2:
            print "del22::",fr.name, fr.monkey_id
        delete_friends = friends1.intersect(friends2)
        for friend in delete_friends:
            print "2friend--del", friend.name, friend.monkey_id
            db.session.delete(friend)
        db.session.commit()
        #update number of friends
        monkeys = Monkey.query.all()
        for monkey in monkeys:
            monkey.lenfriends = len(monkey.friends)
            print "MN, LEN", monkey.name, len(monkey.friends), monkey.friends
        db.session.commit()
        #check whether we should delete best friend if a friend has been deleted
        deletenames = [dn.encode('utf8') for dn in deletenames]
        print "current_monkey.best_friend_name in deletenames",\
            current_monkey.best_friend_name, deletenames
        if current_monkey.best_friend_name in deletenames:
            print "DEL BF"
            current_monkey.best_friend_name = None
        for monkey in del_friends:
            if monkey.best_friend_name == current_monkey.name:
                monkey.best_friend_name = None
        db.session.commit()
    return 

def best_friend2(current_monkey_id, new_best_friend_name):
    """ Select best friend for a given monkey """
    monkeys = Monkey.query.all()
    monkeynames = [(monkey.name,monkey.name) for monkey in monkeys]
    monkeynames.sort()
    current_monkey = Monkey.query.get(current_monkey_id)
    #form = SelectOneMonkeyForm()
    #form.example.label='Select Best Friend for '+current_monkey.name    
    #form.example.choices=monkeynames

    if True:
        friend1 = Friend.\
                 query.filter(Friend.name==new_best_friend_name, 
                              Friend.monkey_id==current_monkey_id).first()
        current_monkey.best_friend_name = new_best_friend_name
        if not(friend1):
            #best friend was not in friends, we must add it there
            friend = Friend(name=new_best_friend_name, 
                            monkey = current_monkey)
            db.session.add(friend)
            #also the other way round
            if (new_best_friend_name != current_monkey.name):
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
    return 







