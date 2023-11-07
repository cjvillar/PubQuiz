"""
script to check if models are correct

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, UserStats


engine = create_engine("sqlite:///pubQuiz.db")
Session = sessionmaker(bind=engine)

db_session = Session()

# query for User model
users = db_session.query(User).all()

if users:
    for user in users:
        print(f"User ID: {user.id}, Username: {user.username}")
else:
    print("No users found")

# query for UserStats model
user_stats = db_session.query(UserStats).all()

result = (
    db_session.query(
        User.username, UserStats.high_score, UserStats.last_score, UserStats.user_time
    )
    .join(UserStats, User.id == UserStats.user_id)
    .all()
)

if result:
    for username, high_score, last_score, user_time in result:
        print(
            f"Username: {username}, High Score: {high_score}, Last Score: {last_score}, Time: {user_time}"
        )
else:
    print("No user stats found")

db_session.close()
