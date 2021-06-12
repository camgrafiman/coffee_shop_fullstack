import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

'''
@DONETODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@DONETODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure

'''
@app.route('/drinks', methods=['GET'])
def drinks():

    try:
        drinks_data = Drink.query.all()

        drinks_arr = [drink.short() for drink in drinks_data]
        print(drinks_arr)

        return jsonify({
            "success": True,
            "status_code": 200,
            "drinks": [drink.short() for drink in drinks_data]
        })
        # print(drinks_data)
    except:
        abort(404)


'''
@DONETODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    print('JWT IN /DRINKS-DETAIL ROUTE ', jwt)
    try:
        drinks_detail_data = Drink.query.order_by(Drink.id).all()

        return jsonify({
            "success": True,
            "status_code": 200,
            "drinks": [drink.long() for drink in drinks_detail_data]
        })

    except:
        abort(401)


'''
@DONETODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(422)
    try:
        title_req = data['title']
        recipe = data['recipe']
        r_color = recipe.get('color')
        r_name = recipe.get('name')
        r_parts = recipe.get('parts')

        recipejson = [
            {"color": r_color, "name": r_name, "parts": int(r_parts)}]
        rjson = json.dumps(recipejson)

        new_drink = Drink(title=title_req, recipe=rjson)
        new_drink.insert()
        print(new_drink)

        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': [new_drink.long()]
        })
    except Exception:
        abort(400)


'''
@DONETODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    if id is None or id <= 0:
        abort(404)

    data = request.get_json()
    selected_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not selected_drink:
        abort(404)

    try:
        selected_drink.title = data['title']

        selected_drink.update()

        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': [selected_drink.long()]
        })
    except:
        abort(422)


'''
@DONETODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    selected_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not selected_drink:
        abort(404)

    try:
        selected_drink.delete()

        return jsonify({
            'success': True,
            'status_code': 200,
            'delete': id
        })
    except:
        abort(422)


@app.route('/')
def index():

    return 'Welcome to COFFEE SHOP API'


@app.route('/login')
def login():
    return 'login'


@app.route('/login-results')
def login_results():
    return 'signed in'


'''
@DONETODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(401)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Sorry, you are not authorized/allowed to view this content.'
    }), 401


'''
@DONETODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found.'
    }), 404


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Forbidden'
    }), 403


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'status_code': 422,
        'message': 'unprocessable'
    }), 422


# Added the 400 Error Bad request:


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'status_code': 400,
        'message': 'Bad request'
    }), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'status_code': 500,
        'message': 'Internal server error.'
    }), 500


@app.errorhandler(502)
def bad_gateway(error):
    return jsonify({
        'success': False,
        'status_code': 502,
        'message': 'Bad gateway.'
    }), 502


@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        'success': False,
        'status_code': 503,
        'message': 'Service unavailable'
    }), 503


@app.errorhandler(504)
def gateway_out(error):
    return jsonify({
        'success': False,
        'error': 504,
        'message': 'Gateway timed out'
    }), 504


'''
@DONETODO implement error handler for AuthError
    error handler should conform to general task above
'''
# Error Handler (401-403) Unauthorized
@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code
