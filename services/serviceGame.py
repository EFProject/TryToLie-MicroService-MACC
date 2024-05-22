import json
from flask_restful import Resource
from google.cloud.firestore_v1.base_query import FieldFilter, Or, And
from flask import jsonify, request, make_response
from utility.dbConnectionHandler import connection_handler



def generate_game_id():
        import uuid
        game_id = str(uuid.uuid4().hex)[:20]
        unique_string = f"game_{game_id}"
        return unique_string



class GameAPI(Resource):
    def __init__(self, db):
        self.db = db
        self.rooms_ref = db.collection("Rooms")
        self.games_ref = db.collection("Games")
        self.users_ref = db.collection("users")
        self.database, self.valid_token = connection_handler(request)


    def get(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        try:
            doc_ref = self.games_ref.document(id)
            doc = doc_ref.get()

            if doc.exists:
                game = doc.to_dict()
                return make_response(game, 200)

            return make_response(jsonify({'msg': 'Game does not exist.'}), 404)
        
        except Exception as e:
            print("Get game error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 400)    


    ###GET ALL GAMES BY UserID
    # def get(self):
    #     try:
    #         parameters = request.json
    #         user_id = parameters.get('idUser')
    #         if not user_id:
    #             return make_response(jsonify({'msg': 'Missing or invalid user ID in request body.'}), 400)

    #         filters = [FieldFilter(f"user_{i}", "==", user_id) for i in range(1, 7)]
    #         or_filter = Or(filters)

    #         rooms = []
    #         query = self.rooms_ref.where(filter=or_filter).limit(10).stream()
    #         rooms.extend([doc.to_dict() for doc in query])

    #         if rooms:
    #             return make_response(jsonify({'rooms': rooms}), 200)
    #         else:
    #             return make_response(jsonify({'msg': 'No rooms found for the user.'}), 404)

    #     except Exception as e:
    #         print("Error fetching rooms:", str(e))
    #         return make_response(jsonify({'msg': 'An error occurred while fetching rooms.'}), 500)


    def post(self, id):
        try:
            if not self.valid_token:
                return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
            
            doc_ref = self.rooms_ref.document(id).get()
            if not doc_ref.exists :
                return make_response(jsonify({'msg': 'Room does not exist.'}), 404)
            room = doc_ref.to_dict()
            if room.get('roomState') != "JOINED":
                    return make_response(jsonify({'msg': "Room not ready yet"}), 402)
            
            # if active_player is None:
            #     return make_response(jsonify({'msg': 'Missing user ID in request body.'}), 400)
            # if room.get('playerOneId') != active_player:
            #         return make_response(jsonify({'msg': "Only user 1 can start a game"}), 402)

            # Create game
            gameId = generate_game_id()
            game_data = {
                "gameId" : gameId,
                "roomId": id,
                "playerOneId": room.get('playerOneId'),
                "playerTwoId": room.get('playerTwoId'),
                "playerOneName": room.get('playerOneName'),
                "playerTwoName": room.get('playerTwoName'),
                "gameState": "DICE_PHASE",
                "playerOneDice": 2,
                "playerTwoDice": 2,
                "currentTurn" : 1,
                "currentPlayer": room.get('playerOneId'),
                "winner": ""
            }

            self.games_ref.document(gameId).set(game_data)
            self.rooms_ref.document(id).update({
                "roomState": "IN_PROGRESS",
                "gameId": gameId,
                })

            return make_response(jsonify({'msg': "Game has been started", 'gameID': gameId}), 201)

        except Exception as e:
            print("Error creating game:", str(e))
            return make_response(jsonify({'msg': 'An error occurred while creating the game.'}), 500)


    def put(self, id): 
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)
        
        doc_ref = self.games_ref.document(id).get()
        if not doc_ref.exists :
            return make_response(jsonify({'msg': 'Game does not exist.'}), 404)
        game = doc_ref.to_dict()

        parameters = json.loads(request.json)
        # active_player = parameters['idUser']
        # if active_player is None:
        #     return make_response(jsonify({'msg': 'Missing user ID in request body.'}), 400)
        # if game.get('active_player') != active_player:
        #         return make_response(jsonify({'msg': "It's not your turn"}), 402)
        msg = "Phase correctly processed"

        try:

            #Liar Call phase
            if game.get('gameState') == "LIAR_PHASE":
                # handle liar outcome
                diceResults = game.get('diceResults')
                declarationResults = game.get('declarationResults')
                liarOutcome = False

                occurency = declarationResults[0]
                dice = declarationResults[1]

                if diceResults.count(dice) < occurency:
                    liarOutcome = True

                game_data = {
                    "currentTurn": game.get('currentTurn') + 1,
                    "diceResults": [],
                    "declarationResults": [],
                    "gameState": "RESOLVE_PHASE",
                    "playerOneDice": game.get('playerOneDice'),
                    "playerTwoDice": game.get('playerTwoDice'),
                    "winner": ""
                }

                if game.get('currentPlayer') == game.get('playerOneId'):
                    if liarOutcome:
                        game_data["playerTwoDice"] -= 1
                        msg = "Player 2 was caught lying, so he loses a dice."
                    else:
                        game_data["playerOneDice"] -= 1
                        msg = "Player 2 told the truth, so Player 1 loses a dice."
                else :
                    if liarOutcome:
                        game_data["playerOneDice"] -= 1
                        msg = "Player 1 was caught lying, so he loses a dice."
                    else:
                        game_data["playerTwoDice"] -= 1
                        msg = "Player 1 told the truth, so Player 2 loses a dice."

                if game_data["playerOneDice"] == 0 : game_data["winner"] = game.get('playerTwoId')
                if game_data["playerTwoDice"] == 0 : game_data["winner"] = game.get('playerTwoId')
                    
                
            #Dice roll phase
            if game.get('gameState') == "DICE_PHASE":
                game_data = {
                    "diceResults": parameters['diceResults'],
                    "gameState": "DECLARATION_PHASE"
                }
            
            #Result Declaration phase
            if game.get('gameState') == "DECLARATION_PHASE":
                game_data = {
                    "declarationResults": parameters['declarationResults'],
                    "gameState": "LIAR_PHASE"
                }
                if game.get('currentPlayer') == game.get('playerOneId'):
                    game_data["currentPlayer"] = game.get('playerTwoId')
                else :
                    game_data["currentPlayer"] = game.get('playerOneId')

            self.games_ref.document(id).update(game_data)

            return make_response(jsonify({'msg': msg, 'gameID': id }), 200)

        except Exception as e:
            print("Processing turn error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 402)
    
    
    def delete(self, id):
        if not self.valid_token:
            return make_response(jsonify({'msg': 'Unauthorized. Invalid or missing token.'}), 401)

        doc_ref = self.games_ref.document(id).get()
        if not doc_ref.exists :
            return make_response(jsonify({'msg': 'Game does not exist.'}), 404)
        game = doc_ref.to_dict()
        id_room = game.get('room_id')
        room = doc_ref = self.rooms_ref.document(id_room).get().to_dict()

        try:
            self.games_ref.document(id).delete()
            self.rooms_ref.document(id_room).update({"state" : "CLOSED"})

            self.users_ref.document(room.get('user_1')).update({"userState" : "ONLINE"})
            self.users_ref.document(room.get('user_2')).update({"userState" : "ONLINE"})

            return make_response(jsonify({'msg': f'Game correctly ended ', 'gameID': id}), 200)
        
        except Exception as e:
            print("Game ending error: ",str(e))
            return make_response(jsonify({'msg': str(e)}), 402)