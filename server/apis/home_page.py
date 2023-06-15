from flask_restful import Resource
from config import api

class HomePage(Resource):
    def get(self):
        return {'message': '200: Welcome to our Home Page'}, 200

api.add_resource(HomePage, '/', endpoint='home-page')