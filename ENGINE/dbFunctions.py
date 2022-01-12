from flask import Flask, request, jsonify
import flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow.fields import Decimal
from pymysql import NULL, cursors
from models import user

db=SQLAlchemy()
ma=Marshmallow()

#from config import db, ma  #mislim da nam ovo ni ne treba jer sam ja stavila sve ovde

app = Flask(__name__)

#ukoliko budemo pisali ciste sql upite
mysql = MySQL()
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'baza'
#app.config['MYSQL_DATABASE_DB'] = 'cryptoBank' #kako se zove nasa baza
#app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#mysql.init_app(app)

#Ako budemo, umesto cistih sql upita, koristili komande vezane za sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:baza@127.0.0.1/cryptoBank'
db.init_app(app)
ma.init_app(app)
#db.create_all()

#------------------------------ DATA BASE FUNCTIONS ----------------------------------

def userExists(email: str) -> bool:
    #connection = mysql.connect()
    #cursors = connection.cursor()
    #cursors.execute("SELECT * from user WHERE email = %s", (email))
    #data = cursors.fetchone()
    #cursors.close()
    #if data:
    #    return True
    #else:
    #    return False

    ret = False
    users = user.User.query.all()
    for temp in users:
        if temp.email == email:
            ret = True
    return ret

def getUser(email):
    if(userExists(email)):
        users = user.User.query.all()
        for temp in users:
            if temp.email == email:
                return temp
    return None

def updateUserAmount(email, amount):
    user = getUser(email)
    user.amount = amount
    db.session.commit()

def SignUpUser(name, lastName, address, city, country, phoneNumber, email, password, cardNumber, cardExpData, cardCode,amount):
    u = user.User(name, lastName, address, city, country, phoneNumber, email, password, cardNumber, cardExpData, cardCode, amount)
    db.session.add(u)
    db.session.commit()

    #connection = mysql.connect()
    #cursors = connection.cursor()
    #cursors.execute("insert into user values (%s, %s, %s, %s, %s, %s, %s, %s, %d, %s, %d)", (name, lastName, address, city, country, phoneNumber, email, password, cardNumber, cardExpData, cardCode))
    # INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #mysql.connect().commit();
    #cursors.close();

def UpdateUser(name, lastName, address, city, country, phoneNumber, email, password):
    u = getUser(email)
    u.name = name
    u.lastName = lastName
    u.address = address
    u.city = city
    u.country = country
    u.phoneNumber = phoneNumber
    if(password != '' and password != ""):
        u.password = password
    db.session.commit()

#Funkcija koja ucitava sve usere iz baze i proverava da li postoji korisnik sa datim emailom i lozinkom
def LoginData(email: str, password: str) -> bool:
    ret = False
    list_of_users = user.User.query.all()
    for temp in list_of_users:
        if temp.email == email:
            if temp.password == password:
                ret = True
            else:
                ret = False
    return ret


def AddCardInfo(email, cardNum, name, expDate, cardCode, amount):
    if userExists(email) == True:
        num_rows_updated = user.User.query.filter_by(email=email).update(dict(cardNumber = cardNum, cardExpDate = expDate, cardCode = cardCode, amount = amount))
        db.session.commit()
        return True
    else:
        return False

#*****
def AddUserToWalletTable(email, tether, bitcoin, litecoin, xrp, dogecoin, stellar, ethereum, tron, chainlink, cardano, cosmos, polygon, solana, avalanche, polkadot):
    u = user.Wallet(email, tether, bitcoin, litecoin, xrp, dogecoin, stellar, ethereum, tron, chainlink, cardano, cosmos, polygon, solana, avalanche, polkadot)
    db.session.add(u)
    db.session.commit()

def getUsersWallet(email):
    wallets = user.Wallet.query.all()
    for temp in wallets:
        if temp.userEmail == email:
            return temp
    return NULL

def addKriptoToWallet(email, kriptoName, kriptoAmount):
    wallet = getUsersWallet(email)
    match kriptoName:
        case 'Tether':
            wallet.tether += float(kriptoAmount) 
        case 'Bitcoin':
            wallet.bitcoin = float(wallet.bitcoin) + float(kriptoAmount) 
        case 'Litecoin':
            wallet.litecoin += float(kriptoAmount) 
        case 'XRP':
            wallet.xrp += float(kriptoAmount) 
        case 'Dogecoin':
            wallet.dogecoin += float(kriptoAmount) 
        case 'Stellar':
            wallet.stellar += float(kriptoAmount) 
        case 'Ethereum':
            wallet.ethereum += float(kriptoAmount)
        case 'TRON':
            wallet.tron += float(kriptoAmount)
        case 'Chainlink':
            wallet.chainlink += float(kriptoAmount)
        case 'Cardano':
            wallet.cardano += float(kriptoAmount)
        case 'Cosmos':
            wallet.cosmos += float(kriptoAmount)
        case 'Polygon':
            wallet.polygon += float(kriptoAmount)
        case 'Solana':
            wallet.solana += float(kriptoAmount)
        case 'Avalanche':
            wallet.avalanche += float(kriptoAmount)
        case 'Polkadot':
            wallet.polkadot += float(kriptoAmount) 
    db.session.commit();

def AddMoneyToCard(email, addedMoney):
    u = getUser(email)
    if u == None:
        return
    u.amount += int(addedMoney)
    db.session.commit()

def GetUserWallet(email):
    if(userExists(email)):
        wallets = user.Wallet.query.all()
        for temp in wallets:
            if temp.userEmail == email:
                return temp
    return None

def ConvertUSDToTether(email, usdAmount):
    if not userExists(email):
        return False
    u = getUser(email)
    w = GetUserWallet(email)
    intUSD = int(usdAmount)
    if u.amount >= intUSD:
        u.amount -= intUSD
        w.tether += intUSD
        db.session.commit()
        return True
    return False


#Upis nove transakcije u bazu  (istestirati kad se napravi za transakciju)
def AddTransactionToDB(_hashId, _userEmail, _initTime, _status, _targetEmail, _cryptoType, _currentCryptoValue, _exchangedQuantity):
    tr = user.Transaction(_hashId, _userEmail, _initTime, _status, _targetEmail, _cryptoType, _currentCryptoValue, _exchangedQuantity)
    db.session.add(tr)
    db.session.commit()


def AllTransactionsForTargerUser(email: str):
    listOfAllTransactions = user.Transaction.query.all()
    listOfTargetTransactions = []

    for transaction in listOfAllTransactions:
        if(transaction.userEmail == email):
            listOfTargetTransactions.append(transaction)

    return listOfTargetTransactions