from flask import Flask, url_for, render_template, session, redirect, request 
import pickle
from flask import Flask,render_template, request
from flask_mysqldb import MySQL
from itertools import islice
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler


app = Flask(__name__)

# Unloading Model with FIREBASE
with open('MainModel.pkl', 'rb') as file:
    model = pickle.load(file)

with open('MainScaler.pkl', 'rb') as file:
    scaler = pickle.load(file)



                                                    # DATABASE

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(r"C:\Users\jasly\OneDrive\Documents\College\6TH SEMESTER\Project\WCPM\waterconsumptionprediction-firebase-adminsdk-uq110-7bc5a33f9a.json")
firebase_admin.initialize_app(cred, {
    "databaseURL":"https://waterconsumptionprediction-default-rtdb.firebaseio.com"
})

@app.route('/enterdataoutput', methods = ['POST', 'GET'])
def insert():
    if request.method == 'GET':
        return "Login via the login Form"
    if request.method == 'POST':
        bdate = request.form['entrydate']
        blockname = request.form['bname']
        unitsconsumed = request.form['unitsconsumed']
        totalbill = request.form['consumptioncost']
        ref = db.reference('/WaterBillData')
        ref.push({
            "BillDate":bdate,
            "BlockName":blockname,
            "UnitsConsumed":unitsconsumed,
            "TotalBill":totalbill
        })
        return render_template("enterdataoutput.html")

@app.route('/viewdataoutput', methods = ['POST', 'GET'])
def view():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        mainlist = []
        datalist=[]
        blockname = request.form['bname']
        yearop = request.form['year']
        ref = db.reference('/WaterBillData')
        data = ref.get()
        for record in data:
            new_string = "WaterBillData" + "/" + record  
            new_ref = db.reference(new_string)
            individual_data=new_ref.get()
            dictbname = individual_data.get('BlockName')
            recdate = individual_data.get('BillDate')
            recyear = ""
            for i in range(len(recdate) - 3):
                num = True
                for j in range(4):
                    num = num & recdate[i + j].isdigit()
                if num :
                    recyear = ""
                    for j in range(4):
                        recyear += recdate[i + j]  
            if ((dictbname == blockname) & (recyear == yearop)):
                billdate = individual_data.get('BillDate')
                totalbill = individual_data.get('TotalBill')
                unitsconsumed = individual_data.get('UnitsConsumed')
                datalist.append(billdate)
                datalist.append(dictbname)
                datalist.append(totalbill)
                datalist.append(unitsconsumed)
                mainlist.append(datalist)
                datalist=[]
        return render_template("viewdataoutput.html", data = mainlist, yearchoice=yearop)

@app.route('/updatedataoutput', methods = ['POST', 'GET'])
def update():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        olddate = request.form['olddate'] 
        oldblockname = request.form['oldbname']
        ref = db.reference('/WaterBillData')
        data = ref.get()
        for record in data:
            new_string = "WaterBillData" + "/" + record  
            new_ref = db.reference(new_string)
            individual_data=new_ref.get()
            refbname = individual_data.get('BlockName')
            refbdate = individual_data.get('BillDate')
            if ((refbname == oldblockname) & (refbdate == olddate)):
                ndate = request.form['newdate']
                blockname = request.form['bname']
                unitsconsumed = request.form['unitsconsumed']
                totalbill = request.form['consumptioncost']
                ref.update({
                    record :{
                        "BillDate":ndate,
                        "BlockName":blockname,
                        "UnitsConsumed":unitsconsumed,
                        "TotalBill":totalbill
                    }
                })
        return render_template("updatedataoutput.html")
                                                    # LOGIN / LOGOUT


@app.route("/", methods=['POST','GET'])
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))


                                                    # HOME



@app.route("/home")           
def home():
    return render_template("index.html")



                                                    # ABOUT

    
@app.route("/about")      
def aboutindex():
    return render_template("mainaboutpage.html")

@app.route("/aboutcollege")      
def aboutaloy():
    return render_template("aboutaloy.html")

@app.route("/aboutproject")      
def aboutmodel():
    return render_template("aboutmodel.html")


                                                    # TREND DEPICTIONS


@app.route("/trenddepict")      
def trendepict():
    return render_template("maintrendpage.html")

@app.route("/yearlydepict")      
def yeartrend():
    return render_template("yearlydepict.html")

@app.route("/monthlydepict")      
def monthtrend():
    return render_template("monthlydepict.html")


                                                    # DATA SET MANAGEMENT


@app.route("/dataindex")      
def dataindex():
    return render_template("maindatapage.html")

@app.route("/enterdata")      
def enterdata():
    return render_template("enterdata.html")

@app.route("/updatedata")      
def updatedata():
    return render_template("updatedata.html")

@app.route("/viewdata")      
def viewdata():
    return render_template("viewdata.html")


                                                    # PREDICTIONS

""" WORKING WITH FIREBASE DB """

def formulacal(predictions):
     admin_consumption=predictions['Admin']
     arrupe_consumption=predictions['Arrupe']
     xavier_consumption=predictions['Xavier']
     lcri_consumption=predictions['LCRI']
     LIST=[admin_consumption,arrupe_consumption,xavier_consumption,lcri_consumption]
     result=[]
     for num in LIST:
         TotalBill = (num/1000) * 44
         result.append(int(TotalBill))
     return result


@app.route('/predict',methods=['GET'])
def predictdisplay():
    return render_template('mainpredictionpage.html')

