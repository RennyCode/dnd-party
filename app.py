from flask import Flask,render_template,redirect,request,flash,session,flash
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = os.urandom(100)
app.config["IMAGE_UPLOADS"] = "C:/Users/Renny/Desktop/coding/vscode/flask_dnd/static/img"

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "4armageddon4",
    database= "dndapp",
    auth_plugin='mysql_native_password'
)

mycursor = mydb.cursor()


@app.route('/')
def homePage():
    mycursor.execute("SELECT max(id) AS number FROM dndapp.users;")
    myresult0 = mycursor.fetchall()
    mycursor.execute("SELECT * FROM users ;")
    myresult1 = mycursor.fetchall()
    mycursor.execute("SELECT * FROM posts ORDER BY PublishDate;")
    myresult = mycursor.fetchall()     
    length= len(myresult)
    arr = []
    for i in range(0,length):
        resultList = list(myresult[i])
        arr.append(resultList[3].replace("/enter", "\n"))

    contentUpdated = ((myresult[0][0], myresult[0][1], myresult[0][2], arr[0], myresult[0][4]),)
    for i in range(1,length):
        contentUpdated = contentUpdated + ((myresult[i][0], myresult[i][1], myresult[i][2], arr[i], myresult[i][4]),)

    return render_template('home.html',users = myresult1 ,posts = contentUpdated , count = myresult0[0][0], len = length-1)

@app.route('/party-members')
def partyMembers():
    mycursor.execute("SELECT * FROM users WHERE userType='dm';")
    myresult1 = mycursor.fetchall()
    mycursor.execute("SELECT * FROM users WHERE userType='player';")
    myresult2 = mycursor.fetchall()
    return render_template('party-members.html' ,dms = myresult1 ,players = myresult2)



@app.route('/allPosts')
def allPosts():
    mycursor.execute("SELECT * FROM posts ORDER BY PublishDate; ;")
    myresult = mycursor.fetchall()
    length= len(myresult)
    arr = []
    for i in range(0,length):
        resultList = list(myresult[i])
        arr.append(resultList[3].replace("<br>", "\n"))

    contentUpdated = ((myresult[0][0], myresult[0][1], myresult[0][2], arr[0], myresult[0][4]),)
    for i in range(1,length):
        contentUpdated = contentUpdated + ((myresult[i][0], myresult[i][1], myresult[i][2], arr[i], myresult[i][4]),)
    
    return render_template('allPosts.html', posts = contentUpdated)  

@app.route('/login' ,methods=['GET','POST'])
def login():
    if request.method == 'POST':
        emailInput = request.form["emailInput"] 
        pswInput = request.form["pswInput"]
        
        mycursor.execute("SELECT * FROM users")
        myresult = mycursor.fetchall()

        userIndex = 0 
        emailFlag  = 0
        
        for user in myresult:
            if (emailInput == user[8]):
                emailFlag = 1
                if(pswInput ==  user[11]):
                    userIndex = user[0]

        if userIndex:
            session['logged_in'] = True
            session['loggedUser'] = myresult[userIndex-1]
            if  session['loggedUser'][2] == 'DM':
                session['type'] = False
            else:
                session['type'] = True

            return render_template('userProfile.html')

        elif emailFlag :
            flash("incorrect password, please try again")
        else:
            flash("No match found, please try again")
    
    return render_template('login.html')
    
    
@app.route('/userProfile')
def userProfile():
    return render_template('userProfile.html')    

