from flask import Flask,render_template,request,redirect,url_for
from datetime import date,datetime
from db_connector import getDbConnection

app = Flask(__name__)

mysql = getDbConnection(app)

@app.route('/')
def home():
    query = 'SELECT * FROM expense_table;'
    data = dataFetcher(query)
    reportData = {}
    Limit = 30000

    reportData['date'] = date.today().strftime('%d-%m-%y')
    reportData['current_month'] = datetime.now().month
    reportData['current_month_name'] = getMonthName(reportData['current_month'])
    reportData['current_year'] = datetime.now().year
    expense = getExpenseForParticularMonth(reportData['current_month'],reportData['current_year'])
    reportData['expense'] = expense
    reportData['remaining_amount'] = Limit - expense
    return render_template('index.html',data=data,reportData=reportData)

@app.route('/add', methods=['POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        cur = mysql.connection.cursor()
        query = 'INSERT INTO expense_table (amount, category, date) VALUES ({},"{}","{}");'
        query = query.format(amount,category,date)
        print("query = " + query)
        cur.execute(query)
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('home'))

def dataFetcher(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

def getExpenseForParticularMonth(month,year):
    query = 'SELECT SUM(amount) AS total_expenses FROM expense_table WHERE YEAR(date) = {} AND MONTH(date) = {};'
    query = query.format(year,month)

    data = dataFetcher(query)
    return data[0][0]

def getMonthName(month):
    month_names = ["January","February","March","April","May","June","July",
            "August","September","October","November","December"]
    return month_names[month - 1]