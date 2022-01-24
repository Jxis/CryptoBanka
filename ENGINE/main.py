from ast import Return, arg
from email.message import EmailMessage
from multiprocessing.connection import wait
from random import Random, randint, random
import re
import string
from time import sleep
from tkinter.filedialog import SaveFileDialog
from unicodedata import decimal
from xmlrpc.client import DateTime
from flask import Flask
from requests.api import get
from datetime import date, datetime
import random
import hashlib, binascii
import sha3
from sha3 import keccak_256
import multiprocessing
from multiprocessing import Process, Lock, Queue
import threading 
from threading import Thread
import mysql.connector

app = Flask(__name__)

from flask import Flask, request, jsonify, session
import flask
from requests import Request, Session
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pymysql import cursors
from models import user
from models.user import TransactionSchema

from dbFunctions import app, userExists, SignUpUser, LoginData, AddCardInfo, AddUserToWalletTable, getUser, UpdateUser, AddMoneyToCard, ConvertUSDToTether, updateUserAmount, UserHaveWallet, addKriptoToWallet, GetUserWallet, PayFromWallet, AddTransactionToDB, ChangeTransactionStatus, AllTransactionsForTargerUser

session = Session()

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

@app.route('/buyKripto', methods=['GET', 'POST'])
def kupi():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    content = flask.request.json
    _nazivKripta = content['nazivKripta']
    _kolikoKripta = content['kolikoKripta']
    _ulozeno = content['ulozeno']
    _valutaPlacanja = content['valutaPlacanja']
    _mejl = content['mejl']

    randNum = random.randint(0,1000)
    rawId = _mejl + current_time + _ulozeno + str(randNum)
    hashId = sha3.keccak_256(rawId.encode('utf-8')).hexdigest()

    AddTransactionToDB(hashId, _mejl, current_time, 'In progress', 'cryptobanka@crypto.com', _valutaPlacanja, _ulozeno, 0, 'buyed')

    if UserHaveWallet(_mejl):
        userWallet = GetUserWallet(_mejl)
        provera = ProveraStanjaNovca(userWallet, _valutaPlacanja, _ulozeno)
        _code = provera['code']
        if _code == 200:
            PayFromWallet(_mejl, _valutaPlacanja , _ulozeno)

            #ako cemo cekati neko vreme
            ChangeTransactionStatus(hashId, 'Approved')
            addKriptoToWallet(_mejl, _nazivKripta, _kolikoKripta)
            retVal = {'message' : 'Kripto successfully added to wallet'}, provera['code']    
        else:
            retVal = {'message' : provera['message']}, provera['code']    

    else:

        retVal = {'message' : 'User does not have wallet.'}, 400    
    
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

@app.route('/wallet', methods=['GET'])
def wallet():
    content = flask.request.args
    email = content['email']
    
    if not userExists(email):
        return {'message': 'User does not exist.'}
    wallet = GetUserWallet(email)
    wallet_data = {
        'tether': wallet.tether,
        'bitcoin': wallet.bitcoin,
        'litecoin': wallet.litecoin,
        'xrp': wallet.xrp,
        'dogecoin': wallet.dogecoin,
        'stellar': wallet.stellar,
        'ethereum': wallet.ethereum,
        'tron': wallet.tron,
        'chainlink': wallet.chainlink,
        'cardano': wallet.cardano,
        'cosmos': wallet.cosmos,
        'polygon': wallet.polygon,
        'solana': wallet.solana,
        'avalanche': wallet.avalanche,
        'polkadot': wallet.polkadot
    }
     
    return wallet_data

@app.route('/newTransaction', methods=['POST'])
def transaction():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    content = flask.request.json
    _emailSender = content["emailSender"]
    _emailReciver = content["emailReciver"]
    _ulozeno = content["ulozeno"]
    _valuta = content["valuta"]    


    zaSkidanje = 1.05 * float(_ulozeno)

    randNum = random.randint(0,1000)
    rawId = _emailSender + _emailReciver + _ulozeno + str(randNum)
    hashId = sha3.keccak_256(rawId.encode('utf-8')).hexdigest()

    AddTransactionToDB(hashId, _emailSender, current_time, 'In progress', _emailReciver, _valuta, _ulozeno, float(_ulozeno)*0.05, 'transacted')

    if userExists(_emailReciver):
        if UserHaveWallet(_emailReciver):
            if UserHaveWallet(_emailSender):
                userWallet = GetUserWallet(_emailSender)
                provera = ProveraStanjaNovca(userWallet, _valuta, zaSkidanje)
                code = provera['code']
                if code == 200:
                    t = Process(target=WaitForApproval, args=[hashId, _emailReciver, _emailSender, _valuta , _ulozeno])
                    t.start()
                    
                    retVal = {'message' : 'Transaction from user: {} to user: {} is SUCCESSFUL'.format(_emailSender, _emailReciver)}, 200
                    return retVal
                else:
                    retVal = {'message' : 'User with {} mail does not have enough {} in wallet.'.format(_emailSender, _valuta)}, 400
            else:
                retVal = {'message' : 'User with {} mail does not have wallet.'.format(_emailSender)}, 400
        else:
            retVal = {'message' : 'User with {} mail does not have wallet.'.format(_emailReciver)}, 400
    else:
        retVal = {'message' : 'User with {} mail does not exists.'.format(_emailReciver)}, 400

    ChangeTransactionStatus(hashId, "Denied")
    return retVal

