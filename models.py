from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()


engine = create_engine("sqlite:///pubQuiz.db")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    passhash = Column(String, nullable=False)


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    last_score = Column(Integer)
    high_score = Column(Integer)
    user_time = Column(Integer)
    badges = Column(String(255))

    def __init__(self, user_id, last_score, high_score, user_time, badges):
        self.user_id = user_id
        self.last_score = last_score
        self.high_score = high_score
        self.user_time = user_time
        self.badges = json.dumps(badges)  # serialize the list to a JSON string

    def get_badges(self):
        return json.loads(self.badges)  # deserialize the JSON string back to a lis


# create the tables in the database
Base.metadata.create_all(engine)

# create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()
