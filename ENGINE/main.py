from flask import Flask
from requests.api import get

app = Flask(__name__)

from flask import Flask, request, jsonify
import flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pymysql import cursors
from models import user
from dbFunctions import app, userExists, SignUpUser, LoginData, AddCardInfo, AddUserToWalletTable, getUser, UpdateUser, AddMoneyToCard, ConvertUSDToTether, GetUserWallet

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

    if len(_cardNum) != 16:
        retVal = {'message' : 'Wrong card number.'}, 400    
        return retVal
    elif len(_cardCode) != 3:
        retVal = {'message' : 'Wrong card code.'}, 400    
        return retVal
    elif int(_amount) < 1:
        retVal = {'message' : 'You need to have more than 1$ on your bank account.'}, 400    
        return retVal
    #elif date(_expDate, '%m/%d/%y') <= datetime.now:
    #    retVal = {'message' : 'Your bank card expired.'}, 400    
    #    return retVal

    newAmount = int(_amount) - 1

    AddUserToWalletTable(_email, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    if AddCardInfo(_email, _cardNum, _name, _expDate, _cardCode, newAmount):
        retVal = {'message' : 'Successfully added data'}, 200    
        print("Trebalo bi sve da je okej")
        return retVal
    else:
        retVal = {'message' : 'Cant add card info'}, 400    
        return retVal

@app.route('/user', methods=['GET'])
def user():
    content = flask.request.args
    email = content['email']
    
    if not userExists(email):
        return {'message': 'User does not exist.'}
    user = getUser(email)
    user_data = {
        'name': user.name,
        'lastName': user.lastName,
        'address': user.address,
        'city': user.city,
        'country': user.country,
        'phoneNumber': user.phoneNumber,
        'email': user.email,
        'password': user.password,
        'cardNumber': user.cardNumber,
        'cardExpDate': user.cardExpDate,
        'cardCode': user.cardCode,
        'amount': user.amount
    }

    return user_data

@app.route('/editUser', methods=['POST'])
def editUser():
    content = flask.request.json
    _email = content['email']

    if not userExists(_email):
        retVal = {'message' : 'User with this email doesn-t exist'}, 400
        return retVal

    _name = content['name']
    _lastName = content['lastName']
    _address = content['address']
    _city = content['city']
    _country = content['country']
    _phoneNumber = content['phoneNumber']
    _password = content['password']
  
    UpdateUser(_name, _lastName, _address, _city, _country, _phoneNumber, _email, _password)
    retVal = {'message' : 'User successfully updated.'}, 200

    return retVal

@app.route("/addMoney", methods=['POST'])
def addMoney():
    content = flask.request.json
    _email = content['email']
    _addedMoney = content['addedMoney']

    if not userExists(_email):
        retVal = {'message' : 'User with this email doesn-t exist'}, 400
        return retVal
    
    AddMoneyToCard(_email, _addedMoney)
    retVal = {'message' : 'Money successfully added.'}, 200
    return retVal

@app.route('/convertUSDToTether', methods=['POST'])
def convertUSDToTether():
    content = flask.request.json
    email = content['email']
    usdAmount = content['usdAmount']
    boolean = ConvertUSDToTether(email, usdAmount)

    if boolean == True:
        retVal = {'message' : 'Money successfully added.'}, 200
    else:
        retVal = {'message' : 'Not enough money on the account.'}, 400
    return retVal

if __name__ == "__main__":
    app.run(port=5001)