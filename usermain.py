from flask import Flask, request, redirect,render_template,session,url_for,flash
import cx_Oracle
import random
import math

con = cx_Oracle.connect('vamsi/vamsi@localhost:1521/xe')
cursor=con.cursor()

app = Flask(__name__)
app.secret_key = "super secret key"



@app.route('/')
def h1():
    return redirect(url_for('home'))
@app.route('/home')
def home():
    return render_template('Home.html')

@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    if request.method == 'POST':
        usermail=request.form['email']
        up=request.form['password1']
        result=cursor.execute("select * from userdata where email=:s and password=:s",(usermail,up))
        record=result.fetchone()
        if record:
            session['loggedin']=True
            session['usermail']=record[1]
            session['username']=record[0]
            return redirect(url_for('userview'))
        con.commit()
    return render_template('login.html')

@app.route('/userregistration',methods=['GET','POST'])
def userregistration():
    if request.method == 'POST':
        uname=request.form['name']
        umail=request.form['email']
        udob=request.form['date']
        upass=request.form['password2']
        result=cursor.execute("insert into userdata values(:s,:s,:s,:s)",(uname,umail,udob,upass))
        con.commit()
        return redirect(url_for('home'))
    return render_template('registration.html')

@app.route('/userview',methods=['GET','POST'])
def userview():
    usermail=session.get('usermail')
    username=session.get('username')
    result=cursor.execute("select complaintno,issue,description,response from usercomp where usermail=:s and username=:s",(usermail,username))
    record=cursor.fetchall()
    if record:
        return render_template('user_view.html',value=record)
    return render_template('user_view.html')

@app.route('/usercomplaint',methods=['GET','POST'])
def usercomplaint():
    if request.method == 'POST':
        usub=request.form['subject']
        ubody=request.form['body']
        unmail=session.get('usermail')
        uname=session.get('username')
        digits = "0123456789"
        a='pending'
        OTP=''
            #now we will use math module along with module to generate a customized
            #6 digit otp
        for i in range(6):
            OTP = OTP + digits[math.floor(random.random()*10)]

        email=cursor.execute("select email,name from userdata where email=:s and name=:s",(unmail,uname))
        emailrec=cursor.fetchone()
        if emailrec:
            result=cursor.execute("insert into usercomp values(:s,:s,:s,:s,:s,:s)",(OTP,usub,ubody,unmail,uname,a))
            con.commit()
            return redirect(url_for('userview'))
        else:
            return render_template('complaint.html',message='Email/username is not correct.Please enter registered mail to register complaint')
        
    return render_template('complaint.html')








if __name__ == '__main__':
    app.run(debug=True)
