from flask_restful import Resource

class homeAPI(Resource):
    def get(self):
        return "Welcome to TryToLie Micro-Service"