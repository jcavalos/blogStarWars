"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# [GET] /people - Listar todos los registros de people


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

# [GET] /people/<int:people_id> - Muestra la información de un solo personaje


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_people(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "People not found"}), 404
    return jsonify(person.serialize()), 200

# [GET] /planets - Listar todos los registros de planets


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# [GET] /planets/<int:planet_id> - Muestra la información de un solo planeta


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# [GET] /users - Listar todos los usuarios del blog


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# [GET] /users/favorites - Listar todos los favoritos del usuario actual


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # Por ahora usamos un usuario fijo (user_id = 1)
    # Más adelante se implementará con autenticación
    user_id = 1

    favorites = Favorite.query.filter_by(user_id=user_id).all()

    result = []
    for fav in favorites:
        if fav.people_id:
            person = People.query.get(fav.people_id)
            if person:
                result.append({
                    "type": "people",
                    "id": person.id,
                    "name": person.name
                })
        if fav.planet_id:
            planet = Planet.query.get(fav.planet_id)
            if planet:
                result.append({
                    "type": "planet",
                    "id": planet.id,
                    "name": planet.name
                })

    return jsonify(result), 200

# [POST] /favorite/planet/<int:planet_id> - Añadir planeta favorito


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Por ahora usamos un usuario fijo (user_id = 1)
    user_id = 1

    # Verificar que el planeta existe
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    # Verificar que no existe ya como favorito
    existing = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if existing:
        return jsonify({"msg": "Planet already in favorites"}), 400

    # Crear el favorito
    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added successfully"}), 201

# [POST] /favorite/people/<int:people_id> - Añadir personaje favorito


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    # Por ahora usamos un usuario fijo (user_id = 1)
    user_id = 1

    # Verificar que el personaje existe
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "People not found"}), 404

    # Verificar que no existe ya como favorito
    existing = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if existing:
        return jsonify({"msg": "People already in favorites"}), 400

    # Crear el favorito
    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite people added successfully"}), 201

# [DELETE] /favorite/planet/<int:planet_id> - Eliminar planeta favorito


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # Por ahora usamos un usuario fijo (user_id = 1)
    user_id = 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite planet deleted successfully"}), 200

# [DELETE] /favorite/people/<int:people_id> - Eliminar personaje favorito


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    # Por ahora usamos un usuario fijo (user_id = 1)
    user_id = 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite people deleted successfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
