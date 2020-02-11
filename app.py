from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'you-will-never-guess'
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.String(8),  primary_key=True)
    pin_hash = db.Column(db.String(128))
    amount=db.Column(db.Integer)

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

@login.user_loader
def load_user(card_number):
    return User.query.get(card_number)

class ATM(db.Model):
    atm_id=db.Column(db.Integer,primary_key=True)
    two_thousand = db.Column(db.Integer)
    two_hundred = db.Column(db.Integer)
    one_hundred = db.Column(db.Integer)
    five_hundred = db.Column(db.Integer)



atm = ATM(0,10,10,10,10)
db.session.add(atm)
ab.session.commit()
@app.route('/api/login', methods=['POST'])
def login():
    card_number = request.json.get("card")
    pin = request.json.get("pin") 
    user = User.query.filter_by(id=card_number).first()
    if user is None or not user.check_pin(pin):
        abort(400)
    login_user(user)
    return jsonify({'data': 'Welcome to ATM'})

@app.route('/api/logout')
def logout():
    logout_user()
    return jsonify({'data': 'Bye!'})


@app.route('/api/register', methods=['POST'])
def register():
    card_number = request.json.get("card")
    pin = request.json.get("pin")
    if card_number is None or pin is None:
        abort(400)
    if User.query.filter_by(id=card_number).first() is not None:
        abort(400)
    user=User(id=card_number)
    user.set_pin(pin)
    user.amount=0
    db.session.add(user)
    db.session.commit()
    return (jsonify({'card_number': user.id}))



@app.route('/api/add_money', methods=['POST'])
def add_money():
    if current_user.is_authenticated:
        two_thousand = int (request.json.get("two_thousand"))
        two_hundred = int (request.json.get("two_hundred"))
        one_hundred = int (request.json.get("one_hundred"))
        five_hundred = int (request.json.get("five_hundred"))
        atm.two_hundred += two_hundred
        atm.one_hundred += one_hundred
        atm.five_hundred += five_hundred
        atm.two_thousand += two_thousand
        current_user.amount += ((100*one_hundred)+(200*two_hundred)+(2000*two_thousand)+(500*five_hundred))
        db.session.commit()
        logout_user()
        return (jsonify({'data':'Money Deposited Successfully'}))    
    abort(400)

@app.route('/api/withdraw',methods=['POST'])
def withdraw():
    if current_user.is_authenticated:
        amt= int (request.json.get("amount"))
        ori_amt=amt
        if amt>20000:
            abort(400)
        if amt>current_user.amount:
            abort(400)
        amount_in_atm=((100*atm.one_hundred)+(200*atm.two_hundred)+(2000*atm.two_thousand)+(500*atm.five_hundred))
        if amt>amount_in_atm:
            abort(400)
        two_thousand = int(amt/2000)
        if two_thousand>atm.two_thousand:
            two_thousand=atm.two_thousand
        amt=amt-(2000*two_thousand)

        five_hundred = int(amt/500)
        if five_hundred>atm.five_hundred:
            five_hundred=atm.five_hundred
        amt=amt-(500*five_hundred)
        
        two_hundred = int(amt/200)
        if two_hundred>atm.two_hundred:
            two_hundred=atm.two_hundred
        amt=amt-(200*two_hundred)

        one_hundred = int(amt/100)
        if one_hundred>atm.one_hundred:
            one_hundred=atm.one_hundred
        amt=amt-(100*one_hundred)

        current_user.amount -= ori_amt
        atm.two_hundred -= two_hundred
        atm.one_hundred -= one_hundred
        atm.five_hundred -= five_hundred
        atm.two_thousand -= two_thousand
        db.session.commit()
        logout_user()
        return jsonify({'one_hunded':one_hundred,'two_hundred':two_hundred,'two_thousand':two_thousand,'five_hundred':five_hundred})
    abort(400)

