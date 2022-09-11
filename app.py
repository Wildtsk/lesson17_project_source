# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import Movie

app = Flask(__name__)
api = Api(app)
move_ns = api.namespace('movies')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

@move_ns.route('/') #/movies — возвращает список всех фильмов, разделенный по страницам;
class MovieView(Resource):
    def get(self):
        all_movies = Movie.query.all()
        return MovieSchema(many=True).dump(all_movies), 200

@move_ns.route('/<int:uid>') #/movies/<int:uid> — возвращает 1 фильм;
class MovieView(Resource):
    def get(self, uid):
        all_movies = Movie.query.get(uid)
        return MovieSchema().dump(all_movies), 200

if __name__ == '__main__':
    app.run(debug=True)
