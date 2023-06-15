from flask_restful import Resource
from config import api, db
from models import Order
from flask import make_response, request

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

api.add_resource(Orders, '/orders', endpoint='orders')
api.add_resource(OrderByID, '/orders/<int:id>')
api.add_resource(ClearCart, '/clearcart', endpoint='clearcart')