@app.route('/changeUserDetails', methods=['GET','POST'])
def changeUserDetails():
    if request.method == 'POST':
        orgUserInfo = session.get('loggedUser', None)
        username = (request.form['username'],)
        email = (request.form['email'],)

        descrip = (request.form['descrip'],)
        psw = (request.form['password1'],)
        if orgUserInfo[2] != 'DM':
            charName = (request.form['charName'],)
            lvl = (request.form['lvl'],)
            charClass = (request.form['class'],)
            subClass = (request.form['subClass'],)
            hp = (request.form['hp'],)
            values = username + (orgUserInfo[2],) + charName +  lvl + charClass + subClass + hp + email  + descrip  + psw
            sql1 = "UPDATE users set userName = '"+ values[0] +"', userType = '"+ values[1] +"', chracterName = '"+ values[2] +"', characterLevel = '"+ values[3] +"', characterClass = '"+ values[4] +"', characterSubClass = '"+ values[5] +"', characterHP = '"+ values[6] +"', userEmail = '"+ values[7] +"', charDescription = '"+ values[8] +"', userPassword = '"+ values[9] +"' where id = "+str(orgUserInfo[0])+";"
           
        else:
            values = username + (orgUserInfo[2],) + email + descrip + psw     
            sql1 = "UPDATE users set userName = '"+ values[0] +"', userType = '"+ values[1] + "', userEmail = '"+ values[2] +"', charDescription = '"+ values[3] +"', userPassword = '"+ values[4] +"' where id = "+str(orgUserInfo[0])+";"
            print(values)
            print(sql1)
        mycursor.execute(sql1)
        mydb.commit()
            


        mycursor.execute("SELECT * FROM users WHERE id='"+str(orgUserInfo[0])+"';")
        myresult1 = mycursor.fetchall()
        session.pop("loggedUser", None)
        session['loggedUser'] = myresult1[0]

        return redirect('/userProfile') 

    else:
        return render_template('changeUserDetails.html')    

@app.route('/uploadPic', methods=['GET', 'POST'])
def uplaodPic():
    if request.method == 'POST':
        
        userinfo = session.get('loggedUser', None)
        session.pop("loggedUser", None)
        image = request.files["pic"]
        
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))

        os.remove(os.path.join(app.config["IMAGE_UPLOADS"],  userinfo[10]))

        imgName = str(image.filename)


        sql3 = "UPDATE `dndapp`.`users` SET `picLink` = '"+ imgName +"' WHERE (`userEmail` = '"+ userinfo[8] +"');"
        mycursor.execute(sql3)
        mydb.commit()

      

        updatedTuple = (userinfo[0], userinfo[1], userinfo[2], userinfo[3], userinfo[4], userinfo[5], userinfo[6], userinfo[7], userinfo[8], userinfo[9],  image.filename, userinfo[11])
        session["loggedUser"] = updatedTuple

        return render_template('userProfile.html') 

    else:
        return render_template('uploadPic.html') 

 

@app.route('/uploadPost',methods=['GET', 'POST'])
def uploadPost():
    if request.method == 'POST':
        userinfo = session.get('loggedUser', None)
        subject = (request.form['subject'],)
        content = (request.form['content'],)
        dateTimeObj = datetime.now()

        print(content[0])

        contentUpdated = (content[0].replace("\r", "<br>"),)


        mycursor.execute("SELECT * FROM posts")
        myresult = mycursor.fetchall()  
        idIs = str(len(myresult)+1)
  
        print(contentUpdated[0])

        values = (userinfo[1],) + subject + contentUpdated
        sql1 = "INSERT INTO posts (byWho, theSubject, content) VALUES(%s, %s, %s)"
        mycursor.execute(sql1, values)
        mydb.commit()
        sql2 = "UPDATE `dndapp`.`posts` SET `publishDate` = '"+  str(dateTimeObj) +"' WHERE (`content` = '"+ contentUpdated[0] +"');"
        mycursor.execute(sql2)
        mydb.commit()
        sql3 = "UPDATE `dndapp`.`posts` SET `serialID` = '"+ idIs +"' WHERE (`content` = '"+ contentUpdated[0] +"');"
        mycursor.execute(sql3)
        mydb.commit()

        return render_template('/userProfile.html')   
    else:
        return render_template('/uploadPost.html')     


    
