from flask import Flask

app = Flask(__name__)

from flask import Flask, request, jsonify
import flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pymysql import cursors
from models import user
from dbFunctions import app, userExists, SignUpUser, LoginData, AddCardInfo, AddUserToWalletTable

@app.route('/sign_up', methods=['POST'])
def signup():
    content = flask.request.json

    _email = content['email']

    if userExists(_email):
        retVal = {'message' : 'User with the sam email already signed up'}, 400
        return retVal

    _name = content['name']
    _lastName = content['lastName']
    _address = content['address']
    _city = content['city']
    _country = content['country']
    _phoneNumber = str(content['phoneNumber'])
   # _email = content['email']
    _password = str(content['password'])
    _cardNumber = content['cardNumber']
    _cardExpDate = content['cardExpDate']
    _cardCode = content['cardCode']
    _amount = content['amount']

    SignUpUser(_name, _lastName, _address, _city, _country, _phoneNumber, _email, _password, _cardNumber, _cardExpDate, _cardCode, _amount)
    retVal = {'message' : 'User successfully signed up'}, 200

    return retVal

@app.route('/login', methods=['POST'])
def login():
    content = flask.request.json
    _email = content['email']
    _password = content['password']

    if LoginData(_email, _password) == False:
        retVal = {'message' : 'Wrong email or password'}, 400    
        return retVal
    else:
        retVal = {'message' : 'User successfully loged in'}, 200
        return retVal


@app.route('/verify', methods=['POST'])
def verify():
    content = flask.request.json
    _cardNum = content['cardNum']
    _name = content['name']
    _expDate = content['expDate']
    _cardCode = content['cardCode']
    _amount = content['amount']
    _email = content['email']

    AddUserToWalletTable(_email, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    if AddCardInfo(_email, _cardNum, _name, _expDate, _cardCode, _amount):
        retVal = {'message' : 'Successfully added data'}, 200    
        print("Trebalo bi sve da je okej")
        return retVal
    else:
        retVal = {'message' : 'Cant add card info'}, 400    
        return retVal

if __name__ == "__main__":
    app.run(port=5001)