from flask import Flask, request, redirect,render_template,session,url_for,flash
import cx_Oracle

con = cx_Oracle.connect('vamsi/vamsi@localhost:1521/xe')
cursor=con.cursor()

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
def h1():
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        un=request.form['email']
        up=request.form['password1']
        result=cursor.execute("select * from adcomp where username=:s and password=:s",(un,up))
        record=result.fetchone()
        if record:
            session['loggedin']=True
            session['username']=record[0]
            return redirect(url_for('adminview'))
        con.commit()
    return render_template('admin_login.html')

@app.route('/adminview',methods=['GET','POST'])
def adminview():
    result=cursor.execute("select * from usercomp")
    record=cursor.fetchall()
    #ab=cursor.execute("update usercomp set response=:s" ,(aa))
    con.commit()
    if record:
        return render_template('admin_view.html',value=record)
        
        
    return render_template('admin_view.html')

@app.route('/updatestatus',methods=['GET','POST'])
def updatestatus():
    if request.method == 'POST':
        aa=request.form['compno']
        ab=request.form['status']
        result=cursor.execute("update usercomp set response=:s where complaintno=:s",(ab,aa))
        a=con.commit()
        return redirect(url_for('adminview'))
        
        
        
    return render_template('update_status.html')



if __name__ == '__main__':
    app.run(debug=True)
