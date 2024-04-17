import json
import random
from flask_restful import Resource
from google.cloud.firestore_v1.base_query import FieldFilter, Or, And
from flask import jsonify, request, make_response
from utility.dbConnectionHandler import connection_handler
from datetime import datetime



def generate_room_id():
        import uuid
        room_id = str(uuid.uuid4().hex)[:20]
        unique_string = f"room_{room_id}"
        return unique_string



class RoomAPI(Resource):
    def __init__(self, db):
        self.db = db
        self.rooms_ref = db.collection("Rooms")
        self.users_ref = db.collection("users")
        self.database, self.valid_token = connection_handler(request)

    def get(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        try:
            doc_ref = self.rooms_ref.document(id)
            doc = doc_ref.get()

            if doc.exists:
                room = doc.to_dict()
                return make_response(room, 200)

            return make_response(jsonify({'msg': 'Room does not exist.'}), 404)
        
        except Exception as e:
            print("Get room error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 400)    
    

    def post(self):
        try:
            if not self.valid_token:
                return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
        
            parameters = json.loads(request.json)
            user_id = parameters.get('playerOneId')
            if not user_id:
                return make_response(jsonify({'msg': 'Missing or invalid user ID in request body.'}), 400)

            # Create room
            roomId = generate_room_id()
            room_data = {
                "roomId": roomId,
                #"diceNumber": parameters.get("diceNumber"),
                "roomState": parameters.get("roomState"),
                #"pictureUrlOne": parameters.get("pictureUrlOne"),
                "playerOneId": parameters.get("playerOneId"),
                "playerOneName": parameters.get("playerOneName"),
            }

            self.rooms_ref.document(roomId).set(room_data)

            return make_response(jsonify(room_data), 201)

        except Exception as e:
            print("Error creating room:", str(e))
            return make_response(jsonify({'msg': 'An error occurred while creating the room.'}), 500)

    
    def put(self):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        try:
            rooms_query = self.rooms_ref.where(filter=FieldFilter('roomState', '==', 'CREATED')).get()
            
            # Convert rooms to a list for random selection
            rooms_list = [(doc.id) for doc in rooms_query]

            if not rooms_list:
                return make_response(jsonify({'msg': 'No rooms with room_state CREATED found.'}), 404)

            room_id = random.choice(rooms_list)
            parameters = json.loads(request.json)

            self.rooms_ref.document(room_id).update({
                #"diceNumber": parameters.get("diceNumber"),
                "roomState": parameters.get("roomState"),
                #"pictureUrlTwo": parameters.get("pictureUrlTwo"),
                "playerTwoId": parameters.get("playerTwoId"),
                "playerTwoName": parameters.get("playerTwoName"),
            })

            free_room = self.rooms_ref.document(room_id).get().to_dict()

            return make_response(jsonify(free_room), 200)
        
        except Exception as e:
            print("Get free room error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 400)  
        
    
    def delete(self, id):

        roomId = id.replace('"','')

        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        doc_ref = self.rooms_ref.document(roomId).get()
        if not doc_ref.exists :
            return make_response(jsonify({'msg': 'Room does not exist.'}), 404)

        try:
            self.rooms_ref.document(roomId).delete()
            return make_response(jsonify({'msg': f'Room correctly deleted ', 'roomID': roomId}), 200)
        
        except Exception as e:
            print("Room delete error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 402)
	