from flask import *
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import json
app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"
app.config["MONGO_URI"] = "mongodb+srv://swaminathan:1234@cluster0.pzfmyxg.mongodb.net/Expensetracker?retryWrites=true&w=majority"
mongo = PyMongo(app)
users = mongo.db.users
expenses = mongo.db.expenses
amtentered = False
amount = None
balance = None
updated = False
datetoday = None
def check():
    datetoday =str(datetime.today().date())
    try:
        l = users.find({},{datetoday:1})
        return True
    except:
        return False
@app.route("/")
def home():
    global amtentered,amount,updated,balance,datetoday
    datetoday = str(datetime.today().date())
    Users = list(users.find())
    disabled = False
    updated = check()
    if(not updated):
        users.update_many({},{"$set":{datetoday:{}}})
        updated = True
    try:
        amount = list(expenses.find({"date":datetoday}))[0]["amount"]
        balance = list(expenses.find({"date":datetoday}))[0]["balance"]
        print(balance)
        disabled = True
    except:
        pass
    if(amtentered):
        flash("Amount updated successfully")
        amtentered = False
    return render_template("home.html",Users = Users,balance = balance,disabled = disabled)
@app.route("/enteramounttoday",methods = ["GET","POST"])
def enterbalancetoday():
    global amtentered,balance
    datetime_now = datetime.today()
    current_date = str(datetime_now.date())
    dates = list(expenses.find({"date":str(current_date)}))
    if(dates == []):
        expenses.insert_one({"date":str(current_date)})
    dates = list(expenses.find({"date":str(current_date)}))
    if(request.method == "POST"):
        amt = request.form.get("amt")
        amt = int(amt)
        balance = amt
        expenses.update_one({"date":str(current_date)},{"$set":{"amount":amt,"balance":balance}})
        amtentered = True
        return redirect(url_for("home"))
    return render_template("enteramount.html",date = current_date)
@app.route("/<id>",methods = ["GET","POST"])
def enterexpense(id):
    global balance,updated
    datetoday = str(datetime.today().date())
    user = users.find_one({"_id":ObjectId(id)})
    balance = list(expenses.find({"date":datetoday}))[0]["balance"]
    try:
        amount = list(expenses.find({"date":datetoday}))[0]["amount"]
    except:
        amount =  None
    name = user["Name"]
    if(amount == None):
        return render_template("enteramtfortoday.html")
    expense,amt = None,None
    if(request.method == "POST"):
        expense = request.form.get("expense")
        try:
            amt = int(request.form.get("amt"))
        except:
            flash("Enter a valid amount")
        if(amt > balance):
            flash("Enter a valid amount")
            return redirect(f"/{id}")
        if(amt != None):
            balance-=amt
            try:
                user[datetoday][expense] = amt
                print(user[datetoday])
                users.update_one({"_id":ObjectId(id)},{"$set":{datetoday:user[datetoday]}})
            except:
                users.update_one({"_id":ObjectId(id)},{"$set":{datetoday:{expense:amt}}})
            updated = True
            expenses.update_one({"date":datetoday},{"$set":{"balance":balance}})
            return redirect(url_for("home"))
    return render_template("expense.html",name=name)
@app.route("/seetodaysexpenses")
def todaysexpenses():
    datetoday = str(datetime.today().date())
    expensestoday = list(users.find({},{"Name":1,datetoday:1}))
    try:
        balance = list(expenses.find({"date":str(datetime.today().date())}))[0]["balance"]
    except:
        balance = None
    return render_template("todaysexpense.html",expensestoday = expensestoday,datetoday=datetoday,balance = balance)
@app.route("/seeallexpenses")
def allexpenses():
    expensesbyusers = list(users.find())
    dates = list(expenses.find({},{"date":1}))
    return render_template("seeallexpenses.html",expensesbyusers=expensesbyusers,dates = dates)
@app.route("/onthatday/<date>")
def onthatday(date):
    if date == str(datetime.today().date()):
        return redirect(url_for("todaysexpenses"))
    expensesonthatday = list(users.find({},{"Name":1,date:1}))
    try:
        balance = list(expenses.find({"date":date}))[0]["balance"]
    except:
        balance = None
    return render_template("seedaysexpenses.html",expensesonthatday = expensesonthatday,date = date,balance=balance)
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
