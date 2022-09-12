from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import Movie, Genre, Director

app = Flask(__name__)
api = Api(app)
move_ns = api.namespace('movies')
genres_ns = api.namespace('genres')
directors_ns = api.namespace('directors')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()

    genre = fields.Pluck(GenreSchema, 'name')

    director = fields.Pluck(DirectorSchema, 'name')


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

@move_ns.route('/') #/movies — возвращает список всех фильмов, разделенный по страницам;
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        query = Movie.query
        if director_id:
            query = query.filter(Movie.director_id == director_id)
        if genre_id:
            query = query.filter(Movie.genre_id == genre_id)
        return MovieSchema(many=True).dump(query.all()), 200

    def post(self): #/movies — добавляет новый фильм;
        data = request.json
        try:
            db.session.add(Movie(**data))
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()


@move_ns.route('/<int:uid>') #/movies/<int:uid> — возвращает 1 фильм;
class MovieView(Resource):
    def get(self, uid):
        all_movies = Movie.query.get(uid)
        return MovieSchema().dump(all_movies), 200

    def put(self, uid): #/movies/<int:uid> — обновляет 1 фильм;
        data = request.json
        result = Movie.query.get(uid)
        result.title = data['title']
        result.description = data['description']
        result.trailer = data['trailer']
        result.year = data['year']
        result.rating = data['rating']
        result.genre_id = data['genre_id']
        result.director_id = data['director_id']

        current_db_sessions = db.session.object_session(result)
        current_db_sessions.add(result)
        current_db_sessions.commit()
        return "", 201

    def delete(self, uid): #/movies/<int:uid> — удаляет 1 фильм;
        all_movies = Movie.query.get(uid)
        result = all_movies
        current_db_sessions = db.session.object_session(result)
        current_db_sessions.delete(result)
        current_db_sessions.commit()
        return "", 204


@genres_ns.route('/') #/genres — возвращает список всех фильмов, разделенный по страницам;
class GenreView(Resource):
    def get(self):
        return GenreSchema(many=True).dump(Genre.query.all()), 200


@genres_ns.route('/<int:uid>') #/genres/<int:uid> — возвращает 1 жанр;
class GenreView(Resource):
    def get(self, uid):
        all_genres = Genre.query.get(uid)
        return GenreSchema().dump(all_genres), 200


@directors_ns.route('/') #/genres — возвращает список всех фильмов, разделенный по страницам;
class DirectorView(Resource):
    def get(self):
        return DirectorSchema(many=True).dump(Director.query.all()), 200


@directors_ns.route('/<int:uid>') #/directors/<int:uid> — возвращает 1 director;
class DirectorView(Resource):
    def get(self, uid):
        all_directors = Director.query.get(uid)
        return DirectorSchema().dump(all_directors), 200


if __name__ == '__main__':
    app.run(debug=True)
