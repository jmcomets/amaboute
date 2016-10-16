import os
import datetime
from functools import wraps
from contextlib import contextmanager
from sqlalchemy import create_engine, literal, func
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

db_name = os.environ.get('AMABOUTE_DB_NAME', 'messages.db')

engine = create_engine('sqlite:///%s' %  db_name)

Session = sessionmaker(bind=engine)

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    nickname = Column(String)

    messages = relationship('Message')

    def __repr__(self):
        return "<Profile(nickname='%s')>" % (self.nickname)

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now)
    text = Column(String)

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def using_session(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with session_scope() as session:
            return f(session, *args, **kwargs)
    return inner

@using_session
def get_registered_nicknames(s):
    return list(map(lambda p: p.nickname, s.query(Profile).all()))

@using_session
def get_history(s):
    for p in s.query(Profile).all():
        yield p.nickname, [(m.timestamp.timestamp(), m.text) for m in p.messages]

@using_session
def get_profile_messages(s, nickname):
    profile = s.query(Profile).filter(Profile.nickname == nickname).first()
    return list(map(lambda m: m.text, profile.messages))

@using_session
def add_message(s, nickname, message, timestamp=None):
    profile = get_or_create(s, Profile, nickname=nickname)
    if timestamp is not None:
        s.add(Message(profile_id=profile.id, text=message, timestamp=datetime.datetime.fromtimestamp(timestamp)))
    else:
        s.add(Message(profile_id=profile.id, text=message))

@using_session
def does_nickname_exist(s, nickname):
    q = s.query(Profile).filter(Profile.nickname == nickname)
    return s.query(literal(True)).filter(q.exists()).scalar() is True

@using_session
def merge_profiles(s, dest, source):
    source_profile = s.query(Profile).filter_by(nickname=source).first()
    dest_profile = get_or_create(s, Profile, nickname=dest)

    for message in s.query(Message).filter_by(profile_id=source_profile.id):
        message.nickname_id = dest_profile.id
    s.commit()

    s.delete(source_profile)

@using_session
def get_registered_profiles_and_message_count(s):
    nb_messages = func.count(Message.profile_id).label('nb_messages')
    return s.query(Profile.nickname, nb_messages).join(Profile.messages).group_by(Profile.nickname).all()

if __name__ == '__main__':
    print(get_registered_profiles_and_message_count())
    #Base.metadata.create_all(engine)
