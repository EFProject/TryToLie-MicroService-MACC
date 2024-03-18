from flask_restful import Resource
import json
from flask import jsonify, request, make_response, send_from_directory
from database.queriesUser import delete_user_db, get_user_db, insert_user_db, update_user_db
from model.user import UserSchema
from utility.dbConnectionHandler import connection_handler
import os


class UserAPI(Resource):
    def __init__(self):
        self.database, self.valid_token = connection_handler(request)

    def get(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
        
        user_info = get_user_db(id, self.database)
        
        if user_info is None:
            return make_response(jsonify({'msg': f'No User found for id: {id}'}), 204)
        else:
            user_schema = UserSchema().dump(user_info)
            return make_response(jsonify(user_schema), 200)

    def post(self):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        if 'application/json' in request.content_type:
            # Convert the dictionary to a JSON string
            parameters = json.dumps(request.json)
        elif 'multipart/form-data' in request.content_type:
            # Handle multipart form data (including file uploads)
            parameters = request.form.get('json_data')
        else: 
            print("Unsupported content type:", request.content_type)
            return make_response(jsonify({'error': 'Unsupported content type'}), 400)
        
        parameters = parameters[:-1] + ', "matches_played": 0, "matches_won": 0}'
        user_info = UserSchema().loads(parameters)
        msg, code = insert_user_db(user_info, self.database)
        id = msg.get('id')

        if 'multipart/form-data' in request.content_type:
            path = f"assets/user_images/profileImage{id}.jpg"
            # Save the new JPG file
            request.files['image'].save(path)

        return make_response(jsonify(msg.get('msg')), code)

    def put(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        if 'application/json' in request.content_type:
            parameters = json.dumps(request.json)
        elif 'multipart/form-data' in request.content_type:
            # Handle multipart form data (including file uploads)
            parameters = request.form.get('json_data')
        else: 
            print("Unsupported content type:", request.content_type)
            return make_response(jsonify({'error': 'Unsupported content type'}), 400)
        user_info = UserSchema().loads(parameters)
        msg, code = update_user_db(id, user_info, self.database)
        if msg.get('error') != f"User with id {id} does not exist" and 'multipart/form-data' in request.content_type:
            path = f"assets/user_images/profileImage{id}.jpg"
            # Check if a JPG file already exists in the directory
            if os.path.exists(path):
                os.remove(path)
            # Save the new JPG file
            request.files['image'].save(path)
        return make_response(jsonify(msg), code)

    def delete(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        msg, code = delete_user_db(id, self.database)
        path = f"assets/user_images/profileImage{id}.jpg"
        if os.path.exists(path): 
            os.remove(path)
        return make_response(jsonify(msg), code)
    

class UserImageAPI(Resource):
    def get(self, id):
        database, valid_token = connection_handler(request)
        if not valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
        
        filename = f"profileImage{id}.jpg"
        directory = "assets/user_images"
        path = os.path.join(directory, filename)
        
        if os.path.exists(path):
            return send_from_directory(directory, filename)
        else:
            return {"message": "Image not found"}, 404