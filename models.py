import datetime
from sqlalchemy import create_engine, literal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

__all__ = ('add_message', 'get_registered_profiles', 'get_history',
           'does_nickname_exist')

Base = declarative_base()

engine = create_engine('sqlite:///messages.db')

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

Session = sessionmaker(bind=engine)

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def add_message(nickname, message, timestamp=None):
    session = Session()
    profile = get_or_create(session, Profile, nickname=nickname)
    session.add(Message(profile_id=profile.id, text=message, timestamp=datetime.datetime.fromtimestamp(timestamp)))
    session.commit()

def get_registered_profiles():
    return Session().query(Profile).all()

def get_history():
    for p in get_registered_profiles():
        yield p.nickname, [m.text for m in p.messages]

def does_nickname_exist(nickname):
    session = Session()
    q = session.query(Profile).filter(Profile.nickname == nickname)
    return session.query(literal(True)).filter(q.exists()).scalar() is True

def merge_profiles(dest, source):
    session = Session()
    dest_profile = get_or_create(session, Profile, nickname=dest)
    source_profile = session.query(Profile).filter_by(nickname=source).first()
    for message in session.query(Message).filter_by(profile_id=source_profile.id):
        message.nickname_id = dest_profile.id
    session.delete(source_profile)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
