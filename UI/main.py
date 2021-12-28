from flask import Flask, render_template, request, json, session, jsonify, flash
from requests import Request, Session

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


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/logout')
def logout():
    return "<p>logout</p>"  #Napraviti da logout stranica bude Home ali sa porukom da je uspesno izlogovan, izbaci korisnika iz sesije


@app.route('/user')
def user():
    return render_template('user.html')


app.run(port=5000)