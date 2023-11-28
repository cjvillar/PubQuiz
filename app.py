import time
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    request,
    jsonify,
)
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from quiz_data import data
from models import User, UserStats

#from dotenv import load_dotenv
import os

# config app
# app = Flask(__name__)

# # correct answers used in quiz
# correctAnswers = 0

# # Configure Flask to use server-side sessions stored in the filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # Configure SQLAlchemy for the database connection
# engine = create_engine("sqlite:///pubQuiz.db")
# Session = sessionmaker(bind=engine)


def create_app(database_uri="sqlite:///pubQuiz.db"):
    # Create the Flask app
    app = Flask(__name__)

    # Set the secret key for the app
    app.secret_key = os.getenv("SECRET_KEY")

    # Configure Flask to use server-side sessions stored in the filesystem
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    # Configure SQLAlchemy for the database connection
    engine = create_engine(database_uri)
    Session = sessionmaker(bind=engine)

    # Define the after_request function
    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app
    
# Get the Flask app instance
app = create_app()

# @app.after_request
# def after_request(response):
#     """Ensure responses aren't cached"""
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response


def calculate_remaining_time():
    timer_duration = 60

    if "quiz_started" not in session:  # or not session["quiz_started"]:
        session["quiz_started"] = True
        session["start_time"] = time.time()

    elapsed_time = time.time() - session["start_time"]
    remaining_time = max(timer_duration - elapsed_time, 0)

    return remaining_time


@app.route("/get_timer", methods=["GET"])
def get_timer():
    remaining_time = calculate_remaining_time()
    return jsonify({"timer": remaining_time})


@app.route("/")
@login_required
def index():
    """Show Quizers Profile"""
    user_id = session["user_id"]

    db_session = Session()
    users = db_session.query(User).filter_by(id=user_id).first()

    if users is None:
        return apology(message="Need A Valid User")

    return render_template("index.html", username=users.username)


@app.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    """Show Leaderboard"""
    db_session = Session()

    # querry to join User and UserStats
    leaderboard_data = (
        db_session.query(User.username, UserStats.high_score, UserStats.user_time)
        .join(UserStats, User.id == UserStats.user_id)
        .distinct(User.username)
    )

    return render_template("leaderboard.html", leaderboard_data=leaderboard_data)


@app.route("/quizResults")
@login_required
def quiz_results():
    """Show quiz results and save in db"""
    user_id = session["user_id"]
    db_session = Session()
    score = session.get("score", 0)
    remaining_time = session.get("remaining_time", calculate_remaining_time())
    formatted_time = f"{remaining_time:.2f}"
    print(f"formatted time: {formatted_time}")

    # query User and UserStats
    user_stats = db_session.query(UserStats).filter_by(user_id=user_id).first()

    if user_stats:
        if user_stats.high_score and (score > user_stats.high_score):
            user_stats.last_score = score
            user_stats.high_score = score
            user_stats.user_time = formatted_time
            # user_stats.badges = new_badges

        else:
            user_stats.last_score = score

        db_session.commit()

    else:
        # if no UserStats record exists, create a new one
        user_stats = UserStats(
            user_id=user_id,
            last_score=score,
            high_score=score,
            user_time=formatted_time,
            badges=[],
        )

        # add user stats
        db_session.add(user_stats)

    db_session.commit()

    return render_template("quizResults.html", score=score)


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Show quiz"""
    if request.method == "GET":  # and "quiz_started" not in session:
        session["quiz_started"] = True
        session["start_time"] = time.time()
        session["current_question_index"] = 0

    correctAnswers = session.get("correctAnswers", 0)
    score = session.get("score", 0)

    if "current_question_index" not in session or "quiz_started" not in session:
        # init quiz if it's the first visit or the quiz_started flag is not set
        session["current_question_index"] = 0
        session["quiz_started"] = True
        remaining_time = session.get("remaining_time", calculate_remaining_time())

    else:
        remaining_time = calculate_remaining_time()
        session["remaining_time"] = remaining_time

    print(f"{remaining_time:.2f}")

    if request.method == "POST":
        user_answer = request.form.get(request.form["question"])

        if user_answer == request.form.get("correct_answer"):
            correctAnswers += 1
            print(f"for each answer: {correctAnswers}")

    # logic to get the next question in data list
    current_question_index = session.get("current_question_index", 0)

    if current_question_index < len(data):
        question = data[current_question_index]
        session["current_question_index"] = current_question_index + 1
        # increment question index
        return render_template(
            "quiz.html", question=question, remaining_time=remaining_time
        )

    if current_question_index == len(data):
        # calc score
        question_score = (correctAnswers / len(data)) * 100
        print(f"this is the score: {question_score}")
        score += question_score

        # store the score in the session
        session["score"] = score

        # clear index and quiz_started
        session.pop("current_question_index", None)
        session.pop("quiz_started", None)

        return redirect(url_for("quiz_results", score=score))

    return render_template("quiz.html", question=data[0], remaining_time=remaining_time)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # clear user_id
    session.clear()

    if request.method == "POST":
        db_session = Session()

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # query database for username

        users = (
            db_session.query(User)
            .filter_by(username=request.form.get("username"))
            .first()
        )

        # check username exists and password is correct
        if not users or not check_password_hash(
            users.passhash, request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # user logged in
        session["user_id"] = users.id

        # Redirect user to home page
        return redirect("/")

    # user reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # clear user_id
    session.clear()

    # redirect user to login
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    db_session = Session()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        check = request.form.get("confirmation")

        users = db_session.query(User).all()
        for user in users:
            if user.username == username:
                return apology(message="Username Already Exsist")

        # create passHash and check
        passHash = generate_password_hash(password)

        confirmation = check_password_hash(passHash, check)

        if not username:
            return apology(message="Need a Username")

        elif not password:
            return apology(message="Password Can Not be Blank")

        elif confirmation != True:
            return apology(message="Password Does not match check")

        else:
            new_user = User(username=username, passhash=passHash)

            db_session.add(new_user)
            db_session.commit()

            db_session.commit()
            db_session.close()

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
