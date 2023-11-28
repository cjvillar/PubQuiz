from helpers import apology, login_required
from flask import Flask
from app import Session

# create a Flask app for testing purposes
app = Flask(__name__)
app.secret_key = 'test_secret_key'

def test_apology():
    message = "Test Apology Message"
    code = 404

    result = apology(message, code)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[1] == code
    assert message in result[0]

def test_login_required():
    @app.route('/')
    @login_required
    def protected_route():
        return 'Protected Route'

    with app.test_client() as client:
        # user not logged in, should be redirected to /login
        response = client.get('/')
        assert response.status_code == 302  # 302 is the status code for redirection

        # set user_id in session to simulate logged-in user
        with client.Session_transaction() as sess:
            sess['user_id'] = 1

        # user logged in, should access the protected route
        response = client.get('/')
        assert response.status_code == 200
        assert b'Protected Route' in response.data
