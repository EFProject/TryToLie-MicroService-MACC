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
        self.rooms_ref = db.collection("rooms")
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
        
            parameters = request.json
            user_id = parameters.get('idUser')
            if not user_id:
                return make_response(jsonify({'msg': 'Missing or invalid user ID in request body.'}), 400)

            # Check user online
            doc = self.users_ref.document(user_id).get()
            if not doc.exists or doc.to_dict().get('userState') != "ONLINE":
                return make_response(jsonify({'msg': "User is offline or playing in another game."}), 402)

            # Create room
            roomId = generate_room_id()
            room_data = {
                "numberOfPlayers": parameters.get('numberOfPlayers', 2),
                "userInLobby": 1,
                f"user_1": user_id,
                "diceUser_1": 6,
                "date": datetime.now().strftime("%Y.%m.%d"),
                "state": "IN_LOBBY"
            }

            self.rooms_ref.document(roomId).set(room_data)

            # Update user state
            self.users_ref.document(user_id).update({'userState': "IN_GAME"})

            return make_response(jsonify({'msg': "Room has been created", 'roomId': roomId}), 201)

        except Exception as e:
            print("Error creating room:", str(e))
            return make_response(jsonify({'msg': 'An error occurred while creating the room.'}), 500)

    
    def put(self, id): 
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
        
        doc_ref = self.rooms_ref.document(id).get()
        if not doc_ref.exists :
            return make_response(jsonify({'msg': 'Room does not exist.'}), 404)
        room = doc_ref.to_dict()
        if room.get('state') != "IN_LOBBY":
                return make_response(jsonify({'msg': "Room not accessible"}), 402)
        
        parameters = request.json
        #Check user online
        user_id = parameters['idUser']
        if user_id is None:
            return make_response(jsonify({'msg': 'Missing user ID in request body.'}), 400)
        doc = self.users_ref.document(user_id).get()
        if doc.exists and doc.to_dict().get('userState') != "ONLINE":
            return make_response(jsonify({'msg': "User offline or is playing in another game"}), 402)
    
        try:
            #Enter room
            room_data = {
                f"user_{room['userInLobby'] + 1}": user_id,
                f"diceUser_{room['userInLobby'] + 1}": 6,
                f"userInLobby": room['userInLobby'] + 1,
            }

            #Update room state - Game starts
            if room["userInLobby"] + 1 == room["numberOfPlayers"] :
                self.rooms_ref.document(id).update({"state": "IN_WAITING"})
            
            self.rooms_ref.document(id).update(room_data)

            #Update user state
            self.users_ref.document(user_id).update({'userState': "IN_GAME"})

            return make_response(jsonify({'msg': f'Entered in room {id}'}), 200)

        except Exception as e:
            print("Enter room error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 402)
	