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
    cardNumber = db.Column(db.Integer)
    cardExpDate = db.Column(db.String(32))
    cardCode = db.Column(db.Integer)

    def __init__(self, _name, _lastName, _address, _city, _country, _phoneNumber, _email, _password, _cardNumber, _cardExpDate, _cardCode):
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


#kreiramo semu kako bismo mogli da pretvaramo u json
class UserSchema(Schema):
    user_id = fields.Number()
    ime = fields.Str()
    prezime = fields.Str()
    adresa = fields.Str()
    grad = fields.Str()
    brojTelefona = fields.Str()
    email = fields.Str()
    loinka = fields.Str()
    brojKartice = fields.Str()
    datumIsteka = fields.Str()
    sigKod = fields.Str()

