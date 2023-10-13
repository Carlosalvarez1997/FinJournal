from flask_app import app
from flask import redirect, render_template, session,request
from flask_app.models import users, entries




@app.route('/')
def register_user():
    return render_template('register.html')

@app.route('/user/register', methods = ["post"])
def create_user():
    if users.User.create_user(request.form):
        return redirect('/home')
    else:
        return render_template('register.html')

@app.route('/user/login', methods = ['post'])
def login_user():
    if users.User.login(request.form):
        return redirect('/home')
    return redirect('/')

@app.route('/add/entry')
def add_entry():
    return render_template('add_entry.html')

@app.route('/entry', methods = ['post'])
def entry():
    if entries.Entry.add_expense(request.form):
        return redirect('/home')
    else:
        return render_template('add_entry.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        these_entries = entries.Entry.get_entries_by_user_id()
        this_user = users.User.get_user_by_id(session['user_id'])
        one_user = users.User.get_user_with_entries(session['user_id'])
        this = users.User.get_api()
        return render_template('home.html', these_entries = these_entries , this_user= this_user, one_user = one_user, this = this)
    else:
        return redirect('/')

@app.route('/add/balance', methods = ['Get', 'Post'])
def add():
    if request.method == "GET":
        return render_template('add_balance.html')
    if request.method == "POST":
        print(request.form['amount'])
        users.User.add_to_balance(request.form['amount'])
        return redirect('/home')

@app.route('/delete/<id>')
def delete_entry(id):
    this_entry = entries.Entry.delete_expense(id)
    return redirect('/home')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
