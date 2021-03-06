from flask import Flask, render_template, url_for
from flask_mysqldb import MySQL
import json

MY_JSON_FILE_NAME = "static/json/initial_data.json"
DB_JSON_FILE_NAME = "static/json/db_data.json"
TRY_JSON_FILE_NAME = "static/json/try_this_data.json"

app = Flask(__name__)

# Local MySQL Connection, Testing
# app.config['MYSQL_HOST'] = 'localhost'      #default, sino ip
# app.config['MYSQL_USER'] = 'root'           #default
# app.config['MYSQL_PASSWORD'] = 'password'           #Como no tiene va vacio
# app.config['MYSQL_DB'] = 'datajson'


# Mysql Connection
app.config['MYSQL_HOST'] = 'us-cdbr-east-04.cleardb.com'      #default, sino ip
app.config['MYSQL_USER'] = 'b84140fd6b4ddf'           #default
app.config['MYSQL_PASSWORD'] = '103a3e04'           #Como no tiene va vacio
app.config['MYSQL_DB'] = 'heroku_f1785faf0fab98b'
mysql = MySQL(app)

# settings
app.secret_key = 'mysecretkey'


# First Way for complete the task, by Storing JSON Data, not file >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_my_json_obj(my_json_file):
    # Get JSON Object from Local
    with open(my_json_file) as file:
        my_json_obj = json.load(file)  
    print("JSON file loaded successfully from Local")
    return my_json_obj

def excuteCommand(success_msg, error_msg, query):
    try:
        cur = mysql.connection.cursor()
        result = cur.execute(query)
        mysql.connection.commit()
        # print(f"{success_msg}, result:", result)
        return cur.fetchall()
    except mysql.connection.Error as error:
        print(f"{error_msg}, error: {error}")


