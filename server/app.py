from flask import Flask, make_response, jsonify, request, session, flash, redirect
from flask_restful import Resource, reqparse
import stripe
import json
from config import app, db, api, bcrypt
from models import User, Item, Order
import re
import os
from dotenv import load_dotenv



# @app.before_request
# def check_if_logged_in():
#     if not session.get('user_id'):
#         return {'error': 'Unauthorized, Please log in'}, 401

load_dotenv()
class HomePage(Resource):
    def get(self):
        return {'message': '200: Welcome to our Home Page'}, 200



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

class Users(Resource):
    def get(self):
        users = [u.to_dict() for u in User.query.all()]
        return make_response(users, 200)

class UserByID(Resource):
    def get(self, id):
        if id not in [i.id for i in User.query.all()]:
            return make_response({'message': 'User not Found, please try again'}, 404)
        return make_response((User.query.filter(User.id==id).first()).to_dict(), 200)

    def patch(self, id):
        if id not in [i.id for i in User.query.all()]:
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
        if id not in [i.id for i in User.query.all()]:
            return make_response({'message': 'User not Found, please try again'}, 404)
        else:
            db.session.query(Order).filter(Order.user_id == id).delete()
            user = User.query.filter(User.id==id).first()
            db.session.delete(user)
            db.session.commit()

            return make_response({'message': 'This User has been terminated!'}, 204)

