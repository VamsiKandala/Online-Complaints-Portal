from flask import Flask, request, redirect,render_template,session,url_for,flash
import mysql.connector
import random
import math
from key import secret_key,salt
from itsdangerous import URLSafeTimedSerializer
from stoken import token
from cmail import sendmail


app = Flask(__name__)
app.secret_key =secret_key


mydb=mysql.connector.connect(host="localhost",user="root",password="vamsi",db="ocp")
cursor=mydb.cursor()




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
        cursor.execute("select count(*) from userdata where email=%s and password=%s",(usermail,up))
        record=cursor.fetchone()[0]
        print(record)
        if record==1:
            session['loggedin']=True
            session['usermail']=usermail
            return redirect(url_for('userview'))
        else:
            flash('Invalid Username/Password')
            return render_template('login.html')
    mydb.commit()
    return render_template('login.html')

@app.route('/userregistration',methods=['GET','POST'])
def userregistration():
    if request.method == 'POST':
        uname=request.form['name']
        umail=request.form['email']
        udob=request.form['date']
        upass=request.form['password2']
        cursor.execute('select count(*) from userdata where name=%s',[uname])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from userdata where email=%s',[umail])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('username already in use')
            return render_template('registration.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('registration.html')
        data={'username':uname,'password':upass,'email':umail,'dob':udob}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('confirm',token=token(data),_external=True)}"
        sendmail(to=umail,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('userlogin'))
        
    return render_template('registration.html')

@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
        #print(e)
        return 'Link Expired register again'
    else:
        cursor=mydb.cursor(buffered=True)
        username=data['username']
        cursor.execute('select count(*) from userdata where name=%s',[username])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('login'))
        else:
            cursor.execute('insert into userdata values(%s,%s,%s,%s)',[data['username'],data['email'],data['dob'],data['password']])
            mydb.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('userlogin'))

@app.route('/userview',methods=['GET','POST'])
def userview():
    usermail=[session.get('usermail')]
    cursor.execute("select complaintno,issue,description,response from usercomp where usermail=%s",(usermail))
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
        digits = "0123456789"
        a='pending'
        OTP=''
            #now we will use math module along with module to generate a customized
            #6 digit otp
        for i in range(6):
            OTP = OTP + digits[math.floor(random.random()*10)]
        
        data={'OTP':OTP,'subject':usub,'body':ubody,'usermail':unmail,'response':a}
        
        cursor.execute("select email,name from userdata where email=%s",([data['usermail']]))
        emailrec=cursor.fetchone()
        if emailrec:
            result=cursor.execute("insert into usercomp values(%s,%s,%s,%s,%s)",[data['OTP'],data['subject'],data['body'],data['usermail'],data['response']])
            mydb.commit()
            return redirect(url_for('userview'))
        else:
            return render_template('complaint.html')
        
    return render_template('complaint.html')

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully logged out')
        return redirect(url_for('userlogin'))
    else:
        return redirect(url_for('userlogin'))








if __name__ == '__main__':
    app.run(debug=True)
