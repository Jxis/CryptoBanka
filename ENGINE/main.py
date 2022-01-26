from ast import Return, arg
from email.message import EmailMessage
from multiprocessing.connection import wait
from random import Random, randint, random
import re
from reprlib import recursive_repr
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
from sqlalchemy import false, true

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
        retVal = {'message' : 'User with the same email already signed up'}, 400
        return retVal

    _name = content['name']
    _lastName = content['lastName']
    _address = content['address']
    _city = content['city']
    _country = content['country']
    _phoneNumber = str(content['phoneNumber'])
    _password = str(content['password'])
    _cardNumber = content['cardNumber']
    _cardExpDate = content['cardExpDate']
    _cardCode = content['cardCode']
    _amount = content['amount']

    if len(_name) <1 :
        retVal = {'message' : 'Username must be longer.'}, 400    
        return retVal
    elif len(_lastName) <1 :
        retVal = {'message' : 'Lastname must be longer.'}, 400    
        return retVal
    elif len(_address) <1 :
        retVal = {'message' : 'Address must be longer.'}, 400    
        return retVal
    elif len(_city) <1 :
        retVal = {'message' : 'City must be longer.'}, 400    
        return retVal
    elif len(_country) <1 :
        retVal = {'message' : 'Country must be longer.'}, 400    
        return retVal
    elif int(_phoneNumber) < 1:
        retVal = {'message' : 'You must enter your phone number.'}, 400    
        return retVal
    elif int(_password) < 1:
        retVal = {'message' : 'You must enter your password'}, 400  
        return retVal

 
   
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

    _today = datetime.now()
    tt = _today.strftime("%Y-%m-%d")
    t = datetime.strptime(tt, "%Y-%m-%d")
    time = datetime.strptime(_expDate, "%Y-%m-%d")


    if len(_cardNum) != 16:
        retVal = {'message' : 'Wrong card number.'}, 400    
        return retVal
    elif len(_cardCode) != 3:
        retVal = {'message' : 'Wrong card code.'}, 400    
        return retVal
    elif int(_amount) < 1:
        retVal = {'message' : 'You need to have more than 1$ on your bank account.'}, 400    
        return retVal
    elif time <= t:
        retVal = {'message' : 'Your bank card expired.'}, 400  
        return retVal
    elif len(_name) < 2 :
        retVal = {'message' : 'Name must be longer'}, 400    
        return retVal
    elif len(_expDate) < 2 :
        retVal = {'message' : 'Date not correct'}, 400    
        return retVal

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

    if len(_ulozeno) < 10:
        retVal = {'message' : 'Morate uloziti vise novca.'}, 400    

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
        retVal = {'message' : 'User with this email does not exist'}, 400
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
    elif int(_addedMoney) < 2:
        retVal = {'message' : 'You must add more money.'}, 400
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

    kolicina = str(content['usdAmount'])

    if int(kolicina) < 2:
        retVal = {'message' : 'You must add more money to convert.'}, 400
        return retVal
    elif boolean == True:
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
    if not UserHaveWallet(email):
        return {'message': 'User is not verified.'}, 401
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
    _emailReciever = content["emailReciver"]
    _ulozeno = content["ulozeno"]
    _valuta = content["valuta"]    

    if(_emailSender is '' or _emailReciever is '' or _ulozeno is ''):
        retVal = {'message' : 'All fields must have values!'}, 400
        return retVal

    randNum = random.randint(0,1000)
    rawId = _emailSender + _emailReciever + _ulozeno + str(randNum)
    hashId = sha3.keccak_256(rawId.encode('utf-8')).hexdigest()

    #nit koji proverava validnost transakcije, skida novac i poziva proces koji onda ceka 5min i upisuje nove podatke u bazu
    p = Process(target=TransactionProcess, args=[current_time, hashId, _emailSender, _emailReciever, _valuta , _ulozeno])
    p.start()
    
    retVal = {'message' : 'Transaction from user: {} to user: {} is IN PROGRESS'.format(_emailSender, _emailReciever)}, 200
    return retVal

