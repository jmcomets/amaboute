import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

engine = create_engine('sqlite:///:memory:')

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

class Dao:
    def registered_profiles(self):
        return Session().query(Profile).all()

    def add_message(self, nickname, message):
        session = Session()
        profile = get_or_create(session, Profile, nickname=nickname)
        session.add(Message(profile_id=profile.id, text=message))
        session.commit()

    def nickname_messages(self):
        for p in self.registered_profiles():
            yield p.nickname, [m.text for m in p.messages]


if __name__ == '__main__':
    Base.metadata.create_all(engine)
