from flask import Flask, render_template, url_for
from flask_mysqldb import MySQL
import json

MY_JSON_FILE_NAME = "static/json/initial_data.json"
DB_JSON_FILE_NAME = "static/json/db_data.json"
TRY_JSON_FILE_NAME = "static/json/try_this_data.json"

app = Flask(__name__)

# Mysql Connection
app.config['MYSQL_HOST'] = 'us-cdbr-east-04.cleardb.com'      #default, sino ip
app.config['MYSQL_USER'] = 'b84140fd6b4ddf'           #default
app.config['MYSQL_PASSWORD'] = '103a3e04'           #Como no tiene va vacio
app.config['MYSQL_DB'] = 'heroku_f1785faf0fab98b'
mysql = MySQL(app)

# settings
app.secret_key = 'mysecretkey'



# A way to get the same result, but by storing the hole JSON File

def get_db_json_bin():
    # Get JSON File from MySQL if exists
    db_json_bin = ''
    try:
        cur = mysql.connection.cursor()
        result = cur.execute("""SELECT data FROM table_json 
        WHERE EXISTS (SELECT data FROM table_json);""")
        db_json_bin = cur.fetchall()
        print("JSON file loaded successfully from MySQL, result: ", result)
    except mysql.connection.Error as error:
        print("Failed loading JSON file from MySQL table: {0}".format(error))
    return db_json_bin

def get_my_json_bin(my_json_file):
    # Get JSON File from Local as binary
    with open(my_json_file, 'rb') as file:
        my_json_bin = file.read()
    print("JSON file loaded successfully from Local")
    return my_json_bin

def store_json_bin(my_json_bin):
    # Updating DB with Local JSON File
    try:
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE IF EXISTS table_json;")
        cur.execute("CREATE TABLE table_json (data BLOB);")
        query = "INSERT INTO table_json (data) VALUES (%s)"
        result = cur.execute(query, [my_json_bin])
        mysql.connection.commit()
        print("Local JSON File inserted successfully as a BLOB into table_json table, result: ", result)
    except mysql.connection.Error as error:
        print("Failed inserting BLOB data into MySQL table: {0}".format(error))

def load_data(new_file_name):
    # Import JSON Data from MySQL
    try:
        cur = mysql.connection.cursor()
        result = cur.execute('SELECT data FROM table_json')
        json_file = cur.fetchall()
        # Writing file
        with open(new_file_name, 'wb') as file:
            file.write(json_file[0][0])
        # Get Python JSON Object
        with open(new_file_name) as file:
            new_data = json.load(file)  
        print("JSON file loaded successfully from table_json table, result: ", result)
    except mysql.connection.Error as error:
        print("Failed loading JSON file from MySQL table: {0}".format(error))
    return new_data

@app.route('/')
def exportJsonFile():
    print()
    print('Start Web-App >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('Checking JSON Data...')
    db_json_bin = get_db_json_bin()
    if db_json_bin:
        db_json_bin = db_json_bin[0][0]
    my_json_bin = get_my_json_bin(MY_JSON_FILE_NAME)
    # Also yo can try with TRY_JSON_FILE_NAME

    if len(db_json_bin) != len(my_json_bin):
        print("DB JSON File needs update, proceding to export local json file to MySQL...")
        store_json_bin(my_json_bin)
        print("Data Base updated")
    else:
        print("Data Base is updated")

    print("Proceding to import the data json...")
    db_data = load_data(DB_JSON_FILE_NAME)
    print("JSON Data loaded correctly and ready to use.")

    all_theraputic_areas = []
    for medication in db_data["CurrentMedications"]:
        for therapeutic_area in medication["TheraputicArea"]:
            if not therapeutic_area in all_theraputic_areas:
                all_theraputic_areas.append(therapeutic_area)

    return render_template('index.html', data = db_data, theraputic_areas = all_theraputic_areas)


if __name__ == '__main__':
    app.run(port = 3000, debug = True)