def TransactionProcess(current_time, hashId, _emailSender, _emailReciever, _valuta, _ulozeno):
    #mora da se kreira nova konekcija sa bazom jer svaki proces i nit zauzima novi memorijski prostor za sebe 
    mySQL = mysql.connector.connect(host = "localhost", user="root", password="baza", db="cryptoBank")
    
    gas = 0.05 * float(_ulozeno)
    #AddTransactionToDB(hashId, _emailSender, current_time, 'In progress', _emailReciever, _valuta, _ulozeno, float(_ulozeno)*0.05, 'transacted')
    c1 = mySQL.cursor()
    c1.execute(''' INSERT INTO transaction (hashId, userEmail, initTime, status, targetEmail, cryptoType, exchangedQuantity, gas, transactionType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ''',(hashId, _emailSender, current_time, "In progress", _emailReciever, _valuta, _ulozeno, gas, 'transacted'))
    mySQL.commit()
    c1.close()

    q = Queue()
    t = Thread(target=WaitForApprovalThread, args=[q, _emailSender, _emailReciever, _valuta, float(_ulozeno)])
    t.start()           
    #cekamo da prodje 5min        
    result = q.get()
    if(result is true):
        #ok
        c6 = mySQL.cursor()
        #ChangeTransactionStatus(hashId, 'Approved')
        c6.execute(''' UPDATE transaction SET status = %s WHERE hashId = %s ''', ("Approved", hashId,))
        c6.close()
        mySQL.commit()

        c7 = mySQL.cursor()
        #addKriptoToWallet(_emailReciever, _valuta, _ulozeno)
        match _valuta:
            case 'Tether':
                c7.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Bitcoin':
                c7.execute(''' SELECT Bitcoin FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Litecoin':
                c7.execute(''' SELECT Litecoin FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'XRP':
                c7.execute(''' SELECT XRP FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Dogecoin':
                c7.execute(''' SELECT Dogecoin FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Stellar':
                c7.execute(''' SELECT Stellar FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Ethereum':
                c7.execute(''' SELECT Ethereum FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'TRON':
                c7.execute(''' SELECT TRON FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Chainlink':
                c7.execute(''' SELECT Chainlink FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Cardano':
                c7.execute(''' SELECT Cardano FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Cosmos':
                c7.execute(''' SELECT Cosmos FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Polygon':
                c7.execute(''' SELECT Polygon FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Solana':
                c7.execute(''' SELECT Solana FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Avalanche':
                c7.execute(''' SELECT Avalanche FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
            case 'Polkadot':
                c7.execute(''' SELECT Polkadot FROM wallet WHERE userEmail = %s ''', (_emailReciever,))
        iznos = c7.fetchone()
        c7.close()
        iznosFloat = float('.'.join(str(ele) for ele in iznos))
        noviIznos = iznosFloat + float(_ulozeno)

        c8 = mySQL.cursor()
        match _valuta:
            case 'Tether':
                c8.execute(''' UPDATE wallet SET Tether = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Bitcoin':
                c8.execute(''' UPDATE wallet SET Bitcoin = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Litecoin':
                c8.execute(''' UPDATE wallet SET Litecoin = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'XRP':
                c8.execute(''' UPDATE wallet SET XRP = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Dogecoin':
                c8.execute(''' UPDATE wallet SET Dogecoin = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Stellar':
                c8.execute(''' UPDATE wallet SET Stellar = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Ethereum':
                c8.execute(''' UPDATE wallet SET Ethereum = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'TRON':
                c8.execute(''' UPDATE wallet SET TRON = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Chainlink':
                c8.execute(''' UPDATE wallet SET Chainlink = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Cardano':
                c8.execute(''' UPDATE wallet SET Cardano = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Cosmos':
                c8.execute(''' UPDATE wallet SET Cosmos = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Polygon':
                c8.execute(''' UPDATE wallet SET Polygon = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Solana':
                c8.execute(''' UPDATE wallet SET Solana = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Avalanche':
                c8.execute(''' UPDATE wallet SET Avalanche = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
            case 'Polkadot':
                c8.execute(''' UPDATE wallet SET Polkadot = %s WHERE userEmail = %s ''', (noviIznos, _emailReciever,))
        c8.close()
        mySQL.commit()       
    else:
        #not ok
        #ChangeTransactionStatus(hashId, "Denied")
        c6 = mySQL.cursor()
        c6.execute(''' UPDATE transaction SET status = %s WHERE hashId = %s ''', ("Denied", hashId,))
        c6.close()
        mySQL.commit()
        #vrati mu pare na racun ako je odbijeno
        c5 = mySQL.cursor()
        match _valuta:
            case 'Tether':
                c5.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Bitcoin':
                c5.execute(''' SELECT Bitcoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Litecoin':
                c5.execute(''' SELECT Litecoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'XRP':
                c5.execute(''' SELECT XRP FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Dogecoin':
                c5.execute(''' SELECT Dogecoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Stellar':
                c5.execute(''' SELECT Stellar FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Ethereum':
                c5.execute(''' SELECT Ethereum FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'TRON':
                c5.execute(''' SELECT TRON FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Chainlink':
                c5.execute(''' SELECT Chainlink FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Cardano':
                c5.execute(''' SELECT Cardano FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Cosmos':
                c5.execute(''' SELECT Cosmos FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Polygon':
                c5.execute(''' SELECT Polygon FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Solana':
                c5.execute(''' SELECT Solana FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Avalanche':
                c5.execute(''' SELECT Avalanche FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
            case 'Polkadot':
                c5.execute(''' SELECT Polkadot FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                iznosDec = c5.fetchone()
                iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
        c5.close()

        c9 = mySQL.cursor()
        zaPlacanje = 1.05 * _ulozeno
        preostalo = iznosFloat + zaPlacanje
        #PayFromWallet(_emailSender, _valuta , _ulozeno)
        match _valuta:
            case 'Tether':
                c9.execute(''' UPDATE wallet SET Tether = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Bitcoin':
                c9.execute(''' UPDATE wallet SET Bitcoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Litecoin':
                c9.execute(''' UPDATE wallet SET Litecoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'XRP':
                c9.execute(''' UPDATE wallet SET XRP = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Dogecoin':
                c9.execute(''' UPDATE wallet SET Dogecoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Stellar':
                c9.execute(''' UPDATE wallet SET Stellar = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Ethereum':
                c9.execute(''' UPDATE wallet SET Ethereum = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'TRON':
                c9.execute(''' UPDATE wallet SET TRON = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Chainlink':
                c9.execute(''' UPDATE wallet SET Chainlink = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Cardano':
                c9.execute(''' UPDATE wallet SET Cardano = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Cosmos':
                c9.execute(''' UPDATE wallet SET Cosmos = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Polygon':
                c9.execute(''' UPDATE wallet SET Polygon = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Solana':
                c9.execute(''' UPDATE wallet SET Solana = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Avalanche':
                c9.execute(''' UPDATE wallet SET Avalanche = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
            case 'Polkadot':
                c9.execute(''' UPDATE wallet SET Polkadot = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
        c9.close()
        mySQL.commit()


#placa iz novcanika i ceka 5min
def WaitForApprovalThread(q, _emailSender, _emailReciever, _valuta, _ulozeno):
    if(_emailReciever == _emailSender):
        sleep(30)
        q.put(false)
        return 

    mySQL = mysql.connector.connect(host = "localhost", user="root", password="baza", db="cryptoBank")
    
    c2 = mySQL.cursor()
    c2.execute(''' SELECT name FROM user WHERE email = %s ''', (_emailReciever,))
    name = c2.fetchone()
    #if userExists(_emailReciever):
    if(name is not None):
        c3 = mySQL.cursor()
        c3.execute(''' SELECT cardNumber FROM user WHERE email = %s ''', (_emailReciever,))
        cardNumber = c3.fetchone()
        c3.close()
        #if UserHasWallet(_emailReciever):
        if(cardNumber != '0'):
            c4 = mySQL.cursor()
            c4.execute(''' SELECT cardNumber FROM user WHERE email = %s ''', (_emailSender,))
            cardNumber = c4.fetchone()
            #if UserHasWallet(_emailSender):
            if(cardNumber != '0'):
                #proveriti da li ima dovoljno novca da mu se skine ta valuta
                c5 = mySQL.cursor()
                match _valuta:
                    case 'Tether':
                        c5.execute(''' SELECT Tether FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Bitcoin':
                        c5.execute(''' SELECT Bitcoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Litecoin':
                        c5.execute(''' SELECT Litecoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'XRP':
                        c5.execute(''' SELECT XRP FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Dogecoin':
                        c5.execute(''' SELECT Dogecoin FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Stellar':
                        c5.execute(''' SELECT Stellar FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Ethereum':
                        c5.execute(''' SELECT Ethereum FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'TRON':
                        c5.execute(''' SELECT TRON FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Chainlink':
                        c5.execute(''' SELECT Chainlink FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Cardano':
                        c5.execute(''' SELECT Cardano FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Cosmos':
                        c5.execute(''' SELECT Cosmos FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Polygon':
                        c5.execute(''' SELECT Polygon FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Solana':
                        c5.execute(''' SELECT Solana FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Avalanche':
                        c5.execute(''' SELECT Avalanche FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                    case 'Polkadot':
                        c5.execute(''' SELECT Polkadot FROM wallet WHERE userEmail = %s ''', (_emailSender,))
                        iznosDec = c5.fetchone()
                        iznosFloat = float('.'.join(str(ele) for ele in iznosDec))
                c5.close()
                zaSkidanje = 1.05 * _ulozeno
                if(zaSkidanje <= iznosFloat):
                    #sve ok
                    sleep(30)
                    c9 = mySQL.cursor()
                    zaPlacanje = 1.05 * _ulozeno
                    preostalo = iznosFloat - zaPlacanje
                    #PayFromWallet(_emailSender, _valuta , _ulozeno)
                    match _valuta:
                        case 'Tether':
                            c9.execute(''' UPDATE wallet SET Tether = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Bitcoin':
                            c9.execute(''' UPDATE wallet SET Bitcoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Litecoin':
                            c9.execute(''' UPDATE wallet SET Litecoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'XRP':
                            c9.execute(''' UPDATE wallet SET XRP = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Dogecoin':
                            c9.execute(''' UPDATE wallet SET Dogecoin = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Stellar':
                            c9.execute(''' UPDATE wallet SET Stellar = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Ethereum':
                            c9.execute(''' UPDATE wallet SET Ethereum = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'TRON':
                            c9.execute(''' UPDATE wallet SET TRON = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Chainlink':
                            c9.execute(''' UPDATE wallet SET Chainlink = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Cardano':
                            c9.execute(''' UPDATE wallet SET Cardano = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Cosmos':
                            c9.execute(''' UPDATE wallet SET Cosmos = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Polygon':
                            c9.execute(''' UPDATE wallet SET Polygon = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Solana':
                            c9.execute(''' UPDATE wallet SET Solana = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Avalanche':
                            c9.execute(''' UPDATE wallet SET Avalanche = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                        case 'Polkadot':
                            c9.execute(''' UPDATE wallet SET Polkadot = %s WHERE userEmail = %s ''', (preostalo, _emailSender,))
                    c9.close()
                    mySQL.commit()
                    q.put(true)
                    return
    sleep(30)
    q.put(false)
    return
                        
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