def store_json_obj(my_json_obj):
    # Export JSON Data to MySQL
    s_msg = "Uploaded "
    e_msg = "Fail to upload "
    # fullQuery = ""

    # MainInfo Table
    query = "DROP TABLE IF EXISTS main_info;"
    # fullQuery += query
    excuteCommand(s_msg + "MainInfo Delete", e_msg, query)  

    query = """
    CREATE TABLE main_info (
        id INT NOT NULL AUTO_INCREMENT,
        samplenumber VARCHAR(15) DEFAULT NULL,
        pipelineversion VARCHAR(10) DEFAULT NULL,
        sequencer VARCHAR(20) DEFAULT NULL,
        knowledgebaseversion VARCHAR(10) DEFAULT NULL,
        dategenerated VARCHAR(30) DEFAULT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "MainInfo", e_msg, query)  

    query = f"""
    INSERT INTO main_info 
    (id, samplenumber, pipelineversion, sequencer, knowledgebaseversion, dategenerated)
    VALUES 
    (
        1,
        '{ my_json_obj["SampleNumber"]}',
        '{ my_json_obj["PipelineVersion"]}',
        '{ my_json_obj["Sequencer"]}',
        '{ my_json_obj["KnowledgebaseVersion"]}',
        '{ my_json_obj["DateGenerated"]}'
    );
    """
    # fullQuery += query
    excuteCommand(s_msg + "MainInfo Data", e_msg, query)  

    # CurrentMedications Table
    query = "DROP TABLE IF EXISTS currentmedications;"
    # fullQuery += query
    excuteCommand(s_msg + "CurrentMedications Delete", e_msg, query)  

    query = """
    CREATE TABLE currentmedications (
        id INT NOT NULL AUTO_INCREMENT,
        groupphenotype VARCHAR(30) NOT NULL,
        idaction INT NOT NULL,
        recommendation VARCHAR(150) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "CurrentMedications", e_msg, query)  

    query = f"""
    INSERT INTO currentmedications 
    (id, groupphenotype, idaction, recommendation)
    VALUES """

    AllActions = []
    for medication in my_json_obj["CurrentMedications"]:
        if not medication["Action"][0] in AllActions:
            AllActions.append(medication["Action"][0])

    idMed = 0
    for medication in my_json_obj["CurrentMedications"]:
        idMed += 1
        query += f"""
        (
            {idMed},
            '{ medication['GroupPhenotype']}',
            '{ AllActions.index(medication['Action'][0]) + 1 }',
            '{ medication['Recommendation']}'
        ),"""

    query = query[:-1] + ";"
    # fullQuery += query
    excuteCommand(s_msg + "CurrentMedications Data", e_msg, query)  


    # TheraputicArea Table
    query = "DROP TABLE IF EXISTS theraputicarea;"
    # fullQuery += query
    excuteCommand(s_msg + "TheraputicArea Delete", e_msg, query)  

    query = """
    CREATE TABLE theraputicarea (
        id INT NOT NULL AUTO_INCREMENT,
        area VARCHAR(20) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "TheraputicArea", e_msg, query)  

    AllAreas = []
    for medication in my_json_obj["CurrentMedications"]:
        for area in medication["TheraputicArea"]:
            if not area in AllAreas:
                AllAreas.append(area)

    query = f"""
    INSERT INTO theraputicarea 
    (id, area)
    VALUES """

    idMed = 0
    for area in AllAreas:
        idMed += 1
        query += f"({idMed},'{area}'),"

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "TheraputicArea Data", e_msg, query)  


    # TheraputicAreaOfCurrentMedication Table
    query = "DROP TABLE IF EXISTS theraputicareaofcurrentmedication;"
    # fullQuery += query
    excuteCommand(s_msg + "theraputicareaofcurrentmedication Delete", e_msg, query)  

    query = """
    CREATE TABLE theraputicareaofcurrentmedication (
        id INT NOT NULL AUTO_INCREMENT,
        idcurrentmedications INT NOT NULL,
        idtheraputicarea INT NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "TheraputicAreaOfCurrentMedication", e_msg, query)  


    query = f"""
    INSERT INTO theraputicareaofcurrentmedication 
    (id, idcurrentmedications, idtheraputicarea)
    VALUES """
   
    idMed = 0
    idArea = 0
    for medication in my_json_obj["CurrentMedications"]:
        idMed += 1
        for area in medication["TheraputicArea"]:
            idArea += 1
            query += f"({idArea},'{ idMed }','{ AllAreas.index(area) + 1 }'),"

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "TheraputicAreaOfCurrentMedication Data", e_msg, query)  
    

    
    # Action Table
    query = "DROP TABLE IF EXISTS action;"
    # fullQuery += query
    excuteCommand(s_msg + "Action Delete", e_msg, query)  

    query = """
    CREATE TABLE action (
        id INT NOT NULL AUTO_INCREMENT,
        value VARCHAR(15) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "Action", e_msg, query)  

    AllActions = []
    for medication in my_json_obj["CurrentMedications"]:
        for action in medication["Action"]:
            if not action in AllActions:
                AllActions.append(action)

    query = f"""
    INSERT INTO action 
    (id, value)
    VALUES """

    idMed = 0
    for action in AllActions:
        idMed += 1
        query += f"({idMed}, '{action}'),"

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "Action Data", e_msg, query)  


    # Generic Table
    query = "DROP TABLE IF EXISTS generic;"
    # fullQuery += query
    excuteCommand(s_msg + "Generic Delete", e_msg, query)  

    query = """
    CREATE TABLE generic (
        id INT NOT NULL AUTO_INCREMENT,
        value VARCHAR(25) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "Generic", e_msg, query)  

    query = f"""
    INSERT INTO generic 
    (id, value)
    VALUES """

    idMed = 0
    AllGenerics = []
    for medication in my_json_obj["CurrentMedications"]:
        for drugs in medication["Drugs"]:
            for generic in drugs["Generic"]:
                if not generic in AllGenerics:
                    idMed += 1
                    AllGenerics.append(generic)
                    query += f"({idMed},'{generic}'),"

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "Generic Data", e_msg, query)  


    # Trade Table
    query = "DROP TABLE IF EXISTS trade;"
    # fullQuery += query
    excuteCommand(s_msg + "Trade Delete", e_msg, query)  

    query = """
    CREATE TABLE trade (
        id INT NOT NULL AUTO_INCREMENT,
        value VARCHAR(25) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "Trade", e_msg, query)  

    query = f"""
    INSERT INTO trade 
    (id, value)
    VALUES """

    idMed = 0
    AllTrades = []
    for medication in my_json_obj["CurrentMedications"]:
        for drugs in medication["Drugs"]:
            for trade in drugs["Trade"]:
                if not trade in AllTrades:
                    idMed += 1
                    AllTrades.append(trade)
                    query += f"({idMed},'{trade}'),"

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "Trade Data", e_msg, query)  


    # Drugs Table
    query = "DROP TABLE IF EXISTS drugs;"
    # fullQuery += query
    excuteCommand(s_msg + "Drugs Delete", e_msg, query)  

    query = """
    CREATE TABLE drugs (
        id INT NOT NULL AUTO_INCREMENT,
        idcurrentmedications INT NOT NULL,
        idgeneric INT NOT NULL,
        idtrade INT NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "Drugs", e_msg, query)  

    query = f"""
    INSERT INTO drugs 
    (id, idcurrentmedications, idgeneric, idtrade)
    VALUES """

    idDrug = 0
    idMed = 0
    for medication in my_json_obj["CurrentMedications"]:
        idMed += 1
        for drug in medication["Drugs"]:
            idDrug += 1
            query += f"""(
                {idDrug},
                {idMed},
                {AllGenerics.index(drug["Generic"][0]) + 1},
                {AllTrades.index(drug["Trade"][0]) + 1}
                ),"""

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "Drugs Data", e_msg, query)  
    

    # GeneInfo Table
    query = "DROP TABLE IF EXISTS geneinfo;"
    # fullQuery += query
    excuteCommand(s_msg + "GeneInfo Delete", e_msg, query)  

    query = """
    CREATE TABLE geneinfo (
        id INT NOT NULL AUTO_INCREMENT,
        idcurrentmedications INT NOT NULL,
        gene VARCHAR(15) NOT NULL,
        genotype VARCHAR(10) NOT NULL,
        phenotype VARCHAR(25) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    """
    # fullQuery += query
    excuteCommand(s_msg + "GeneInfo", e_msg, query)  

    query = f"""
    INSERT INTO geneinfo 
    (id, idcurrentmedications, gene, genotype, phenotype)
    VALUES """

    idGene = 0
    idMed = 0
    for medication in my_json_obj["CurrentMedications"]:
        idMed += 1
        for gene in medication["GeneInfo"]:
            idGene += 1
            query += f"""(
                {idGene},
                {idMed},
                '{gene["Gene"]}',
                '{gene["Genotype"]}',
                '{gene["Phenotype"]}'
                ),"""

    query = query[:-1] + ";"

    # fullQuery += query
    excuteCommand(s_msg + "GeneInfo Data", e_msg, query)  

    # with open("sent_sql.txt", 'w') as file:
    #     file.write(fullQuery)


