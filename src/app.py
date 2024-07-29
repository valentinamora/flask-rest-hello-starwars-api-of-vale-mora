"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_swagger import swagger # type: ignore
from flask_cors import CORS # type: ignore
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Planet,Character,Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

@app.route('/user', methods=['GET'])
def handle_hello():

    user=User.query.all()
    if user == []:
        return jsonify({"msj":"no existe usuario"}),404
    response_body=list(map(lambda item:item.serialize(),user))

    return jsonify(response_body), 200

@app.route('/planet', methods=['GET'])
def get_planet():

    planet=Planet.query.all()
    if planet == []:
        return jsonify({"msj":"no existe planeta"}),404
    response_body=list(map(lambda item:item.serialize(),planet))

    return jsonify(response_body), 200

@app.route('/character', methods=['GET'])
def get_character():

    character=Character.query.all()
    if character== []:
        return jsonify({"msj":"no existe personaje"}),404
    response_body=list(map(lambda item:item.serialize(),character))

    return jsonify(response_body), 200

@app.route('/favorite', methods=['GET'])
def get_favorite():

    favorite=Favorite.query.all()
    if favorite== []:
        return jsonify({"msj":"no existe ningun favorito"}),404
    response_body=list(map(lambda item:item.serialize(),favorite))

    return jsonify(response_body), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    user=User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"msj":"no existe el usuario"}),404
    return jsonify(user.serialize()),200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet=Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        return jsonify({"msj":"no existe el planeta"}),404
    return jsonify(planet.serialize()),200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_single_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    if character is None:
        return jsonify({"msj": "no existe el personaje"}), 404
    return jsonify(character.serialize()), 200

# esto es nuevo 

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"msj": "no existe el usuario"}), 404
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    response_body = list(map(lambda item: item.serialize(), favorites))
    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1 
    if Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({"msg": "El planeta ya está en favoritos"}), 400

    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": f"Planeta con id={planet_id} agregado a favoritos"}), 201

@app.route('/favorite/people/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id = 1 
    if Favorite.query.filter_by(user_id=user_id, character_id=character_id).first():
        return jsonify({"msg": "El personaje ya está en favoritos"}), 400

    favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": f"Personaje con id={character_id} agregado a favoritos"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = 1 
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"msg": "El planeta no está en favoritos"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Planeta con id={planet_id} eliminado de favoritos"}), 200

@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(character_id):
    user_id = 1 
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite is None:
        return jsonify({"msg": "El personaje no está en favoritos"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Personaje con id={character_id} eliminado de favoritos"}), 200

# hasta aca 


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
