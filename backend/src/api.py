import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    drinks_data = Drink.query.all()
    drinks = [drink.short() for drink in drinks_data]
    
    return jsonify({
        "success": True, 
        "drinks": drinks
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks_data = Drink.query.all()
    drinks = [drink.long() for drink in drinks_data]

    return jsonify({
        "success": True, 
        "drinks": drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()

    title = body.get('title', None)
    recipe_list = body.get('recipe', None)
    recipe_string = json.dumps(recipe_list)
    try:
        drink = Drink(title=title,recipe=recipe_string)
        drink.insert()

        return jsonify({
            "success": True, 
            "drinks": [drink.long()]
        })
    except: 
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,id):
    body = request.get_json()

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if not drink:
            abort(404)
        
        title = body.get('title', None)
        
        if not title or type(title) is not str or len(title) == 0 :
            abort(400)
        
        drink.title = title
        recipe_list = body.get('recipe', None)
        
        if recipe_list:
            drink.recipe = json.dumps(recipe_list)

        drink.update()

        return jsonify({
                'success': True,
                'drinks': [drink.long()],
            })

    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(payload,id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    if not drink:
            abort(404)
    
    try:
        drink.delete()

        return jsonify({
            "success": True, 
            "delete": id
        })
    
    except:
        abort(500)
        
## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Resource not found"
                    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "server error"
                    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad request"
                    }), 400

@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unathorized",
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden",
    }), 403
