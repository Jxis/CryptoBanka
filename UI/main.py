from flask import Flask, render_template, request, json, session, jsonify, flash
from requests import Request, Session
import requests

app = Flask(__name__)

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
    return render_template("home.html",
                           response=json.loads(response.text)['data'])


@app.route('/login')
def login():
    return render_template("login.html")


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

        header = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
        body = json.dumps({'name' : _firstName, 'lastName' : _lastName, 'address' : _address, 'city' : _city, 'country' : _country, 'phoneNumber' : _phoneNumber, 'email' : _email, 'password' : _password, 'cardNumber' : _cardNumber, 'cardExpDate' : _cardExpDate, 'cardCode' : _cardCode})
        req = requests.post("http://127.0.0.1:5001/sign_up", data = body, headers = header)
        #req = requests.post("http://0.0.0.0:5001/sign_up", data = body, headers = header)

        response = (req.json())
        _message = response['message']
        _code = req.status_code
        if(_code == 200):
            return "<p>USPELO</p>"  #ovde mozda prebaciti na to da unese podatke za karticu
        return render_template('sign_up.html', message = _message)


@app.route('/logout')
def logout():
    return "<p>logout</p>"  #Napraviti da logout stranica bude Home ali sa porukom da je uspesno izlogovan, izbaci korisnika iz sesije


@app.route('/user')
def user():
    return render_template('user.html')

if __name__ == "__main__":
    app.run(port=5000)