def TransactionThread(hashId, _emailReciver, _emailSender, _valuta , _ulozeno):
    PayFromWallet(_emailSender, _valuta , _ulozeno)

    #kreirati thread koji poziva nit
    #u threadu su sve funkcije ka bazi
    #ta nit ima sleep 
    #videti gde treba nova konekcija ka bazi

    p = Process(target=WaitForApproval, args=[hashId, _emailReciver, _valuta, _ulozeno])
    p.start()
    p.join()

def WaitForApproval(hashId, _emailReciver, _emailSender, _valuta , _ulozeno):
    mySQL = mysql.connector.connect(host = "localhost", user="root", password="baza", db="cryptoBank")
    cursor = mySQL.cursor()

    #PayFromWallet(_emailSender, _valuta , _ulozeno)
    #prebaciti u funkciju sve i dodati switch case po valuti
    cursor.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailSender,))
    iznosDecimal = cursor.fetchone()
    iznosFloat = float('.'.join(str(ele) for ele in iznosDecimal))
    print("prvo stanje na racunu = " + str(iznosFloat))
    noviIznos = iznosFloat - float(_ulozeno)
    cursor.execute(''' UPDATE wallet SET Tether = %s WHERE userEmail = %s ''', (noviIznos, _emailSender,))
    print("novi iznos = " + str(noviIznos))
    print("Paid from wallet")
    print("Now we wait...")

    mySQL.commit()

    sleep(10)

    #ChangeTransactionStatus(hashId, 'Approved')
    cursor.execute(''' UPDATE transaction SET status = %s WHERE hashId = %s ''', ("Approved", hashId,))

    #addKriptoToWallet(_emailReciver, _valuta, _ulozeno)
    cursor.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailReciver,))
    iznos = cursor.fetchone()
    iznosFloat = float('.'.join(str(ele) for ele in iznos))
    print("stanje kod primaoca = " + str(iznosFloat))
    noviIznos = iznosFloat + float(_ulozeno)
    cursor.execute(''' UPDATE wallet SET Tether = %s WHERE userEmail = %s ''', (noviIznos, _emailReciver,))

    cursor.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailReciver,))
    iznos = cursor.fetchone()
    iznosFloat = float('.'.join(str(ele) for ele in iznos))
    print("novo stanje kod primaoca = " + str(iznosFloat))

    mySQL.commit()

    cursor.close()
    print("DONE")

def ProveraStanjaNovca(userWallet,_valutaPlacanja, _ulozeno):
    match _valutaPlacanja:
        case 'Tether':
            if userWallet.tether >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Tether in wallet.', 'code' : 400}            
        case 'Bitcoin':
            if userWallet.bitcoin >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Bitcoin in wallet.', 'code' : 400}   
        case 'Litecoin':
            if userWallet.litecoin >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Bitcoin in wallet.', 'code' : 400}                 
        case 'XRP':
            if userWallet.xrp >= float(_ulozeno):
                retVal = {'code': 200} 
            else:
                retVal = {'message' : 'User does not have enought Litecoin in wallet.', 'code' : 400}
        case 'Dogecoin':
            if userWallet.dogecoin >= float(_ulozeno):
                retVal = {'code': 200}  
            else:
                retVal = {'message' : 'User does not have enought Dogecoin in wallet.', 'code' : 400}
        case 'Stellar':
            if userWallet.stellar >= float(_ulozeno):
                retVal = {'code': 200}  
            else:
                retVal = {'message' : 'User does not have enought Stellar in wallet.', 'code' : 400} 
        case 'Ethereum':
            if userWallet.ethereum >= float(_ulozeno):
                retVal = {'code': 200}    
            else:
                retVal = {'message' : 'User does not have enought Ethereum in wallet.', 'code' : 400}
        case 'TRON':
            if userWallet.tron >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought TRON in wallet.', 'code' : 400}
        case 'Chainlink':
            if userWallet.chainlink >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Chainlink in wallet.', 'code' : 400}
        case 'Cardano':
            if userWallet.cardano >= float(_ulozeno):
                retVal = {'code': 200} 
            else:
                retVal = {'message' : 'User does not have enought Cardano in wallet.', 'code' : 400}
        case 'Cosmos':
            if userWallet.cosmos >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Cosmos in wallet.', 'code' : 400}
        case 'Polygon':
            if userWallet.polygon >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Polygon in wallet.', 'code' : 400}
        case 'Solana':
            if userWallet.solana >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Solana in wallet.', 'code' : 400}
        case 'Avalanche':
            if userWallet.avalanche >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Avalanche in wallet.', 'code' : 400}
        case 'Polkadot':
            if userWallet.polkadot >= float(_ulozeno):
                retVal = {'code': 200}
            else:
                retVal = {'message' : 'User does not have enought Polkadot in wallet.', 'code' : 400}
    return retVal

