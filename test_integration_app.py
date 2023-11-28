import os
import tempfile
import pytest
from app import app, engine


@pytest.fixture
def client():
    """Create a test client for the app"""
    app.config["TESTING"] = True
    client = app.test_client()

    # Create a temporary database for testing
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.config['DATABASE']}"
    with app.app_context():
        engine.create_all()
    
    yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])

def test_index_route(client):
    """Test the index route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Show Quizers Profile' in response.data

def test_login_route(client):
    """Test the login route"""
    response = client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Log user in' in response.data  # Add assertions for the login behavior

# Add more test cases for other routes and functionalities as needed
