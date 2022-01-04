from flask import Flask, render_template, request, json, session, jsonify, flash, redirect, url_for
from flask.helpers import url_for
from requests import Request, Session
import requests
from werkzeug.utils import redirect

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
##########################################################


@app.route('/')
def home():
    response = session.get(url, params=parameters)
    setattr(session, "user", None)  #*****
    return render_template("home.html",
                           response=json.loads(response.text)['data'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    #mozemo mozda da ubacimo proveru da li vec posotiji neko u sesiji
    if request.method == 'GET':
        return render_template("login.html")
    else:
        _email = request.form['email']
        _password = request.form['password']

        header = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
        body = json.dumps({'email' : _email, 'password' : _password})
        req = requests.post("http://127.0.0.1:5001/login", data = body, headers = header)

        response = (req.json())

        _message = response['message']  
        _code = req.status_code
        if(_code == 200):
            #znaci da je sve okej, da postoji korisnik sa datim emailom i lozinkom i ovde cemo da ga stavimo
            # u sesiju i da vratimo stranicu recimo home
            #session["usr"] = request.form['email'] #ovo iz nekog razloga ne radi
            setattr(session, "user", _email)
            return redirect(url_for("home"))
        else:
            # Vratimo login, sa ispisom wrong email or password
            return render_template("login.html", message = _message)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
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


        header = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
        body = json.dumps({'name' : _firstName, 'lastName' : _lastName, 'address' : _address, 'city' : _city, 'country' : _country, 'phoneNumber' : _phoneNumber, 'email' : _email, 'password' : _password, 'cardNumber' : _cardNumber, 'cardExpDate' : _cardExpDate, 'cardCode' : _cardCode, 'amount' : _amount})
        req = requests.post("http://127.0.0.1:5001/sign_up", data = body, headers = header)
        #req = requests.post("http://0.0.0.0:5001/sign_up", data = body, headers = header)

        response = (req.json())
        _message = response['message']
        _code = req.status_code
        if(_code == 200):
            setattr(session, "user", _email)
            return redirect(url_for("verify"))
        return render_template('sign_up.html', message = _message)


@app.route('/logout')
def logout():
    setattr(session, "user", None)
    return "<p>logout</p>"  #Napraviti da logout stranica bude Home ali sa porukom da je uspesno izlogovan, izbaci korisnika iz sesije


@app.route('/user')
def user():
    return render_template('user.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    temp = getattr(session, "user")
    if temp != None:
        if request.method == 'GET':        
            return render_template('verify.html')
        else:
            _cardNum = request.form['cardNum']
            _name = request.form['name']
            _expDate = request.form['expDate']
            _cardCode = request.form['cardCode']
            _amount = request.form['amount']
            mejl = getattr(session, "user")
            #mejl = session["user"]
            #mejl = str(session.get('user'))

            header = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
            body = json.dumps({'cardNum' : _cardNum, 'name' : _name, 'expDate' : _expDate, 'cardCode' : _cardCode, "email" : mejl, 'amount' : _amount})
            req = requests.post("http://127.0.0.1:5001/verify", data = body, headers = header)

            response = (req.json())
            _message = response['message']
            _code = req.status_code
            if(_code == 200):
                return redirect(url_for("home"))
            else:
                return "GRESKA PRI VERIFIKACIJI"
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(port=5000)