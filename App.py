from flask import Flask, render_template, url_for
# from flask_mysqldb import MySQL

app = Flask(__name__)

# Mysql Connection
# app.config['MYSQL_HOST'] = 'us-cdbr-east-04.cleardb.com'      #default, sino ip
# app.config['MYSQL_USER'] = 'b4d3b8e1fc8fb2'           #default
# app.config['MYSQL_PASSWORD'] = 'e34e027d'           #Como no tiene va vacio
# app.config['MYSQL_DB'] = 'heroku_cf5f6f322e8e525'
# mysql = MySQL(app)

# settings
# app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    return render_template('index.html')
    # cur = mysql.connection.cursor()
    # cur.execute('SELECT * FROM contacts')
    # data = cur.fetchall()
    # print(data)
    # return render_template('index.html', contacts = data)


if __name__ == '__main__':
    app.run(port = 3000, debug = True)