def load_data(new_file_name):
    # Import JSON Data from MySQL
    s_msg = "Downloaded "
    e_msg = "Fail to download "
    db_json = { "CurrentMedications": [] }

    query = "SELECT * FROM currentmedications"
    CurrentMedications = excuteCommand(s_msg + "CurrentMedications Data", e_msg, query)  
    query = "SELECT * FROM theraputicarea"
    TheraputicArea = excuteCommand(s_msg + "TheraputicArea Data", e_msg, query)  
    query = "SELECT * FROM theraputicareaofcurrentmedication"
    TAofCM = excuteCommand(s_msg + "TheraputicAreaOfCurrentMedication Data", e_msg, query)  
    query = "SELECT * FROM action"
    Action = excuteCommand(s_msg + "Action Data", e_msg, query)  
    query = "SELECT * FROM drugs"
    Drugs = excuteCommand(s_msg + "Drugs Data", e_msg, query)  
    query = "SELECT * FROM trade"
    Trade = excuteCommand(s_msg + "Trade Data", e_msg, query)  
    query = "SELECT * FROM generic"
    Generic = excuteCommand(s_msg + "Generic Data", e_msg, query)  
    query = "SELECT * FROM geneinfo"
    GeneInfo = excuteCommand(s_msg + "GeneInfo Data", e_msg, query)  
     
    AllActions = []
    for act in Action:
        AllActions.append(act[1])

    AllAreas = []
    for area in TheraputicArea:
        AllAreas.append(area[1])

    AllTrades = []
    for trade in Trade:
        AllTrades.append(trade[1])

    AllGenerics = []
    for generic in Generic:
        AllGenerics.append(generic[1])

    for medication in CurrentMedications:
        if medication:
            medicationAreas = []
            for item in TAofCM:
                if item[1] is medication[0]:
                    medicationAreas.append(AllAreas[(item[2] - 1)])

            medicationDrugs = []
            for drug in Drugs:
                if drug[1] is medication[0]:
                    medicationDrugs.append({
                        "Generic": [AllGenerics[(drug[2] - 1)],],
                        "Trade": [AllTrades[(drug[3] - 1)],]
                    })    
            
            medicationGeneInfo = []
            for gene in GeneInfo:
                if gene[1] is medication[0]:
                    medicationGeneInfo.append({
                        "Gene": gene[2],
                        "Genotype": gene[3],
                        "Phenotype": gene[4]
                    })    
            
            db_json["CurrentMedications"].append({
                "Drugs": medicationDrugs,
                "TheraputicArea": medicationAreas,
                "GeneInfo": medicationGeneInfo,
                "GroupPhenotype": medication[1],
                "Action": [AllActions[(medication[2] - 1)],],
                "Recommendation": medication[3] 
            })


    # Writing file
    with open(new_file_name, 'w') as file:
        file.write(json.dumps(db_json, indent=2 ))

    return db_json


