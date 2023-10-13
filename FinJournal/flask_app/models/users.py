from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_app.models import entries
import requests
import re
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


class User:
    db = "FinJournal" #which database are you using for this project
    def __init__(self, data):
        self.id = data['id']
        self.fname= data['fname']
        self.lname = data['lname']
        self.user_name = data['user_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.balance = data['balance']
        self.entries = []
        # What changes need to be made above for this project?
        #What needs to be added her for class association?


    @classmethod
    def create_user(cls , data):
        if not cls.validate_user(data):
            return False
        data = cls.parsed_data(data)
        query = """
        INSERT INTO user (fname, lname, user_name, email, password, balance)
        VALUES( %(fname)s, %(lname)s, %(user_name)s, %(email)s, %(password)s, %(balance)s )
        ;"""
        user_id = connectToMySQL(cls.db).query_db(query,data)
        session['user_id'] = user_id
        return user_id

    @classmethod
    def get_user_by_email(cls , email):
        data = {'email': email}
        query = """
        SELECT *
        FROM user
        WHERE email = %(email)s
        ;"""
        user_id = connectToMySQL(cls.db).query_db(query, data)
        if user_id:
            return cls(user_id[0])
        return False


    @classmethod
    def get_user_by_id(cls , id):
        data = {'id': id}
        query = """
        SELECT *
        FROM user
        WHERE id = %(id)s
        ;"""
        user_id = connectToMySQL(cls.db).query_db(query, data)
        if user_id:
            return cls(user_id[0])
        return False

    @classmethod
    def get_user_with_entries(cls, id):
        query = """
        SELECT *
        FROM entry
        JOIN user
        ON entry.user_id = user.id
        """
        result = connectToMySQL(cls.db).query_db(query)
        total = 0
        for row in result:
            total = total + int(row['amount'])
        this_user = cls.get_user_by_id(id)
        this_user.balance = this_user.balance - total
        return this_user

    @classmethod
    def add_to_balance(cls, amount):
        this_user = cls.get_user_by_id(session['user_id'])
        this_user.balance = this_user.balance + int(amount)
        print(this_user.balance)
        balance = {
            "balance" : this_user.balance
        }
        print(balance)
        query= """
        UPDATE user
        SET balance = %(balance)s
        """
        result = connectToMySQL(cls.db).query_db(query, balance)
        return this_user

    @classmethod
    def get_api(cls):
        url = "https://dad-jokes.p.rapidapi.com/random/joke"

        headers = {
            "X-RapidAPI-Key": "f2566eb36bmshd3682e87f5e2ec9p18e814jsn1b97d49709d7",
            "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        this= response.json()
        setup = this['body'][0]['setup']
        punchline = this['body'][0]['punchline']
        joke = {
            'setup' : setup,
            'punchline' : punchline
        }

        return joke




    @staticmethod
    def parsed_data(data):
        parsed_entry = {
            "fname" : data['fname'],
            "lname" : data['lname'],
            "user_name" : data['user_name'],
            "email" : data['email'],
            "password": bcrypt.generate_password_hash(data['password']),
            "balance" : data['balance']
        }
        return parsed_entry



    #Validation for creating a user.
    @staticmethod
    def validate_user(data):
        is_valid = True
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(data['fname']) < 2:
            flash("First name needs to be longer than 2 characters")
            is_valid = False
        if len(data['lname'])< 2:
            flash("Last name needs to be longer than 2 characters")
            is_valid = False
        if len(data['user_name']) < 2:
            flash('User name needs to be atleast 2 characters')
            is_valid= False
        if len(data['balance'])< 1:
            flash("Please enter a Opening Balance, if none put 0")
            is_valid= False
        if 'id' not in data:
            if len(data['password'])<8:
                flash("Passwords needs to be longer than 2 characters")
                is_valid= False
            if  "!" not in data['password']:
                flash("Password must contain either a '!' or '?' or '.' " )
                is_valid = False
                if '?' not in data['password']:
                    flash("Password must contain either a '!' or '?' or '.' " )
                    is_valid = False
                    if '.' not in data['password']:
                        flash("Password must contain either a '!' or '?' or '.' " )
                        is_valid = False
            if data['password'] != data['confirm_password']:
                flash("Passwords do not match")
                is_valid= False
        if 'id' not in data or data['email'] != User.get_user_by_id(data['id']).email:
            if not EMAIL_REGEX.match(data['email']):
                flash("email address format incomplete")
                is_valid= False
            if User.get_user_by_email(data['email']):
                flash('Email Address is already Taken')
                is_valid= False
        return is_valid


#Validation for loging in a user
    @staticmethod
    def login(data):
        this_user = User.get_user_by_email(data['email'])
        if this_user:
            if bcrypt.check_password_hash(this_user.password, data['password']):
                session['user_id'] = this_user.id
                session['fname'] = this_user.fname
                return True
        flash("Email or Password is Incorrect")
        return False