class Items(Resource):
    def get(self):
        items = [i.to_dict() for i in Item.query.all()]
        return make_response(items, 200)

    def post(self):
        data = request.get_json()

        required_fields = ['name', 'category', 'image', 'description', 'in_stock', 'price', 'price_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_message = f"Missing required fields: {', '.join(missing_fields)}"
            return make_response(jsonify(error=error_message), 400)

        if not isinstance(data['name'], str) or not isinstance(data['category'], str) or not isinstance(data['description'], str):
            return make_response(jsonify(error="Invalid data type for 'name' or 'category' or 'description'"), 400)
        if not isinstance(data['image'], str) or not data['image'].startswith('http'):
            return make_response(jsonify(error="Invalid image URL"), 400)
        if not isinstance(data['in_stock'], bool):
            return make_response(jsonify(error="Invalid data type for 'in_stock'"), 400)
        if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
            return make_response(jsonify(error="Invalid price"), 400)
        if not isinstance(data['price_id'], str):
            return make_response(jsonify(error="Invalid data type for 'price_id'"), 400)


        new_item = Item(
            name = data['name'],
            category = data['category'],
            image = data['image'],
            description = data['description'],
            in_stock = data['in_stock'],
            price = data['price'],
            price_id = data['price_id']
        )

        db.session.add(new_item)
        db.session.commit()

        return make_response(new_item.to_dict(), 201)

class ItemByID(Resource):
    def get(self, id):
        if id not in [i.id for i in Item.query.all()]:
            return make_response({'message': 'Item not Found, please try again'}, 404)
        return make_response((Item.query.filter(Item.id==id).first()).to_dict(), 200)

    def patch(self, id):
        if id not in [i.id for i in Item.query.all()]:
            return make_response({'message': 'Item not Found, please try again'}, 404)
        else:
            data = request.get_json()

            if 'name' in data and (not isinstance(data['name'], str) or not data['name'].isalpha()):
                return make_response(jsonify(error="Invalid name format"), 400)
            if 'category' in data and (not isinstance(data['category'], str) or not data['category'].isalpha()):
                return make_response(jsonify(error="Invalid category format"), 400)
            if 'image' in data and (not isinstance(data['image'], str) or not data['image'].startswith('http')):
                return make_response(jsonify(error="Invalid image URL"), 400)
            if 'description' in data and not isinstance(data['description'], str):
                return make_response(jsonify(error="Invalid description format"), 400)
            if 'in_stock' in data and not isinstance(data['in_stock'], bool):
                return make_response(jsonify(error="Invalid in_stock format"), 400)
            if 'price' in data and (not isinstance(data['price'], (int, float)) or data['price'] <= 0):
                return make_response(jsonify(error="Invalid price format"), 400)
            if 'price_id' in data and not isinstance(data['price_id'], str):
                return make_response(jsonify(error="Invalid price_id format"), 400)

            item = Item.query.filter(Item.id==id).first()
            for key in data.keys():
                setattr(item, key, data[key])
            db.session.add(item)
            db.session.commit()

            return make_response(item.to_dict(), 200)

    def delete(self, id):
        if id not in [i.id for i in Item.query.all()]:
            return make_response({'message': 'Item not Found, please try again'}, 404)
        else:
            db.session.query(Order).filter(Order.item_id == id).delete()
            item = Item.query.filter(Item.id==id).first()
            db.session.delete(item)
            db.session.commit()

            return make_response({'message': 'This item is either out of stock or removed from menu!'}, 204)

class Orders(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return make_response({'error': 'please log in'}, 401)
        return make_response([o.to_dict() for o in Order.query.filter(Order.user_id == user_id, Order.status != 'completed').all()], 200)

    def post(self):
        data = request.get_json()

        if 'user_id' not in data or not isinstance(data['user_id'], int):
            return make_response(jsonify(error="Invalid user ID"), 400)
        if 'item_id' not in data or not isinstance(data['item_id'], int):
            return make_response(jsonify(error="Invalid item ID"), 400)
        if 'item_count' not in data or not isinstance(data['item_count'], int) or data['item_count'] <= 0:
            return make_response(jsonify(error="Invalid item count"), 400)

        new_order = Order(
            user_id = data['user_id'],
            item_id = data['item_id'],
            item_count = data['item_count'],
        )

        db.session.add(new_order)
        db.session.commit()

        return make_response(new_order.to_dict(), 201)

class OrderByID(Resource):
    def get(self, id):
        if id not in [i.id for i in Order.query.all()]:
            return make_response({'message': 'Order not Found, please try again'}, 404)
        return make_response((Order.query.filter(Order.id==id).first()).to_dict(), 200)

    def patch(self, id):
        if id not in [i.id for i in Order.query.all()]:
            return make_response({'message': 'Order not Found, please try again'}, 404)
        else:
            data = request.get_json()

            # if 'user_id' not in data or not isinstance(data['user_id'], int):
            #     return make_response(jsonify(error="Invalid user ID"), 401)
            # if 'item_id' not in data or not isinstance(data['item_id'], int):
            #     return make_response(jsonify(error="Invalid item ID"), 402)
            # if 'item_count' not in data or not isinstance(data['item_count'], int) or data['item_count'] <= 0:
            #     return make_response(jsonify(error="Invalid item count"), 403)

            order = Order.query.filter(Order.id==id).first()
            for key in data.keys():
                if key != 'status':
                    setattr(order, key, data[key])
            db.session.add(order)
            db.session.commit()

            return make_response(order.to_dict(), 200)

    def delete(self, id):
        if id not in [i.id for i in Order.query.all()]:
            return make_response({'message': 'Order not Found, please try again'}, 404)
        else:
            order = Order.query.filter(Order.id==id).first()
            db.session.delete(order)
            db.session.commit()

            return make_response({'message': 'This order has been settled!'}, 204)

class ClearCart(Resource):
    def get(self):
        user_id = session.get('user_id')
        db.session.query(Order).filter(Order.user_id == user_id).delete()
        db.session.commit()

        return {'message': 'cart is clear'}, 200


def calculate_order_amount(cart_items):
    total_amount = 0
    for item in cart_items:
        total_amount += item.item_count * item.item.price
    return int(total_amount * 100)

stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUR_DOMAIN = 'http://localhost:3000'

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    user_id = session.get('user_id')
    cart_items = Order.query.filter(Order.user_id == user_id, Order.status != 'completed').all()
    line_items = []
    user_email = User.query.filter(User.id == user_id).first().email
    for item in cart_items:
        line_items.append({
            'price': item.item.price_id,
            'quantity': item.item_count,
        })
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=user_email,
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/checkout/success',
            cancel_url=YOUR_DOMAIN + '/checkout/fail',
        )
        # print(checkout_session.status)
        # if checkout_session.status == 'complete':
        # print(checkout_session.status)
        for item in cart_items:
            item.status = 'completed'
        db.session.commit()


    except Exception as e:
        db.session.rollback()
        return str(e)

    return redirect(checkout_session.url, code=303)
endpoint_secret = 'whsec_2c88fc29d4ce3d969b71887b2f3026752ec785fe1cde73fccfdce7d535bd67f7'
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_data()
    event = None
    user_id = session.get('user_id')
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(event.type)

            cart_items = Order.query.filter(Order.user_id == user_id, Order.status != 'completed').all()

            for item in cart_items:
                item.status = 'completed'
            db.session.commit()

    except ValueError as e:
        return str(e), 400
    except stripe.error.SignatureVerificationError as e:
        return str(e), 400

    # Handle the payment_intent.succeeded event


    return '', 200



class CheckEmail(Resource):
    def get(self):
        email = request.args.get("email")
        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"error": "Invalid email address"}, 400
            # Check if email exists in the database
            user = User.query.filter_by(email=email).first()
            if user:
                return {"isUnique": False}
            return {"isUnique": True}
        return {"error": "Email not provided"}, 400

api.add_resource(CheckEmail, "/check-email")


api.add_resource(HomePage, '/', endpoint='home-page')
api.add_resource(SignUp, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(ClearSession, '/clear_session', endpoint='clear_session')
api.add_resource(Users, '/users', endpoint='users')
api.add_resource(UserByID, '/users/<int:id>')
api.add_resource(Items, '/items', endpoint='items')
api.add_resource(ItemByID, '/items/<int:id>')
api.add_resource(Orders, '/orders', endpoint='orders')
api.add_resource(OrderByID, '/orders/<int:id>')
api.add_resource(ClearCart, '/clearcart', endpoint='clearcart')

if __name__ == '__main__':
    app.run(port=5555, debug=True)