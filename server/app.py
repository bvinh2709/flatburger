from flask import Flask, make_response, jsonify, request, session, redirect
from flask_restful import Resource
from config import app, db, api, bcrypt
from apis import home_page, users, auth, items, orders, stripe

home_page
users
auth
items
orders
stripe

if __name__ == '__main__':
    app.run(port=5555, debug=True)