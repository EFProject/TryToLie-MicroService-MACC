from flask_restful import Api
from flask import Flask
from firebase_admin import credentials, initialize_app, firestore
from services.serviceUser import UserAPI
from services.serviceHome import homeAPI


app = Flask(__name__)
api = Api(app)

# Initialize Firebase Admin SDK with credentials from the JSON file
firebaseConfig = credentials.Certificate("TryToLie-Microservice-MACC/firebaseConfig.json")
fireBaseApp = initialize_app(firebaseConfig)

# Initialize Firestore database
db = firestore.client()

api.add_resource(homeAPI, '/')
api.add_resource(UserAPI, '/api/v1/user', '/api/v1/user/<string:id>')

if __name__ == "__main__":
     app.run(host='0.0.0.0',port=5001 ,debug=True)
