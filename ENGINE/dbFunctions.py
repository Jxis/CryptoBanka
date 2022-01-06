from flask import Flask, request, jsonify
import flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pymysql import cursors
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