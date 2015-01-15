

def init_db(remove_file=None):
    """ 
    Initialise a database with some values 
    for testing and playing around 
    """
    from app import db
    from config import basedir
    import os.path
    from app.models import Monkey, Friend

    if remove_file:
        try:
            os.remove(remove_file)
        except:
            pass

    db.create_all()

    admin = Monkey(name='admin', age=12, email='admin@example.com')
    guest = Monkey(name='guest', age=12, email='guest@example.com')
    veeti = Monkey(name='veeti', age=3, email='veeti@example.com')
    kerttu = Monkey(name='kerttu', age=7, email='kerttu@example.com')
    kukka = Monkey(name='kukka', age=10, email='kukka@example.com')
    db.session.add(admin)
    db.session.add(guest)
    db.session.add(veeti)
    db.session.add(kerttu)
    db.session.add(kukka)
    db.session.commit()

    adminf = Friend(name='guest', to_monkey = admin)
    guestf = Friend(name='admin', to_monkey = guest)
    veetif1 = Friend(name='kerttu', to_monkey = veeti)
    veetif2 = Friend(name='kukka', to_monkey = veeti)
    kerttuf = Friend(name='veeti', to_monkey = kerttu)
    kukkaf = Friend(name='veeti', to_monkey = kukka)
    kukkaf2 = Friend(name='kukka', to_monkey = kukka)
    db.session.add(adminf)
    db.session.add(guestf)
    db.session.add(veetif1)
    db.session.add(veetif2)
    db.session.add(kerttuf)
    db.session.add(kukkaf)
    db.session.add(kukkaf2)
    db.session.commit()

    m1 = Monkey.query.get(1)
    m1.lenfriends = 1
    m1.best_friend_name = "guest"
    m2 = Monkey.query.get(2)
    m2.lenfriends = 1
    m2.best_friend_name = "admin"
    m3 = Monkey.query.get(3)
    m3.lenfriends = 2
    m3.best_friend_name = "kerttu"
    m4 = Monkey.query.get(4)
    m4.lenfriends = 1
    m4.best_friend_name = "veeti"
    m5 = Monkey.query.get(5)
    m5.lenfriends = 2
    m5.best_friend_name = "veeti"

    db.session.commit()