@app.route('/transactionsTable', methods=['POST'])
def transactionsTable():
    content = flask.request.json
    email = content['email']
    lista = [0]

    lista = AllTransactionsForTargerUser(email)

    object_schema = TransactionSchema()
    json_string = object_schema.dumps(lista, many=True)
    return json_string

@app.route('/TransSortByTargetEmail', methods=['POST'])
def TransSortByTargetEmail():
    content = flask.request.json
    email = content['email']
    lista = [0]

    lista = AllTransactionsForTargerUser(email)

    tempSortEmail = getattr(session, "sortTargetEmail")

    if tempSortEmail == "False":
        lista.sort(key=lambda x: x.targetEmail)
        setattr(session, "sortTargetEmail", "True")
    else:
        lista.sort(key=lambda x: x.targetEmail, reverse=True)
        setattr(session, "sortTargetEmail", "False")

    object_schema = TransactionSchema()
    json_string = object_schema.dumps(lista, many=True)
    return json_string

@app.route('/TransSortByTime', methods=['POST'])
def TransSortByTime():
    content = flask.request.json
    email = content['email']
    lista = [0]

    lista = AllTransactionsForTargerUser(email)

    tempSortTime = getattr(session, "sortTime")

    if tempSortTime == "False":
        lista.sort(key=lambda x: x.initTime)
        setattr(session, "sortTime", "True")
    else:
        lista.sort(key=lambda x: x.initTime, reverse=True)
        setattr(session, "sortTime", "False")

    object_schema = TransactionSchema()   
    json_string = object_schema.dumps(lista, many=True)

    return json_string

@app.route('/filterTransactions', methods=['POST'])
def filterTransactions():
    content = flask.request.json
    email = content['email']
    targetEmail = content['targetEmail']
    initTimeStart1 = content['initTimeStart']
    initTimeEnd1 = content['initTimeEnd']
    crypto = content['crypto']

    lista = AllTransactionsForTargerUser(email)

    newList = []

    if targetEmail != "" and initTimeStart1 != "" and initTimeEnd1 != "" and crypto != "":  
        initTimeStart = datetime.strptime(initTimeStart1, '%Y-%m-%d %H:%M:%S')
        initTimeEnd = datetime.strptime(initTimeEnd1, '%Y-%m-%d %H:%M:%S')
        for t in lista:
            if t.targetEmail == targetEmail and t.initTime >= initTimeStart and t.initTime <= initTimeEnd and t.cryptoType == crypto:
                newList.append(t)

    elif targetEmail == "" and initTimeStart1 != "" and initTimeEnd1 != "" and crypto == "": 
        initTimeStart = datetime.strptime(initTimeStart1, '%Y-%m-%d %H:%M:%S')
        initTimeEnd = datetime.strptime(initTimeEnd1, '%Y-%m-%d %H:%M:%S')
        for t in lista:
            if t.initTime >= initTimeStart and t.initTime <= initTimeEnd:
                newList.append(t)

    elif targetEmail != "" and initTimeStart1 == "" and initTimeEnd1 == "" and crypto == "": 
        for t in lista:
            if t.targetEmail == targetEmail:
                newList.append(t)

    elif targetEmail == "" and initTimeStart1 == "" and initTimeEnd1 == "" and crypto != "": 
        for t in lista:
            if t.cryptoType == crypto:
                newList.append(t)

    elif targetEmail != "" and initTimeStart1 == "" and initTimeEnd1 == "" and crypto != "": 
        for t in lista:
            if t.cryptoType == crypto and t.targetEmail == targetEmail:
                newList.append(t)

    elif targetEmail != "" and initTimeStart1 != "" and initTimeEnd1 != "" and crypto == "": 
        initTimeStart = datetime.strptime(initTimeStart1, '%Y-%m-%d %H:%M:%S')
        initTimeEnd = datetime.strptime(initTimeEnd1, '%Y-%m-%d %H:%M:%S')
        for t in lista:
            if t.targetEmail == targetEmail and t.initTime >= initTimeStart and t.initTime <= initTimeEnd:
                newList.append(t)

    elif targetEmail == "" and initTimeStart1 != "" and initTimeEnd1 != "" and crypto != "": 
        initTimeStart = datetime.strptime(initTimeStart1, '%Y-%m-%d %H:%M:%S')
        initTimeEnd = datetime.strptime(initTimeEnd1, '%Y-%m-%d %H:%M:%S')
        for t in lista:
            if t.cryptoType == crypto and t.initTime >= initTimeStart and t.initTime <= initTimeEnd:
                newList.append(t)

    object_schema = TransactionSchema()   
    json_string = object_schema.dumps(newList, many=True)

    return json_string

if __name__ == "__main__":
    setattr(session, "sortTargetEmail", "False")
    setattr(session, "sortTime", "False")
    app.run(port=5001)