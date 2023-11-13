from flask import Flask,render_template,request,redirect,url_for,jsonify
from datetime import date,datetime
from db_connector import getDbConnection
import calendar

app = Flask(__name__)

mysql = getDbConnection(app)

@app.route('/')
def home():
    query = 'SELECT * FROM expense_table ORDER BY id DESC LIMIT 5;'
    data = dataFetcher(query)
    reportData = {}
    Limit = 30000

    reportData['date'] = date.today().strftime('%d-%m-%y')
    reportData['current_month'] = datetime.now().month
    reportData['current_month_name'] = getMonthName(reportData['current_month'])
    reportData['current_year'] = datetime.now().year
    reportData['Rent'] = getExpenseForCategogry("Rent",reportData['current_month'],reportData['current_year'])
    reportData['Food'] = getExpenseForCategogry("DirectiFood",reportData['current_month'],reportData['current_year']) + getExpenseForCategogry("OutsideFood",reportData['current_month'],reportData['current_year'])
    reportData['Others'] = getExpenseForCategogry("Other",reportData['current_month'],reportData['current_year'])
    reportData['Home'] = getExpenseForCategogry("Home",reportData['current_month'],reportData['current_year'])
    reportData['Travel'] = getExpenseForCategogry("Travel",reportData['current_month'],reportData['current_year'])
    reportData['Bills'] = getExpenseForCategogry("Bills",reportData['current_month'],reportData['current_year'])
    reportData['expense'] = reportData['Rent'] + reportData['Food'] + reportData['Others'] + reportData['Travel'] + reportData['Bills']
    reportData['remaining_amount'] = Limit - reportData['expense']
    reportData['days_left'] = getNumOfDaysLeft()
    reportData['Total'] = getTotalExpenseForParticularMonth(reportData['current_month'],reportData['current_year'])
    app.logger.info(reportData)
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
        cur.execute(query)
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('home'))


@app.route('/execute_sql', methods=['GET', 'POST'])
def execute_sql():
    if request.method == 'POST':
        sql_query = request.form['sql_query']
        cursor = mysql.connection.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        result_json = [dict(zip(columns, row)) for row in result]
        print(result_json)
        return jsonify(result_json)
    return render_template('customquery.html')



def dataFetcher(query):
    app.logger.info(query)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    app.logger.info(data)
    cur.close()
    return data

def getTotalExpenseForParticularMonth(month,year):
    query = 'SELECT SUM(amount) AS total_expenses FROM expense_table WHERE YEAR(date) = {} AND MONTH(date) = {};'
    query = query.format(year,month)

    data = dataFetcher(query)
    if data[0][0] is None:
        return 0
    return data[0][0]

def getMonthName(month):
    month_names = ["January","February","March","April","May","June","July",
            "August","September","October","November","December"]
    return month_names[month - 1]

def getNumOfDaysLeft():
    current_date = datetime.now()
    last_day_of_month = calendar.monthrange(current_date.year, current_date.month)
    days_left = last_day_of_month[1] - current_date.day
    return days_left

def getExpenseForCategogry(category,month,year):
    query = 'SELECT SUM(amount) FROM expense_table where category = "{}" and MONTH(date) = {} and YEAR(date) = {};'
    query = query.format(category,month,year)
    data = dataFetcher(query)
    if data[0][0] is None:
        return 0
    return data[0][0]