@app.route('/log_out')
def log_out():
    session.clear()
    return redirect('/')  

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')    
 

@app.route('/getInfo1', methods=['GET','POST'])
def getInfo1():
    
    username = (request.form['username'],)

    mycursor.execute("SELECT * FROM users WHERE userName ='"+ username[0] +"';")
    nameExist = mycursor.fetchall()
    if nameExist:
        flash("User Name is taken, please choose a uniqe one")
        return render_template('/signUp.html')    
    email = (request.form['email'],)
    userType = (request.form['userType'],)
    descrip = (request.form['descrip'],)
    psw = (request.form['password1'],)

    infoArr1 = [username,userType,email,descrip,psw]

 
    if userType[0] !='DM':
        session['info']= infoArr1
        return render_template('/signUpPlayer.html')    
    else:
    
        # add DM to users database!!!!r
        mycursor.execute("SELECT * FROM users")
        myresult = mycursor.fetchall()
        idIs = str(len(myresult)+1)
        values = username + userType  + ('The DM',)+ ('',) + ('',) + ('',) + ('',) + email + descrip  + ('',) + psw

        sql1 = "INSERT INTO users (userName, userType, chracterName, characterLevel, characterClass, characterSubClass, characterHP, userEmail, charDescription, picLink, userPassword ) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s);"
        mycursor.execute(sql1, values)
        mydb.commit()
        sql2 = "UPDATE `dndapp`.`users` SET `id` = '"+ idIs +"' WHERE (`userName` = '"+ username[0] +"');"
        mycursor.execute(sql2)
        mydb.commit()


        return render_template('/signInDone.html')   

@app.route('/signUpPlayer' ,methods=['GET','POST'])
def signUpPlayer():
    userInfo = session.get('info', None)
    session.pop("info", None)
    charName = (request.form['charName'],)
    lvl = (request.form['lvl'],)
    charClass = (request.form['class'],)
    subClass = (request.form['subClass'],)
    hp = (request.form['hp'],)
 
 
     # save user data

    mycursor.execute("SELECT * FROM users")
    myresult = mycursor.fetchall()
    idIs = str(len(myresult)+1)
    values = userInfo[0] + userInfo[1]  + charName +  lvl + charClass + subClass + hp + userInfo[2]  + userInfo[3] + ("",) +userInfo[4]
  

    sql1 = "INSERT INTO users (userName, userType, chracterName, characterLevel, characterClass, characterSubClass, characterHP, userEmail, charDescription, picLink, userPassword ) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s);"
    mycursor.execute(sql1, values)
    mydb.commit()
    sql2 = "UPDATE `dndapp`.`users` SET `id` = '"+ idIs +"' WHERE (`userName` = '"+ userInfo[0][0] +"');"
    mycursor.execute(sql2)
    mydb.commit()

  
    return redirect('/signInDone')        

@app.route('/signInDone' ,methods=['GET','POST'])
def signInDone():
    return render_template('signInDone.html') 


@app.route('/postPage/<string:id>' ,methods=['GET','POST'])
def postPage(id):

    

    mycursor.execute("SELECT * FROM posts ORDER BY PublishDate; ;")
    myresult = mycursor.fetchall()
    print(myresult[4])
    print(myresult[4][3])
    # length= len(myresult)
    # arr = []
    # for i in range(0,length):
    #     resultList = list(myresult[i])
    #     arr.append(resultList[3].replace("\r", "<br/>"))

    # contentUpdated = ((myresult[0][0], myresult[0][1], myresult[0][2], arr[0], myresult[0][4]),)
    # for i in range(1,length):
    #     contentUpdated = contentUpdated + ((myresult[i][0], myresult[i][1], myresult[i][2], arr[i], myresult[i][4]),)


    # print(contentUpdated[4])
    # print(contentUpdated[4][3])
    

    return render_template('postPage.html', id=int(id)-1 ,postContent =myresult) 
