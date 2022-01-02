from types import MethodType
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>logout</p>"
    return "<p>logout</p>" #Napraviti da logout stranica bude Home ali sa porukom da je uspesno izlogovan


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        #Dodati da pokupi vrednosti iz svih polja i kreira User-a

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.',
                  category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            flash('Account created!', category='success')
    return render_template("sign_up.html")


@auth.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        card_date = request.form.get('card_date')
        card_password = request.form.get('card_password')
        card_state = request.form.get('card_state')
        
        #skinuti init money sa kartice
        #upis podataka u trenutnog korisnika i onda u bazu

        #boolean podesiti da li je uneta kartica ili ne
    return render_template("user.html",
                           boolean=False, user=current_user)  #ovako se prosledjuju varijable