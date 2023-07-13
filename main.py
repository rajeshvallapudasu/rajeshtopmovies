from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

movie_url= "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
API="a09196b981a879cc7028a93ed7779aeb"
movie_details_url = "https://api.themoviedb.org/3/movie/movie_id?language=en-US"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description= db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)

class Form(FlaskForm):
    movierating = StringField(label='Your rating out of 10 E.G.7.5')
    moviereview=StringField(label='Your Review')
    submit=SubmitField(label="Done")
class Addmovie(FlaskForm):
    movietitle=StringField(label='movie title')
    submit = SubmitField(label="Add movie")

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking=len(all_movies)-i
    return render_template("index.html", movies=all_movies)

@app.route('/edit',methods=["GET","POST"])
def rate_movie():
    form=Form()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.movierating.data)
        movie.review = form.moviereview.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",movie=movie,form=form)

@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))



headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhMDkxOTZiOTgxYTg3OWNjNzAyOGE5M2VkNzc3OWFlYiIsInN1YiI6IjY0OTJhYTUxYzI4MjNhMDExY2RiYjNiMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.IDcxJWahPPF2DU09pGK6rdnpqep7RcJoHOpsldvXNhM"
}




@app.route('/add',methods=["GET","POST"])
def add_movie():
    form=Addmovie()
    movie_title=form.movietitle.data
    if form.validate_on_submit():
        response = requests.get(movie_url, params={"api_key": API, "query": movie_title},headers=headers)
        data=response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html",form=form)
@app.route('/find')
def find_movie():
    movie_api_id=request.args.get("id")

    if movie_api_id:
        movie_api_url=f"https://api.themoviedb.org/3/movie/{movie_api_id}?language=en-US"
        response = requests.get(movie_api_url, params={"api_key": API},headers=headers)
        data=response.json()
        new_movie=Movie(
            title=data["title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
