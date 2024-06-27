from flask import request
from database.queriesUser import get_user_db, update_user_db
from model.user import UserSchema
from utility.dbConnectionHandler import connection_handler


def generate_game_id():
	import uuid
	game_id = str(uuid.uuid4().hex)[:20]
	unique_string = f"game_{game_id}"
	return unique_string


def handle_endgame(winnerId, looserId):
	database, valid_token = connection_handler(request)
	winner_info = UserSchema().dump(get_user_db(winnerId, database))
	looser_info = UserSchema().dump(get_user_db(looserId, database))

	#handle guest
	if(winner_info != {}):
		winner_info["matchesPlayed"] += 1
		winner_info["matchesWon"] += 1

		updated_winner_info = UserSchema().load(winner_info)
		update_user_db(winnerId, updated_winner_info, database)

	if(looser_info != {}):
		looser_info["matchesPlayed"] += 1

		updated_looser_info = UserSchema().load(looser_info)
		update_user_db(looserId, updated_looser_info, database)
        