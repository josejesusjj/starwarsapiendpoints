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
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

    # General calls for users, people and planets:

@app.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    response_body = []
    for user in users:
        response_body.append(user.serialize())


    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def handle_people():
    people = People.query.all()
    response_body = []
    for character in people:
        response_body.append(character.serialize())
    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    response_body = []
    for planet in planets:
        response_body.append(planet.serialize())
    return jsonify(response_body), 200
    
 # Individual call for people and planets:

@app.route('/people/<int:id>', methods=['GET'])
def get_people_by_id(id):
    people = People.get_by_id(id)
    if people: 
        return jsonify(people.serialize()), 200
    return ({'error': 'Character not found'}), 404

@app.route('/planets/<int:id>', methods=['GET'])
def get_planet_by_id(id):
    planet = Planets.get_by_id(id)
    if planet: 
        return jsonify(planet.serialize()), 200
    return ({'error': 'Planet not found'}), 404

 # calls, adds and removes favorites:

@app.route('/favorites/<int:id>', methods=['GET'])
def handle_favorites(id):
    favorites = Favorites.query.filter_by(user_id = id).all()
    response_body = []
    for favorite in favorites:
        response_body.append(favorite.serialize())
    return jsonify(response_body), 200


@app.route('/favorite-add', methods=['GET','POST'])
def add_favorite_planet(user_id, planets_id):
    #user_id = request.form.get('user_id')
    #new = Favorites( user_id = user_id, planets_id = planets_id)
    user_id = request.form.get('user_id')
    item_id = request.form.get('item_id')
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    item = Favorites( user_id=user_id, item_id=item_id, item_name=item_name, category=category)
    db.session.add(item)
    db.session.commit()
    favorites = Favorites.query.filter_by(user_id = user_id).all()
    response_body = []
    for favorite in favorites:
        response_body.append(favorite.serialize())
    return jsonify(response_body), 200

@app.route('/favorite-delete/<int:id>', methods=['GET','POST'])
def delete_favorite_people(id):
    old = Favorites.query.get(id)
    db.session.delete(old)
    db.session.commit()
    favorites = Favorites.query.filter_by(user_id = 1).all()
    response_body = []
    for favorite in favorites:
        response_body.append(favorite.serialize())
    return jsonify(response_body), 200   


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)