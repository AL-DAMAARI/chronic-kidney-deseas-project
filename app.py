import numpy as np

from flask import Flask, request, jsonify, render_template, url_for, redirect, session
import pickle
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import pandas as pd

#importing mysql connector
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

#loading model
model = pickle.load(open('model_rf.pkl','rb'))
scaler = pickle.load(open('scaler.pkl','rb'))


app.secret_key = 'omm'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ckd-db'
 
mysql = MySQL(app)




@app.route('/')
def home_page():
    return render_template('home.html')
#doctor login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'nF' in request.form and 'pass' in request.form:
        doctor_Name = request.form['nF']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctor WHERE doctor_Name = % s AND password = % s', (doctor_Name, password, ))
        doctor = cursor.fetchone()
        if doctor:
            session['loggedin'] = True
            session['id'] = doctor['doctorID']
            session['doctor_Name'] = doctor['doctor_Name']
            msg = 'Logged in successfully !'
            return redirect(url_for('doctor'))
        else:
            msg = 'Incorrect DName / password !'
    return render_template('login.html', msg = msg)

# # MLT login
@app.route('/MltLogin', methods=['GET', 'POST'])
def MltLogin():
    msg = ''
    if request.method == 'POST' and 'nF' in request.form and 'pass' in request.form:
        mlt_Name = request.form['nF']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM mlt WHERE mlt_Name = %s AND password = %s', (mlt_Name, password,))
        mlt = cursor.fetchone()
        if mlt:
            session['loggedin'] = True
            session['id'] = mlt['mltID']
            session['mlt_Name'] = mlt['mlt_Name']
            msg = 'Logged in successfully!'
            return redirect(url_for('mlt_page'))
        else:
            msg = 'Incorrect mltName / password!'
    return render_template('mlt.html', msg = msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('mlt_Name', None)
    return redirect(url_for('home_page'))

#the  admin
@app.route('/admin', methods = ['GET'])
def admin_page():
     #doctor tLists
    def doctortList():
        #creating variable for connection
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from doctor")
        #fetching all records from database
        data=cursor.fetchall()
        #returning back to projectlist.html with all records from MySQL which are stored in variable data
        return data
    return render_template('adminDashboard.html', data = doctortList())

#Admin Tasks 
@app.route('/addDoctor', methods=['GET', 'POST'])
def addDoctor_page():
    msg = ''
    if request.method == 'POST' and 'dName' in request.form and 'sex' in request.form  and 'E-mail' in request.form and 'password' in request.form:
        doctor_Name = request.form['dName']
        doctor_Sex = request.form['sex']
        E_mail = request.form['E-mail']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctor WHERE doctor_Name = % s', (doctor_Name, ))
        doctor = cursor.fetchone()
        if doctor:
            msg = 'User already exists !'
        elif not re.match(r'[A-Za-z0-9]+', doctor_Name):
            msg = 'PatientName must contain only characters and numbers !'
        elif not doctor_Name or not doctor_Sex or not E_mail or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO doctor VALUES (NULL, % s, % s, % s, % s)', (doctor_Name, doctor_Sex, E_mail, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('users/doctor/addDoctor.html', msg = msg)



# adding mlt
@app.route('/addMLT', methods=['GET', 'POST'])
def addMlt_page():
    msg = ''
    if request.method == 'POST' and 'mlt_Name' in request.form and 'sex' in request.form  and 'E-mail' in request.form and 'password' in request.form:
        mlt_Name = request.form['mlt_Name']
        mlt_Sex = request.form['sex']
        E_mail = request.form['E-mail']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM mlt WHERE mlt_Name = % s', (mlt_Name, ))
        mlt = cursor.fetchone()
        if mlt:
            msg = 'User already exists !'
        elif not re.match(r'[A-Za-z0-9]+', mlt_Name):
            msg = 'PatientName must contain only characters and numbers !'
        elif not mlt_Name or not mlt_Sex or not E_mail or not password:
            print('now here')
            msg = 'Please fill out the form !'
        else:
            
            cursor.execute('INSERT INTO mlt VALUES (NULL, %s, %s, %s, %s)', (mlt_Name, mlt_Sex, E_mail, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        print('why here')
        msg = 'Please fill out the form !'
    return render_template('addMlt.html', msg = msg)
#admin views
@app.route('/viewMlt', methods=['GET'])
def view_mlt():
    #mlt Lists
    def mltList():
        #creating variable for connection
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from mlt")
        #fetching all records from database
        data=cursor.fetchall()
        #returning back to projectlist.html with all records from MySQL which are stored in variable data
        return data
    return render_template('viewMlt.html', data = mltList())

# doctor dahsboard
@app.route('/doctor', methods=['GET'])
def doctor():
    #patientLists
    def patientList():
        #creating variable for connection
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from patient")
        #fetching all records from database
        data=cursor.fetchall()
        #returning back to projectlist.html with all records from MySQL which are stored in variable data
        return data
    return render_template('users/doctor/doctorDashBoard.html', data = patientList())

@app.route('/doctor/<string:id>', methods=['GET'])
def view(id):
    #patientLists
    def patientList():
        #creating variable for connection
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from laboratory where patientID = % s", (id,))
        #fetching the records from database
        data=cursor.fetchall()
        #returning back to projectlist.html with all records from MySQL which are stored in variable data
        return data
    return render_template('viewPatient.html', data = patientList())



# mlt dahsboard
@app.route('/mlt_page', methods=['GET'])
def mlt_page():
    #patientLists
    def patientList():
        #creating variable for connection
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #executing query
        cursor.execute("select * from patient")
        #fetching all records from database
        data=cursor.fetchall()
        #returning back to projectlist.html with all records from MySQL which are stored in variable data
        return data
    return render_template('users/laboratory/labDashBoard.html', data = patientList())

@app.route('/addpatient', methods =['GET', 'POST'])
def add():
    msg = ''
    if request.method == 'POST' and 'patientName' in request.form and 'age' in request.form  and 'sex' in request.form and 'phone' in request.form:
        patientName = request.form['patientName']
        patientAge = request.form['age']
        patientSex = request.form['sex']
        patientPhone = request.form['phone']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE patientName = % s', (patientName, ))
        user = cursor.fetchone()
        if user:
            msg = 'User already exists !'
        elif not re.match(r'[A-Za-z0-9]+', patientName):
            msg = 'PatientName must contain only characters and numbers !'
        elif not patientName or not patientAge or not patientSex or not patientPhone:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO patient VALUES (NULL, % s, % s, % s, % s)', (patientName, patientAge, patientSex, patientPhone,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('users/laboratory/addPatient.html', msg = msg)





#Update Patient
@app.route('/update', methods=['GET','POST'])
def update_patient():
    # if request.method == POST:
    id = request.form['patientID']
    patientName = request.form['patientName']
    patientAge = request.form['patientAge']
    patientSex = request.form['patientSex']
    patientPhone = request.form['patientPhone']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
            UPDATE patient
            set patientName = %s, patientAge = %s, 
            patientSex = %s, patientPhone = %s
            where patientID = %s
        """, (patientName, patientAge, patientSex, patientPhone, id))
    mysql.connection.commit()
    # msg = 'updated successfully!'
    return redirect(url_for('mlt_page'))
#Delete Patient
@app.route('/delete/<string:id>', methods=['GET','POST'])
def delete_patient(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('delete from patient where patientID = %s', (id,))
    mysql.connection.commit()
    # msg = 'updated successfully!'
    return redirect(url_for('mlt_page'))
#take medical laboratpry
@app.route('/medicalLab/<string:id>', methods=['GET','POST'])
def take_medicalLab(id):

    patientID = id
    result = ''
    msg = ''
    if request.method == 'POST' and 'sg' in request.form and 'rbc' in request.form  and 'pc' in request.form and 'sod' in request.form and 'hemo' in request.form and 'pcv' in request.form and 'rc' in request.form and 'htn' in request.form:
        sg = request.form['sg']
        rbc = request.form['rbc']
        pc = request.form['pc']
        sod= request.form['sod']
        hemo= request.form['hemo']
        pcv= request.form['pcv']
        rc= request.form['rc']
        htn= request.form['htn']
        result = prediction(sg, rbc, pc, sod, hemo, pcv, rc, htn, scaler, model)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM  WHERE patientName = % s', (patientName, ))
        # user = cursor.fetchone()
        # if user:
        #     msg = 'User already exists !'
        # elif not re.match(r'[A-Za-z0-9]+', patientName):
        #     msg = 'PatientName must contain only characters and numbers !'
        if not sg or not rbc or not pc or not sod or not hemo or not pcv or not rc or not htn:
            msg = 'Please fill out the form !'
            print('problem occurs here')
        else:
            cursor.execute('INSERT INTO laboratory VALUES (NULL, % s, % s, % s, % s, %s, %s, %s, %s, %s, %s)', (patientID, sg, rbc, pc,sod, hemo, pcv, rc, htn, result))
            mysql.connection.commit()
            # msg = 'You have successfully registered !'
    elif request.method == 'POST':
        print('problem occurs here')
        msg = 'Please fill out the form !'
    return render_template('users/laboratory/medicalLab.html', msg = msg, id = patientID, res = result)
def prediction(sg, rbc, pc, sod, hemo, pcv, rc, htn, scaler, model):
    
   

    one = ['yes', 'present', 'good', 'normal', 'Yes', 'Present', 'Good', 'Normal', 'YES', 'PRESENT', 'GOOD', 'NORMAL']
    zero = ['no', 'notpresent', 'not present', 'poor', 'abnormal', 'No', 'Notpresent', 'NotPresent', 'Not Present', 'Poor', 'Abnormal', 'AbNormal', 'NO', 'NOTPRESENT', 'NOT PRESENT', 'POOR', 'ABNORMAL']
    int_features = []
    #storing to the list
    my_lst = [sg, rbc, pc, sod, hemo, pcv, rc, htn]
    

    for i in my_lst:
        if i in one:
            int_features.append(1.0)
        elif i in zero:
            int_features.append(0.0)
        else:
            int_features.append(float(i))
            
    final_features = [np.array(int_features)]
    
    print("has size of ", len(int_features))
    print("al r s: ", request.form.values())
    final_features = scaler.transform(final_features)
    
    prediction = model.predict(final_features)
    output = prediction
    print(output)
    if output == [0]:
        output = "Patient has no ckd"
    elif output == [1]:
        output = "Patient has ckd"
    return output





if __name__ == '__main__':
    app.run(port=7000, debug=True)
