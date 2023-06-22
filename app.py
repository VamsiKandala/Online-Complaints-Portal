from flask import Flask, request, redirect,render_template,session,url_for,flash
import mysql.connector
import random
import math,os
from key import secret_key,salt
from itsdangerous import URLSafeTimedSerializer
from stoken import token
from cmail import sendmail


app = Flask(__name__)
app.secret_key =secret_key


#mydb=mysql.connector.connect(host="localhost",user="root",password="vamsi",db="ocp")
#cursor=mydb.cursor()

user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')
with mysql.connector.connect(host=host,user=user,password=password,port=port,db=db) as conn:
    cursor=conn.cursor(buffered=True)
    cursor.execute("create table if not exists usercomp(complaintno varchar(10),issue varchar(1000),description varchar(2000),usermail varchar(100),response varchar(20))")
    cursor.execute("create table if not exists userdata(name varchar(50),email varchar(100),dob varchar(20),password varchar(30))")
    cursor.execute("create table if not exists adcomp(username varchar(100),password varchar(30))")
    cursor.execute("insert into  adcomp values('vamsi@gmail.com','vamsi')")
    conn.commit()
    cursor.close()
mydb=mysql.connector.connect(host=host,user=user,password=password,db=db)
cursor=mydb.cursor(buffered=True)




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
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select count(*) from userdata where email=%s and password=%s",(usermail,up))
        record=cursor.fetchone()[0]
        print(record)
        if record==1:
            session['loggedin']=True
            session['usermail']=usermail
            cursor.close()
            return redirect(url_for('userview'))
        
        
        else:
            flash('Invalid Username/Password')
            return render_template('login.html')
        
    return render_template('login.html')

@app.route('/userregistration',methods=['GET','POST'])
def userregistration():
    if request.method == 'POST':
        cursor=mydb.cursor(buffered=True)
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
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select complaintno,issue,description,response from usercomp where usermail=%s",(usermail))
    record=cursor.fetchall()
    if record:
        cursor.close()
        return render_template('user_view.html',value=record)
    return render_template('user_view.html')

cursor=mydb.cursor(buffered=True)
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
        cursor=mydb.cursor(buffered=True)
        
        cursor.execute("select email,name from userdata where email=%s",([data['usermail']]))
        emailrec=cursor.fetchone()
        if emailrec:
            result=cursor.execute("insert into usercomp values(%s,%s,%s,%s,%s)",[data['OTP'],data['subject'],data['body'],data['usermail'],data['response']])
            mydb.commit()
            cursor.close()
            return redirect(url_for('userview'))
        else:
            cursor.close()
            return render_template('complaint.html')
        
    return render_template('complaint.html')

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        un=request.form['email']
        up=request.form['password1']
        cursor=mydb.cursor(buffered=True)
        cursor.execute("insert into adcomp values('%s','%s')",(un,up))
        mydb.commit()
        return redirect(url_for('adminlogin'))
        '''cursor.execute("select count(*) from adcomp where username=%s and password=%s",(un,up))
        record=cursor.fetchone()[0]
        if record==1:
            session['loggedin']=True
            session['username']=un
            mydb.commit()
            cursor.close()
            return redirect(url_for('adminview'))
        
        else:
            flash('Invalid Username/Password')
            return render_template('admin_login.html')'''
    return render_template('admin_login.html')

@app.route('/adminview',methods=['GET','POST'])
def adminview():
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select * from usercomp")
    record=cursor.fetchall()
    #ab=cursor.execute("update usercomp set response=:s" ,(aa))
    mydb.commit()
    if record:
        cursor.close()
        return render_template('admin_view.html',value=record)
        
        
    return render_template('admin_view.html')


@app.route('/updatestatus',methods=['GET','POST'])
def updatestatus():
    if request.method == 'POST':
        aa=request.form['compno']
        ab=request.form['status']
        cno=[aa]
        cursor=mydb.cursor(buffered=True)
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
@app.route('/adminlogout')
def adminlogout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully logged out')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

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