def predict_consumption(date):
    # Create a DataFrame with the input date and the four blocks
    blocks = ['Admin', 'Arrupe', 'Xavier', 'LCRI']
    data = {'Date': [date]*4, 'BlockName': blocks}
    df = pd.DataFrame(data)

    # Preprocess the input data
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month.astype('Int64')
    df['Year'] = df['Date'].dt.year.astype('Int64')

    # Load the OneHotEncoder used during training
    with open('MainEncoder.pkl', 'rb') as file:
        ohe = pickle.load(file)

    transformed = ohe.transform(df[['BlockName']])
    df[ohe.categories_[0]] = transformed.toarray()

    df = df.drop(columns=['BlockName', 'Date'])
    df = pd.DataFrame(scaler.transform(df), columns=df.columns)

    # Generate predictions for each block
    predictions = model.predict(df)
    predictions = [int(p) for p in predictions]

    # Combine the predictions with the block names
    result = dict(zip(blocks, predictions))
    return result

global_consumption_list = []
global_cost_list = []
global_date_list = []
global_people_list = []
@app.route('/predictresult',methods=['POST'])
def predict():
    # Get user input date from form
    date = request.form['date']
    numpeople = request.form['numpeople']
    predictions = predict_consumption(date)
    # admin arrupe xavier lcri
    global global_consumption_list
    global global_cost_list
    global global_date_list
    global global_people_list
    if (len(global_consumption_list) == 1):
        global_consumption_list = []
    if (len(global_cost_list) == 1):
        global_cost_list = []
    if (len(global_date_list) == 1):
        global_date_list = []
    if (len(global_people_list) == 1):
        global_people_list = []
    billamt=formulacal(predictions)
    billsum=sum(billamt)
    sum_of_predictions=sum(predictions.values())
    global_consumption_list.append(sum_of_predictions)
    global_cost_list.append(billsum)
    global_date_list.append(date)
    if (numpeople):  
        global_people_list.append(int(numpeople))
    else:
        global_people_list.append(6441)
    return render_template('predictionresult.html', date=date, prediction_text=predictions, sumval=sum_of_predictions, billamt=billamt, billsum=billsum)

@app.route('/predictpdf')
def predictpdf():
    current_data = []
    new_pred_list = []
    from datetime import date, datetime, timedelta
    today = date.today()
    pred_date = global_date_list[0]
    numpeople = global_people_list[0]
    date_obj = datetime.strptime(pred_date, '%Y-%m-%d').date()  # convert to a date object
    delta = date_obj - today 
    num_days = delta.days  

    # Get a reference to the database
    ref = db.reference("/WaterBillData")
    # Order the data by key in descending order and limit the query to just the last inserted data
    query = ref.order_by_key().limit_to_last(4)
    # Retrieve the last inserted data
    snapshot = query.get()
    for key, value in snapshot.items():
        last_data = value
        current_dict_data = last_data.values()
        current_data.append(list(current_dict_data))
    # bill units

    sum_units = 0  
    sum_cost = 0
    for i in range (len(current_data)):   
        sum_units +=  int(current_data[i][3])
        sum_cost += int(current_data[i][2])
    diff_cost = abs(global_cost_list[0] - sum_cost)
    s_r = 0.97 * global_cost_list[0]
    e_r = 1.03 * global_cost_list[0]
    start_range = round(s_r, 2)  
    end_range = round(e_r, 2)  

    # the user enters the date in the format YYYY-MM-DD
    user_date = datetime.strptime(pred_date, '%Y-%m-%d')

    # extract the month and year from the user date
    user_month = user_date.month
    user_year = user_date.year

   # get the start and end dates for the desired month of the previous year
    prev_year_start_date = datetime(user_year - 1, user_month, 1)
    prev_year_end_date = prev_year_start_date + timedelta(days=32)
    prev_year_end_date = datetime(prev_year_end_date.year, prev_year_end_date.month, 1) - timedelta(days=1)

    # convert the dates to strings
    prev_year_start_date_str = prev_year_start_date.strftime('%Y-%m-%d')
    prev_year_end_date_str = prev_year_end_date.strftime('%Y-%m-%d')

    # query the records that belong to the same month of the previous year
    query = ref.order_by_child('BillDate').start_at(prev_year_start_date_str).\
        end_at(prev_year_end_date_str).get()

    for key, value in query.items():
        new_pred_result = value
        new_dict_data = new_pred_result.values()
        new_pred_list.append(list(new_dict_data))

    prev_sum_cost = global_cost_list[0]  
    prev_sum_consumption = global_consumption_list[0] 

    # Get number of days in the month for the input date
    month = date_obj.month
    year = date_obj.year
    
    num_days_in_month = None

    if month == 2:  # February
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # Leap year
            num_days_in_month = 29
        else:
            num_days_in_month = 28
    elif month in {4, 6, 9, 11}:  # April, June, September, November
        num_days_in_month = 30
    else:  # January, March, May, July, August, October, December
        num_days_in_month = 31

    e_r = ((((numpeople * prev_sum_cost)/6441) * num_days) / num_days_in_month)
    expected_result = int(e_r)

    e_r2= ((((numpeople * prev_sum_consumption)/6441) * num_days) / num_days_in_month)
    expected_result2 = int(e_r2)

    # global_list contains the predicted values of the last predicted date.
    return render_template('pdfformat.html', consumption_pred = global_consumption_list, pred_date = global_date_list, cost_pred = global_cost_list, today_date = today, prev_cost = sum_cost, prev_units = sum_units, diff_cost = diff_cost, start_range = start_range, end_range = end_range, num_days = num_days, num_people = numpeople, expected_result = expected_result, expected_result2 = expected_result2)

                                                    # MAIN


if __name__ == "__main__":
    app.run(debug=True)

