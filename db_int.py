from flask import *
import pymysql
import datetime
import jwt
from functools import wraps   
app=Flask(__name__)
app.config['SECRET_KEY']="koech"

userID=[]          
@app.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Please login to continue"})
@app.route('/register',methods=['POST'])
def register():
    fname=request.get_json()["Fname"]
    lname=request.get_json()["Lname"]
    email=request.get_json()["email"]
    username=request.get_json()["username"]
    password=request.get_json()["password"]
    timestamp=datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    try:
        connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql="INSERT INTO `users` (`Fname`, `Lname`, `Email`, `Username`, `Password`, `Timestamp`) VALUES ('"+fname+"', '"+lname+"', '"+email+"', '"+username+"','"+password+"', '"+timestamp+"');"
            try:
                cursor.execute("SELECT * FROM `users` WHERE `username` LIKE '"+username+"'")
                if cursor.fetchone() is not None:
                    return jsonify({"Alert":"User already Exists"})
                cursor.execute(sql)
            except:
                return jsonify({"message": "oops Register unsuccessful"})
        connection.commit()
    finally:
        connection.close()
    return jsonify({"message": "Register successful"})
@app.route('/login',methods=['POST'])
def login():
    username=request.get_json()["username"]
    password=request.get_json()["password"]
    userType=request.get_json()["userType"]
    rawtoken={}
    
    if userType=='admin':
        try:
            connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
            with connection.cursor() as cursor1:
                sql1="SELECT * FROM `admin` WHERE `Userame` LIKE '"+username+"' AND `Password` LIKE '"+password+"'"
                try:
                    cursor1.execute(sql1)
                    result = cursor1.fetchall()
                    for each in result:
                        rawtoken.update({"username":str(each[1]),"exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=5)})
                except:
                    return jsonify({"message": "oops unsuccessful"})
            connection.commit()
        finally:
            connection.close()
        if len(rawtoken)==0:
            return jsonify({"message":"you are not an admin"})            
        token=jwt.encode(rawtoken,app.config['SECRET_KEY'])    
        return jsonify({"Admintoken":token.decode('utf-8')})
        
    else:
        try:
            connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
            with connection.cursor() as cursor1:
                sql1="SELECT * FROM `users` WHERE `Username` LIKE '"+username+"' AND `Password` LIKE '"+password+"'"
                try:
                    cursor1.execute(sql1)
                    result = cursor1.fetchall()
                    for each in result:
                        rawtoken.update({"username":str(each[4]),"exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=5)})
                        userID.append(each[0])
                except:
                    return jsonify({"message": "oops unsuccessful"})      
            connection.commit()
        finally:
            connection.close()
    if len(rawtoken)==0:
        return jsonify({"message":"Invalid Credentials"})
    token=jwt.encode(rawtoken,app.config['SECRET_KEY'])        
    return jsonify({"token":token.decode('utf-8')})
def authorizeAdmin(t):
    @wraps(t)
    def decorated(*args,**kwargs):
        if request.args.get('Admintoken')=='':
            return jsonify({"Alert":'please login as admin'})
        try:
            jwt.decode(request.args.get('Admintoken'), app.config['SECRET_KEY'])
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
            jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
        except:
            return jsonify({"Alert":'please login again'})
        return f(*args,**kwargs)
    return decorated
@app.route('/post_comment',methods=['POST'])
@authorizeUser
def post_comment():
    comment=request.get_json()["comment"]
    timestamp=datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    writer=str(userID[len(userID)-1])
    try:
        connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql="INSERT INTO `comments` (`comment`, `Time`, `ID`) VALUES ('"+comment+"', '"+timestamp+"', "+writer+");"
            try:
                cursor.execute(sql)
            except:
                return jsonify({"message": "oops unsuccessful"})
        connection.commit()
    finally:
            connection.close()
    return jsonify({"message": "successful comments"})
@app.route('/view_comments',methods=['GET'])
@authorizeUser
def view_comments():
    output={}
    try:
        connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `comments` WHERE `ID` = "+str(userID[len(userID)-1])+";"
            try:
                cursor.execute(sql)
                result=cursor.fetchall()
                for each in result:
                    output.update({str(each[0]):str(each[1])})
            except:
                jsonify({"message": "oops unsuccessful"})
        connection.commit()
    finally:
        connection.close()
    return jsonify(output)
@app.route('/account',methods=['GET'])
@authorizeUser
def account():
    myID=''
    Name=''
    Email=''
    username=''
    try:
        connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE `ID` = "+str(userID[len(userID)-1])+""
            try:
                cursor.execute(sql)
                result=cursor.fetchall()
                for each in result:
                    myID+=str(each[0])
                    Name+=str(each[1])+' '+str(each[2])
                    Email+=str(each[3])
                    username+=str(each[4])
            except:
                return jsonify({"message": "oops unsuccessful"})
        connection.commit()
    finally:
        connection.close()
    return jsonify({"username":username,"Name":Name,"Email":Email,"userID":myID})
@app.route('/delete_comment/<int:commentID>',methods=['DELETE'])
@authorizeUser
def delete_comment(commentID):
    try:
        connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql="DELETE FROM `comments` WHERE `comments`.`commentID` = "+str(commentID)+" and `comments`.`ID`="+str(userID[len(userID)-1])+""
            
            try:
                cursor.execute("SELECT * FROM `comments` WHERE `commentID` LIKE "+str(commentID)+" and `ID` LIKE "+str(userID[len(userID)-1])+" ")
                result=cursor.fetchone()
                if result is None:
                    return jsonify({"Alert":"You are not Authorized to delete this comment"})
                else:               
                    cursor.execute(sql)
            except:
                return jsonify({"message": "oops unsuccessful,Either you are not authorized to delete or there is a problem with database connection"})
        connection.commit()
    finally:
        connection.close()
    return jsonify({"message": "successfully deleted,you cannot undo this"})
@app.route('/allcomments/<int:commentID>',methods=['DELETE'])
@authorizeAdmin
def delete_commentsByAdmin(commentID):
    try:
        connection=pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql="DELETE FROM `comments` WHERE `comments`.`commentID`="+str(commentID)+""
            try:
                cursor.execute(sql)
            except:
                return ({"message": "oops unsuccessful"})
        connection.commit()    
    finally:
        connection.close()           
    return jsonify({"message": "successful"})
@app.route('/view_all',methods=['GET'])
@authorizeAdmin
def view_commentsByAdmin():
    output={}
    try:
        connection=pymysql.connect(host='localhost',user='root',password='',db='andela')
        with connection.cursor() as cursor:
            sql="SELECT * FROM `comments`"
            try:
                cursor.execute(sql)
                result=cursor.fetchall()
                for each in result:
                    output.update({"commentID "+str(each[0]):{"userID "+str(each[3]):str(each[1])}})
            except:
                return ({"message": "oops unsuccessful"})
        connection.commit()
    finally:
        connection.close()
    return jsonify(output)    
  
if __name__=='__main__':
    app.run(port=5566,debug=True)    