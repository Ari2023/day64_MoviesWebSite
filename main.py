from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests, json


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"

# CREATE THE EXTENSION
db = SQLAlchemy(model_class=Base)

# initialise the app with the extension
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# CREATE TABLE SCHEMA IN THE DATABASE
with app.app_context():
    db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    movie_name = StringField("Movie name", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    # READ ALL MOVIES
    result = db.session.execute(db.select(Movie).order_by(Movie.title))
    all_movies = result.scalars().all()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_to_search = form.movie_name.data
        url = "https://api.themoviedb.org/3/search/movie?query=Superman&include_adult=false&language=en-US&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiYzFmNmViMzNiYjA0ZGFhNTE2ZjdlNThhYjI2NzI0NSIsIm5iZiI6MTcyOTc1OTEzNi44MzY2MzgsInN1YiI6IjY3MDRmZjUzNWFlMDFkMDkwZTFkNDRjMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ljYS6iTtVXYTPuQvk0pVtBW3Cz54-Gdj_KNTsLfCAes"
        }
        parameters = {
            "query": movie_to_search
        }
        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        movie_list = data["results"]
        movie_data = []
        for movie in movie_list:
            title = movie["title"]
            date = movie["release_date"]
            id = movie["id"]
            new_movie=(title, date, id)
            movie_data.append(new_movie)
        print (movie_data)
        return render_template("select.html", movies=movie_data)

    return render_template("add.html", form=form)

@app.route("/append_movie", methods=["GET", "POST"])
def append_movie():
    url = "https://api.themoviedb.org/3/movie/603?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiYzFmNmViMzNiYjA0ZGFhNTE2ZjdlNThhYjI2NzI0NSIsIm5iZiI6MTczMDAzMDEzMS43MDc0NTUsInN1YiI6IjY3MDRmZjUzNWFlMDFkMDkwZTFkNDRjMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.rQWb72vnH5aQCJ8UNXkl0qkONtq0Gb4o1EEaoeZhFhM"
    }
    parameters = {
        "movie_id": id
    }
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    print (data)
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    # DELETE A MOVIE
    movie_id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
