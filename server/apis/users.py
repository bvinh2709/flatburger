from flask_restful import Resource
from config import api, db
from models import User, Order
from flask import make_response, request

class Users(Resource):
    def get(self):
        return make_response([u.to_dict() for u in User.query.all()], 200)

class UserByID(Resource):
    def get(self, id):
        if id not in [u.id for u in User.query.all()]:
            return make_response({'message': 'User not Found, please try again'}, 404)
        return make_response((User.query.filter(User.id==id).first()).to_dict(), 200)

    def patch(self, id):
        if id not in [u.id for u in User.query.all()]:
            return make_response({'message': 'User not Found, please try again'}, 404)
        else:
            data = request.get_json()

            if not data:
                return make_response({'error': 'Invalid data'}, 400)

            user = User.query.filter(User.id==id).first()
            for key in data.keys():
                setattr(user, key, data[key])

            db.session.add(user)
            db.session.commit()

            return make_response(user.to_dict(), 200)

    def delete(self, id):
        if id not in [u.id for u in User.query.all()]:
            return make_response({'message': 'User not Found, please try again'}, 404)
        else:
            db.session.query(Order).filter(Order.user_id == id).delete()
            user = User.query.filter(User.id==id).first()
            db.session.delete(user)
            db.session.commit()

            return make_response({'message': 'This User has been terminated!'}, 204)


api.add_resource(Users, '/users', endpoint='users')
api.add_resource(UserByID, '/users/<int:id>', endpoint='user-by-id')