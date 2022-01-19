from dbFunctions import db, ma 
from marshmallow import Schema, fields

class User(db.Model):
    __tablename__ = 'user' #ovo je da znamo na koju tabelu u bazi se refereciramo
    name = db.Column(db.String(32))
    lastName = db.Column(db.String(32))
    address = db.Column(db.String(32))
    city = db.Column(db.String(32))
    country = db.Column(db.String(32))
    phoneNumber = db.Column(db.String(32))
    email = db.Column(db.String(32), primary_key=True)
    password = db.Column(db.String(32))
    cardNumber = db.Column(db.String(32))
    cardExpDate = db.Column(db.String(32))
    cardCode = db.Column(db.Integer)
    amount = db.Column(db.Integer)

    def __init__(self, _name, _lastName, _address, _city, _country, _phoneNumber, _email, _password, _cardNumber, _cardExpDate, _cardCode, _amount):
        self.name = _name
        self.lastName = _lastName
        self.address = _address
        self.city = _city
        self.country = _country
        self.phoneNumber = _phoneNumber        
        self.email = _email
        self.password = _password
        self.cardNumber = _cardNumber
        self.cardExpDate = _cardExpDate
        self.cardCode = _cardCode
        self.amount = _amount


#kreiramo semu kako bismo mogli da pretvaramo u json
class UserSchema(Schema):
    name = fields.Str()
    lastName = fields.Str()
    address = fields.Str()
    city = fields.Str()
    country = fields.Str()
    phoneNumber = fields.Str()
    email = fields.Str()
    password = fields.Str()
    cardNumber = fields.Str()
    cardExpDate = fields.Str()
    cardCode = fields.Int()
    amount = fields.Int()


class Wallet(db.Model):
    __tablename__ = 'wallet' #ovo je da znamo na koju tabelu u bazi se refereciramo
    userEmail = db.Column(db.String(32), primary_key=True)
    tether = db.Column(db.Float(38,10))
    bitcoin = db.Column(db.Float(38,10))
    litecoin = db.Column(db.Float(38,10))
    xrp  = db.Column(db.Float(38,10))
    dogecoin = db.Column(db.Float(38,10))
    stellar = db.Column(db.Float(38,10))
    ethereum = db.Column(db.Float(38,10))
    tron = db.Column(db.Float(38,10))
    chainlink = db.Column(db.Float(38,10))
    cardano = db.Column(db.Float(38,10))
    cosmos = db.Column(db.Float(38,10))
    polygon = db.Column(db.Float(38,10))
    solana = db.Column(db.Float(38,10))
    avalanche = db.Column(db.Float(38,10))
    polkadot = db.Column(db.Float(38,10))

    def __init__(self, _userEmail, _tether, _bitcoin, _litecoin, _xrp, _dogecoin, _stellar, _ethereum, _tron, _chainlink, _cardano, _cosmos, _polygon, _solana, _avalanche, _polkadot):
        self.tether = _tether
        self.userEmail = _userEmail
        self.bitcoin = _bitcoin
        self.litecoin = _litecoin
        self.xrp  = _xrp
        self.dogecoin = _dogecoin
        self.stellar = _stellar
        self.ethereum = _ethereum
        self.tron = _tron
        self.chainlink = _chainlink
        self.cardano = _cardano
        self.cosmos = _cosmos
        self.polygon = _polygon
        self.solana = _solana
        self.avalanche = _avalanche
        self.polkadot = _polkadot
        

class Transaction(db.Model):
    __tablename__ = 'transaction' #ovo je da znamo na koju tabelu u bazi se refereciramo
    hashId = db.Column(db.String(32), primary_key=True)
    userEmail = db.Column(db.String(32))
    initTime = db.Column(db.DateTime)    #vreme iniciranja transakcije
    status = db.Column(db.String(32))    #da li je transakcija odobrena ili odbijena
    targetEmail = db.Column(db.String(32))    #email na koji se prenosi novac
    cryptoType = db.Column(db.String(32))   #tip kripto valute koji se prenosi
    exchangedQuantity = db.Column(db.Float(38,10))  # kolicina koja je razmenjena

    def __init__(self, _hashId, _userEmail, _initTime, _status, _targetEmail, _cryptoType, _exchangedQuantity):
        self.hashId = _hashId
        self.userEmail = _userEmail
        self.initTime = _initTime
        self.status = _status
        self.targetEmail = _targetEmail
        self.cryptoType = _cryptoType;
        self.exchangedQuantity = _exchangedQuantity


class TransactionSchema(Schema):
    hashId = fields.Str()
    userEmail = fields.Str()
    initTime = fields.DateTime()
    status = fields.Str()
    targetEmail = fields.Str()
    cryptoType = fields.Str()
    exchangedQuantity = fields.Float()