@app.route('/')
def exportJsonData():
    print()
    print('Start Web-App >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    my_json_obj = get_my_json_obj(MY_JSON_FILE_NAME)
    # Try with TRY_JSON_FILE_NAME
    
    print("Updating DB JSON File, proceding to export local json file to MySQL...")
    store_json_obj(my_json_obj)
    print("Updated Data Base")

    print("Proceding to import the data json...")
    db_data = load_data(DB_JSON_FILE_NAME)
    print("JSON Data loaded correctly and ready to use.")

    all_theraputic_areas = []
    for medication in db_data["CurrentMedications"]:
        for therapeutic_area in medication["TheraputicArea"]:
            if not therapeutic_area in all_theraputic_areas:
                all_theraputic_areas.append(therapeutic_area)

    return render_template('index.html', data = db_data, theraputic_areas = all_theraputic_areas)


@app.route('/bigger')
def exportJsonDataBiggerFile():
    print()
    print('Start Web-App >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    my_json_obj = get_my_json_obj(TRY_JSON_FILE_NAME)

    print("Updating DB JSON File, proceding to export local json file to MySQL...")
    store_json_obj(my_json_obj)
    print("Updated Data Base")

    print("Proceding to import the data json...")
    db_data = load_data(DB_JSON_FILE_NAME)
    print("JSON Data loaded correctly and ready to use.")

    all_theraputic_areas = []
    for medication in db_data["CurrentMedications"]:
        for therapeutic_area in medication["TheraputicArea"]:
            if not therapeutic_area in all_theraputic_areas:
                all_theraputic_areas.append(therapeutic_area)

    return render_template('index.html', data = db_data, theraputic_areas = all_theraputic_areas)





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
    # Export JSON File to MySQL
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

def load_data_bin(new_file_name):
    # Import JSON File from MySQL
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

@app.route('/export-json-file')
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
    db_data = load_data_bin(DB_JSON_FILE_NAME)
    print("JSON Data loaded correctly and ready to use.")

    all_theraputic_areas = []
    for medication in db_data["CurrentMedications"]:
        for therapeutic_area in medication["TheraputicArea"]:
            if not therapeutic_area in all_theraputic_areas:
                all_theraputic_areas.append(therapeutic_area)

    return render_template('index.html', data = db_data, theraputic_areas = all_theraputic_areas)


if __name__ == '__main__':
    app.run(port = 3000, debug = True)