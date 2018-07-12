from flask import *
import psycopg2
import datetime
import jwt
from functools import wraps
app=Flask(__name__)
app.config['SECRET_KEY']="koech"

connection=psycopg2.connect(dbname='first', user='postgres', host='localhost', password='01071992',port="5432")
def createTables():
    cursor=connection.cursor()
    cursor.execute("CREATE TABLE admin(AdminID SERIAL PRIMARY KEY,Username VARCHAR NOT NULL,Password VARCHAR NOT NULL);")
    cursor.execute("CREATE TABLE comments (commentID SERIAL PRIMARY KEY,  comment TEXT NOT NULL,  Time TIMESTAMP default current_timestamp, ID INT NOT NULL);")
    cursor.execute("CREATE TABLE users  (ID SERIAL PRIMARY KEY, fname VARCHAR NOT NULL, lname VARCHAR NOT NULL, email VARCHAR NOT NULL,Username VARCHAR NOT NULL,password VARCHAR NOT NULL,  timestamp TIMESTAMP default current_timestamp);")
    cursor.execute("INSERT INTO admin (adminid,username,password) VALUES (1, 'admin', 'admin');")
    connection.commit()
    
@app.route('/',methods=['GET'])
def home():
    createTables()
    return jsonify({"message":"Please login to continue"})

@app.route('/register',methods=['POST'])
def register():
    fname=request.get_json()["fname"]
    lname=request.get_json()["lname"]
    email=request.get_json()["email"]
    username=request.get_json()["username"]
    password=request.get_json()["password"]
    sql="INSERT INTO users (fname,lname,email,username,password) VALUES ('"+fname+"','"+lname+"','"+email+"','"+username+"','"+password+"');"
    cursor=connection.cursor()
    
    cursor.execute("SELECT * from users WHERE username = '"+username+"'")
    if cursor.fetchone() is not None:
        return jsonify({"message":"User already exists"})
    cursor.execute(sql)
    connection.commit()
    return jsonify({"message": "Register successful"})

def authorizeAdmin(t):
    @wraps(t)
    def decorated(*args,**kwargs):
        if request.args.get('token')=='':
            return jsonify({"Alert":'Token is missing'})
        try:
            data=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
            
            if data['user']=='normal':
                return jsonify({"Alert":'Only admins can access this'})
        except:    
            return jsonify({"Alert":'please login again'})
        return t(*args,**kwargs)
    return decorated


def authorizeUser(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if request.args.get('token')=='':
            return jsonify({"Alert":'please login as user'})
        try:
            data=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
            if data['user']=='admin':
                return jsonify({"Alert":"utilize admin rights"})
           # userID.append(data['ID'])
        except:
            return jsonify({"Alert":'please login again'})
        return f(*args,**kwargs)
    return decorated


@app.route('/login',methods=['POST'])
def login():
    username=request.get_json()["username"]
    password=request.get_json()["password"]
    userType=request.get_json()["userType"]
    rawtoken={}
    cursor=connection.cursor()
    if userType=='admin':
        sql1="SELECT * FROM admin WHERE username = '"+username+"' AND password = '"+password+"';"
        cursor.execute(sql1)
        
        for each in cursor.fetchall():
            rawtoken.update({"user":"admin","username":str(each[1]),"exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=15)})
        
    else:
        sql="SELECT * FROM users WHERE username = '"+username+"' AND password = '"+password+"';"
        cursor.execute(sql)
        for each in cursor.fetchall():
            rawtoken.update({"userID":str(each[0]),"user":"user","username":str(each[1]),"exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=15)})
    connection.commit()    
    if len(rawtoken)==0:
        return jsonify({"message":"Invalid credentials"})
    token=jwt.encode(rawtoken,app.config['SECRET_KEY'])
    return jsonify({"token":token.decode('utf-8')})
            

@app.route('/post_comment',methods=['POST'])
@authorizeUser
def postComment():
    comment=request.get_json()["comment"]
    
    writer=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])['userID']
    cursor=connection.cursor()
    cursor.execute("INSERT INTO comments (comment,id) VALUES ('"+comment+"',"+writer+");")
    connection.commit()
    return jsonify({"message": "commenting successful"})

@app.route('/view_comments',methods=['GET'])
@authorizeUser
def view_comments():
    cursor=connection.cursor()
    output={}
    myID=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])['userID']
    cursor.execute("SELECT * FROM comments WHERE id = "+myID+";")
    result=cursor.fetchall()
    for each in result:
        output.update({str(each[0]):str(each[1])})
    connection.commit()    
    return jsonify(output)

@app.route('/account',methods=['GET','POST'])
@authorizeUser
def account():
    myID=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])['userID']
    Name=''
    Email=''
    username=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])['username']
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = "+myID+";")
    result=cursor.fetchall()
    for each in result:
        Name+=str(each[1])+' '+str(each[2])
        Email+=str(each[3])
        
    connection.commit()
    return jsonify({"username":username,"Name":Name,"Email":Email,"userID":myID})

@app.route('/delete_comment/<int:commentID>',methods=['DELETE'])
@authorizeUser
def delete_comment(commentID):
    myID=jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])['userID']
    cursor=connection.cursor()
    sql="DELETE FROM comments WHERE commentID = "+str(commentID)+" and ID="+myID+";"
    cursor.execute("SELECT * FROM comments WHERE commentID = "+str(commentID)+" and ID = "+myID+" ;")
    if cursor.fetchone() is None:
        return jsonify({"Alert":"You are not Authorized to delete this comment"})
    else:
        cursor.execute(sql)
    connection.commit()
    return jsonify({"message": "successfully deleted,you cannot undo this"})

@app.route('/allcomments/<int:commentID>',methods=['DELETE'])
@authorizeAdmin
def delete_commentsByAdmin(commentID):
    cursor = connection.cursor()
    sql="DELETE FROM comments WHERE commentID="+str(commentID)+";"
    cursor.execute(sql)
    connection.commit()
    return jsonify({"message": "successful"})

@app.route('/view_all',methods=['GET'])
@authorizeAdmin
def view_commentsByAdmin():
    output={}
    cursor=connection.cursor()
    sql="SELECT * FROM comments;"
    cursor.execute(sql)
    for each in cursor.fetchall():
        output.update({"commentID "+str(each[0]):{"userID "+str(each[3]):str(each[1])}})
    connection.commit()
    return jsonify(output)

if __name__=='__main__':
    app.run(port=5512,debug=True)    
    
    



    