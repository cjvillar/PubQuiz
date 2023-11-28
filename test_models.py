
import logging
from models import Base, engine, session, User, UserStats
import pytest

# Configure the logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@pytest.fixture(scope='module')
def setup():
    # create the database schema
    Base.metadata.create_all(engine)
    yield  # this allows the tests to run
    # drop the tables after tests are done
    Base.metadata.drop_all(engine)

def test_user_model(setup):
    # Create a test user
    user = User(username='test_user', passhash='test_password')
    session.add(user)
    session.commit()

    # query the database and assert the user exists
    queried_user = session.query(User).filter_by(username='test_user').first()
    assert queried_user is not None
    assert queried_user.passhash == 'test_password'

    # log successful user creation
    logger.info(f"User 'test_user' created successfully.")

def test_userstats_model(setup):
    try:
        # create a test UserStats object
        badges = ['badge1', 'badge2']
        user_stats = UserStats(user_id=1, last_score=100, high_score=200, user_time=50, badges=badges)
        session.add(user_stats)
        session.commit()

        # query the database and assert the UserStats object exists
        queried_stats = session.query(UserStats).filter_by(user_id=1).first()
        assert queried_stats is not None
        assert queried_stats.last_score == 100
        assert queried_stats.high_score == 200
        assert queried_stats.get_badges() == badges

        # log successful UserStats creation
        logger.info(f"UserStats for User ID {queried_stats.id} created successfully.")
    except AssertionError as e:
        # log an error if any assertion fails
        logger.error(f"Test failed: {e}")
        # raise the exception to mark the test as failed
        raise e
    except Exception as e:
        # log an error for any other exceptions raised during the test
        logger.error(f"An error occurred: {e}")
        # raise the exception to mark the test as failed
        raise e

