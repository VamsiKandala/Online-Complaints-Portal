from flask import Flask, request, redirect,render_template,session,url_for,flash
import mysql.connector
import os
from cmail import sendmail


app = Flask(__name__)
app.secret_key = "super secret key"
#mydb=mysql.connector.connect(host="localhost",user="root",password="vamsi",db="ocp")
#cursor=mydb.cursor()
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')
with mysql.connector.connect(host=host,user=user,password=password,port=port,db=db) as conn:
    cursor=conn.cursor(buffered=True)
    cursor.execute("create table if not exists usercomp(complaintno varchar(10),issue varchar(1000),description varchar(2000),usermail varchar(100),username varchar(100),response varchar(20))")
    cursor.execute("create table if not exists userdata(name varchar(50),email varchar(100),dob varchar(20),password varchar(30))")
    cursor.execute("create table if not exists adcomp(username varchar(100),password varchar(30))")
    cursor.close()
mydb=mysql.connector.connect(host=host,user=user,password=password,db=db)
@app.route('/')
def h1():
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        un=request.form['email']
        up=request.form['password1']
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select count(*) from adcomp where username=%s and password=%s",(un,up))
        record=cursor.fetchone()[0]
        if record==1:
            session['loggedin']=True
            session['username']=un
            return redirect(url_for('adminview'))
        else:
            flash('Invalid Username/Password')
            return render_template('admin_login.html')
        mydb.commit()
    return render_template('admin_login.html')

@app.route('/adminview',methods=['GET','POST'])
def adminview():
    cursor.execute("select * from usercomp")
    record=cursor.fetchall()
    #ab=cursor.execute("update usercomp set response=:s" ,(aa))
    mydb.commit()
    if record:
        return render_template('admin_view.html',value=record)
        
        
    return render_template('admin_view.html')

@app.route('/updatestatus',methods=['GET','POST'])
def updatestatus():
    if request.method == 'POST':
        aa=request.form['compno']
        ab=request.form['status']
        cno=[aa]
        result=cursor.execute("update usercomp set response=%s where complaintno=%s",(ab,aa))
        ac=cursor.execute("select usermail,issue from usercomp where complaintno=%s",(cno))
        ad=cursor.fetchone()
        if ab=='Solved':
            subject='Complaint Status'
            body=f"Your Registered Complaint no:{aa} regarding the problem:{ad[1]} is Solved.Thanks For Contacting The Online Complaints Portal."
            sendmail(to=ad[0],subject=subject,body=body)
            return redirect(url_for('adminview'))
        elif ab=='In Progress':
            subject='Complaint Status'
            body=f"Your Registered Complaint no:{aa} regarding the problem:{ad[1]} is Updated to In Progress.Thanks For Contacting The Online Complaints Portal."
            sendmail(to=ad[0],subject=subject,body=body)
            return redirect(url_for('adminview'))

        
        a=mydb.commit()
        
        
    return render_template('update_status.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully logged out')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)
