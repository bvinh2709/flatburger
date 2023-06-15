from flask_restful import Resource
from config import api, db
from models import User
from flask import make_response, request

class SignUp(Resource):
    def post(self):
        email = request.json['email']
        password = request.json['password']
        password_confirmation = request.json['password_confirmation']
        firstname = request.json['first_name']
        lastname = request.json['last_name']
        dob = request.json['dob']

        # user_exists = User.query.filter(User.email == email).first() is not None

        if email in [u.email for u in User.query.all()]:
            flash('Username already taken!')
            return jsonify({"error": "There is already a user with this name"}), 409

        if not firstname.isalpha() or not lastname.isalpha():
            return jsonify({"error": "First name and last name should contain only alphabetic characters"}), 400

        if not email or not password or not password_confirmation or not firstname or not lastname or not dob:
            return jsonify({"error": "All fields are required"}), 400

        if password != password_confirmation:
            return jsonify({"error": "Password and password confirmation do not match"}), 400

        hashed_password = bcrypt.generate_password_hash(password)

        new_user = User(
            email = email,
            _password_hash = hashed_password,
            password_confirmation = password_confirmation,
            first_name = firstname,
            last_name = lastname,
            dob = dob
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict()

class Login(Resource):
    def post(self):
        email = request.get_json().get('email')
        password = request.get_json().get('password')
        user = User.query.filter(User.email == email).first()

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        if user.authenticate(password):
            session['user_id'] = user.id
            session.permanent = True
            return user.to_dict()
        elif user is None:
            return {'error': 'Invalid email or password'}, 404
        else:
            return {'error': 'Invalid email or password'}, 404

class Logout(Resource):
    def delete(self):
        session.get('user_id') == None

        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200

        return {}, 401

class ClearSession(Resource):
    def delete(self):
        session.get('user_id') == None
        return {}, 204

api.add_resource(SignUp, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(ClearSession, '/clear_session', endpoint='clear_session')