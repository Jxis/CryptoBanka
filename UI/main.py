from flask import Flask, render_template, request, json, session, jsonify, flash

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


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