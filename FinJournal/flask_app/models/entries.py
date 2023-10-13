from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_app.models import users

class Entry:
    db = "FinJournal" #which database are you using for this project
    def __init__(self, data):
        self.id = data['id']
        self.amount = data['amount']
        self.catagory = data['catagory']
        self.note = data['note']
        self.merchant = data['merchant']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.entryowner = ''

    @classmethod
    def add_expense(cls, data):
        if not cls.validate_entry(data):
            return False
        data = cls.parssed_data(data)
        query = """
        INSERT INTO entry ( amount, catagory, note, merchant, user_id)
        VALUES( %(amount)s, %(catagory)s, %(note)s, %(merchant)s, %(user_id)s)
        ;"""
        entry_id = connectToMySQL(cls.db).query_db(query,data)
        this_user = users.User.get_user_by_id(data['user_id'])
        this_user.balance = this_user.balance - int(data['amount'])
        return entry_id and this_user.balance

    @classmethod
    def delete_expense(cls,id):
        data = {'id': id}
        query = """
        DELETE FROM entry
        WHERE id = %(id)s
        ;"""
        result = connectToMySQL(cls.db).query_db(query,data)
        return

    @classmethod
    def get_entries_by_user_id(cls):
        query = """
        SELECT *
        FROM entry
        JOIN user
        ON entry.user_id = user.id
        ;"""
        result = connectToMySQL(cls.db).query_db(query)
        all_entries = []
        for row in result:
            one_entry = cls(row)
            one_entry_owner = {
                'id' :row['user_id'],
                'fname' : row['fname'],
                'lname' : row['lname'],
                'email' : row['email'],
                'password':row['password'],
                'created_at':row['created_at'],
                'updated_at':row['updated_at'],
                'user_name' : row['user_name'],
                'balance' : row['balance']
            }
            entryowner = users.User(one_entry_owner)
            one_entry.entryowner = entryowner
            all_entries.append(one_entry)
        return all_entries

    @staticmethod
    def parssed_data(data):
        parsed_entry = {
            "amount": data['amount'],
            'catagory': data['catagory'],
            'note' : data['note'],
            'merchant' : data['merchant'],
            "user_id" : data['user_id']
        }
        return parsed_entry

    @staticmethod
    def validate_entry(data):
        is_valid = True
        if len(data['amount']) < 1:
            flash("Please Enter an Amount over $1")
            is_valid = False
        if len(data['catagory']) == '':
            flash("Please select a catagory")
            is_valid = False
        if len(data['merchant']) == '':
            flash("Enter a Valid Merchant")
            is_valid = False
        return is_valid
