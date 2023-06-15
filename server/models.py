from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from sqlalchemy.ext.associationproxy import association_proxy

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-orders', '-_password_hash', '-password_confirmation',)

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    password_confirmation = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    points = db.Column(db.Integer, default=0)

    orders = db.relationship('Order', backref='user')
    items = association_proxy('orders', 'item')
    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @staticmethod
    def simple_hash(input):
        return sum(bytearray(input, encoding='utf-8'))


class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    serialize_rules = ('users', 'orders', '-orders.item',)

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    in_stock = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, db.CheckConstraint('price > 0'), nullable=False)
    price_id = db.Column(db.String)

    orders = db.relationship('Order', backref='item')
    users = association_proxy('orders', 'user')

    __table_args__ = (
        db.CheckConstraint('price > 0'),
    )
    
class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'

    serialize_rules = ('-item.orders', '-user._password_hash', '-user.password_confirmation',)

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable = False)
    item_count = db.Column(db.Integer)
    status = db.Column(db.String, default='pending')


