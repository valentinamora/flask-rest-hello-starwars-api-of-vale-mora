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

# tengo que hacer lo mismo con personajes y favoritos. 

@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    user=User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"msj":"no existe el usuario"}),404
    return jsonify(user.serialize()),200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
