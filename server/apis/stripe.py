import stripe
from dotenv import load_dotenv
import os
from models import User, Order
from config import app, db

load_dotenv()
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