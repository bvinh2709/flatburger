from flask_restful import Resource
from config import api, db
from models import Item, Order
from flask import make_response, request

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

api.add_resource(Items, '/items', endpoint='items')
api.add_resource(ItemByID, '/items/<int:id>')