from email import message
from getpass import getuser
from types import MethodDescriptorType
from flask import Flask, render_template, request, json, session, jsonify, flash, redirect, url_for
from flask.helpers import url_for
from requests import Request, Session
import requests
from werkzeug.utils import redirect
from werkzeug.wrappers import response
import jinja2
from jinja2 import filters


app = Flask(__name__)
app.secret_key = 'key'

############### CRYPTO EXTERNAL API ######################

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

parameters = {
    'slug':
    "bitcoin,ethereum,solana,xrp,cardano,avalanche,polkadot,dogecoin,polygon,litecoin,chainlink,tron,stellar,cosmos",
    'convert': 'USD'
}

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY':
    'af2460d3-d55c-4349-8e18-eb2844eb0058'  # napravila poseban acc na coinmarketcap za drs
}

session = Session()
session.headers.update(headers)

#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)
##########################################################


@app.route('/')
def home():
    response = session.get(url, params=parameters)
    user = getattr(session, "user")
    return render_template("home.html",
                           response=json.loads(response.text)['data'], user = user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    #mozemo mozda da ubacimo proveru da li vec posotiji neko u sesiji
    if request.method == 'GET':
        return render_template("login.html", user = getattr(session, "user"))
    else:
        _email = request.form['email']
        _password = request.form['password']

        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({'email': _email, 'password': _password})
        req = requests.post("http://127.0.0.1:5001/login",
                            data=body,
                            headers=header)

        response = (req.json())

        _message = response['message']
        _code = req.status_code
        if (_code == 200):
            setattr(session, "user", _email)
            response = session.get(url, params=parameters)
            return render_template("home.html",
                           response=json.loads(response.text)['data'], user = user, message = "You have logged in.")
        else:
            return render_template("login.html", message=_message, user = getattr(session, "user"))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html', user = getattr(session, "user"))
    else:
        _firstName = request.form['firstName']
        _lastName = request.form['lastName']
        _address = request.form['address']
        _city = request.form['city']
        _country = request.form['country']
        _phoneNumber = request.form['number']
        _email = request.form['email']
        _password = request.form['password']
        _cardNumber = 0
        _cardExpDate = '0'
        _cardCode = 0
        _amount = -1

        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({
            'name': _firstName,
            'lastName': _lastName,
            'address': _address,
            'city': _city,
            'country': _country,
            'phoneNumber': _phoneNumber,
            'email': _email,
            'password': _password,
            'cardNumber': _cardNumber,
            'cardExpDate': _cardExpDate,
            'cardCode': _cardCode,
            'amount': _amount
        })
        req = requests.post("http://127.0.0.1:5001/sign_up",
                            data=body,
                            headers=header)
        #req = requests.post("http://0.0.0.0:5001/sign_up", data = body, headers = header)

        response = (req.json())
        _message = response['message']
        _code = req.status_code
        if (_code == 200):
            setattr(session, "user", _email)
            setattr(app, "user", _email)
            #session["user_email"] = _email
            return redirect(url_for("verify"))
        return render_template('sign_up.html', message=_message, user = getattr(session, "user"))


@app.route('/logout')
def logout():
    setattr(session, "user", None)
    response = session.get(url, params=parameters)
    user = None
    return render_template("home.html",
                           response=json.loads(response.text)['data'], user = user, message = "You have logged out.")

@app.route('/user', methods=['GET'])
def user():
    #_email = session.get("user_email")
    #session["user"] = "nesto"
    _email = getattr(session, "user")
    if _email == None:
        return "<p>User not logged in.</p>"
    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    req = requests.get("http://127.0.0.1:5001/user?email={}".format(_email),                           
                        headers=header)
    response = json.loads(jsonify(req.text).json)

    name = response['name']
    lastName = response['lastName']
    address = response['address']
    city = response['city']
    country = response['country']
    phoneNumber = response['phoneNumber']
    email = response['email']
    password = response['password']
    cardNumber = response['cardNumber']
    cardExpDate = response['cardExpDate']
    cardCode = response['cardCode']
    amount = response['amount']

    user_data = {
        'name': name,
        'lastName': lastName,
        'address': address,
        'city': city,
        'country': country,
        'phoneNumber': phoneNumber,
        'email': email,
        'password': password,
        'cardNumber': cardNumber,
        'cardExpDate': cardExpDate,
        'cardCode': cardCode,
        'amount': amount
    }

    _code = req.status_code
    if (_code == 200):
        setattr(session, "user_data", user_data)
        if cardNumber != '0':
            verified = True
        else:
            verified = False
        setattr(session, 'verified', verified)
        #return redirect(url_for("user"), user_data = user_data)
        return render_template("user.html", user_data = user_data, boolean = verified, user = getattr(session, "user"))
    return render_template('login.html', user = getattr(session, "user"))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    temp = getattr(session, "user")
    if temp != None:
        if request.method == 'GET':
            return render_template('verify.html', user = getattr(session, "user"))
        else:
            _cardNum = request.form['cardNum']
            _name = request.form['name']
            _expDate = request.form['expDate']
            _cardCode = request.form['cardCode']
            _amount = request.form['amount']
            mejl = getattr(session, "user")
            #mejl = session["user"]
            #mejl = str(session.get('user'))

            header = {
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            }
            body = json.dumps({
                'cardNum': _cardNum,
                'name': _name,
                'expDate': _expDate,
                'cardCode': _cardCode,
                "email": mejl,
                'amount': _amount
            })
            req = requests.post("http://127.0.0.1:5001/verify",
                                data=body,
                                headers=header)

            response = (req.json())
            _message = response['message']
            _code = req.status_code
            if (_code == 200):
                setattr(session, 'verified', True)
                return redirect(url_for("home"))
            else:
                return render_template("verify.html", message = _message, user = getattr(session, "user"))
    else:
        return redirect(url_for("login"))


@app.route('/trade', methods=['GET', 'POST'])
def trade():
    if request.method == "GET":
        response = session.get(url, params=parameters)
        return render_template("trade.html", response=json.loads(response.text)['data'], user = getattr(session, "user"))

@app.route('/buyKripto', methods=['GET', 'POST'])
def kupi():
    #napravi da se skida nova i sve to cu sutra
    _nazivKripta = request.args.get('nazivKripta')
    _kolikoKripta = request.args.get('kolikoKripta')
    _ulozeno = request.args.get('ulozeno')
    _valutaPlacanja = request.args.get('valutaPlacanja')
    _mejl = getattr(session, "user")

    header = {
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }   
    body = json.dumps({
        'nazivKripta' : _nazivKripta,
        'kolikoKripta' : _kolikoKripta,
        'ulozeno' : _ulozeno,
        'valutaPlacanja' : _valutaPlacanja,
        'mejl' : _mejl
    })

    req = requests.post("http://127.0.0.1:5001/buyKripto", data=body, headers=header)
    response = (req.json())
    _message = response['message']
    _code = req.status_code
    
    if _code == 200:
        return redirect(url_for("home"))
    else:
        return render_template("verify.html", message = _message)


@app.route('/editUser', methods=['GET', 'POST'])
def editUser():
    if request.method == 'GET':
        user_data = getattr(session, "user_data")
        return render_template("editUser.html", user_data=user_data)
    else:
        #logika za cuvanje podataka u bazi
        user_data = getattr(session, "user_data")
        _email = getattr(session, "user")
        _firstName = request.form['name']
        _lastName = request.form['lastName']
        _address = request.form['address']
        _city = request.form['city']
        _country = request.form['country']
        _phoneNumber = request.form['phoneNumber']
        _oldPassword = request.form['oldPassword']
        _newPassword1 = request.form['newPassword1']
        _newPassword2 = request.form['newPassword2']

        if _newPassword1 != "" and _newPassword1 != '':
            if user_data['password'] != _oldPassword:
                _message = "Check your old password again."
                render_template('sign_up.html', message=_message, user = getattr(session, "user"))

            if _newPassword1 != _newPassword2:
                _message = "Passwords don't match."
                render_template('sign_up.html', message=_message, user = getattr(session, "user"))

        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({
            'name': _firstName,
            'lastName': _lastName,
            'address': _address,
            'city': _city,
            'country': _country,
            'phoneNumber': _phoneNumber,
            'email': _email,
            'password': _newPassword1
        })
        req = requests.post("http://127.0.0.1:5001/editUser",
                            data=body,
                            headers=header)

        response = (req.json())
        _message = response['message']
        _code = req.status_code
        if (_code == 200):
            return redirect(url_for("user"))
        return redirect(url_for("editUser"), message = _message)

@app.route('/wallet')
def wallet():
    _email = getattr(session, "user")
    if _email == None:
        return "<p>User not logged in.</p>"

    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    req = requests.get("http://127.0.0.1:5001/wallet?email={}".format(_email),                           
                        headers=header)
    response = json.loads(jsonify(req.text).json)

    _code = req.status_code
    if (_code == 200):
        setattr(session, "wallet_data", response)
        return render_template("wallet.html", response = response, user = getattr(session, "user"))
    return render_template('user.html', user = getattr(session, "user"))

@app.route('/addMoney', methods=['POST'])
def addMoney():
    addedMoney = request.form['addedMoney']
    email = getattr(session, 'user')
    if addedMoney != '' and addedMoney != "" and addedMoney != 0:
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({
            'email': email,
            'addedMoney': addedMoney
        })
        req = requests.post("http://127.0.0.1:5001/addMoney",
                            data=body,
                            headers=header)
        response = json.loads(jsonify(req.text).json)

        _message = response['message']
        _code = req.status_code
        if (_code == 200):
            return redirect(url_for("user"))
        return redirect(url_for("user"), message = _message)
    else:
        _message = "Wrong input"

    return redirect(url_for(user))

@app.route('/convertUSDToTether', methods=['POST'])
def convertUSDToTether():
    email = getattr(session, 'user')
    usdAmount = request.form['usdToTetherAmount']

    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({
        'email': email,
        'usdAmount': usdAmount
    })
    req = requests.post("http://127.0.0.1:5001/convertUSDToTether",
                        data=body,
                        headers=header)
    
    response = (req.json())
    #response = json.loads(jsonify(req.text).json)

    _message = response['message']
    _code = req.status_code
    if (_code == 200):
        return redirect(url_for("user"))
    return redirect(url_for("user"), message = _message)

if __name__ == "__main__":
    setattr(session, "user", None)
    app.run(port=5000)