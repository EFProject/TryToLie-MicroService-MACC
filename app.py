from flask_restful import Api
from flask import Flask
from firebase_admin import credentials, initialize_app, firestore
from services.serviceHome import homeAPI
from services.serviceUser import UserAPI, UserImageAPI
from services.serviceRoom import RoomAPI
from services.serviceGame import GameAPI

app = Flask(__name__)
api = Api(app)
# Load the configuration from the config module
app.config.from_object('config')

# Initialize Firebase Admin SDK with credentials from the JSON file
firebase_credentials = credentials.Certificate("firebaseConfig.json")
fireBaseApp = initialize_app(firebase_credentials)

# Initialize Firestore database
db = firestore.client()

api.add_resource(homeAPI, '/')
api.add_resource(UserAPI, '/api/v1/user', '/api/v1/user/<string:id>')
api.add_resource(UserImageAPI,'/api/v1/user/image/<string:id>')
api.add_resource(RoomAPI, '/api/v1/room', '/api/v1/room/<string:id>', resource_class_kwargs={'db': db})
api.add_resource(GameAPI, '/api/v1/game/<string:id>', resource_class_kwargs={'db': db})

if __name__ == "__main__":
     app.run(host='0.0.0.0',port=5001 ,debug=True)
