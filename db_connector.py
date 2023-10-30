from flask_mysqldb import MySQL


def getDbConnection(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'rootroot'
    app.config['MYSQL_DB'] = 'expense_tracker'
    return MySQL(app)