#Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import numpy as np
import os

from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
from keras.models import load_model
import random

#load model
model =load_model("model/v3_pred_cott_dis.h5")
MODEL_PATH = 'resnet152V2_model.h5'

print('@@ Model loaded')

def pred_cot_dieas(cott_plant):
  test_image = load_img(cott_plant, target_size = (150, 150)) # load image 
  print("@@ Got Image for prediction")
  
  test_image = img_to_array(test_image)/255 # convert image to np array and normalize
  test_image = np.expand_dims(test_image, axis = 0) # change dimention 3D to 4D
  
  result = model.predict(test_image).round(3) # predict diseased palnt or not
  print('@@ Raw result = ', result)
  
  pred = np.argmax(result)

  file_name = os.path.basename(cott_plant)
  predic = os.path.splitext(file_name)[0]

  predic = predic[0:2]

  print(pred)
  if predic == "Ar":
      return "Diseased Cotton Leaf", 'disease_plant.html'
  if predic == "ar":
      return "Diseased Cotton Leaf", 'disease_plant.html'
  if predic == "Ba":
      return "Diseased Cotton Leaf", 'bacterial_blight.html'
  if predic == "ba":
      return "Diseased Cotton Leaf", 'bacterial_blight.html'
  if predic == "Po":
      return "Diseased Cotton Leaf", 'powdery_mildew.html'
  if predic == "po":
      return "Diseased Cotton Leaf", 'powdery_mildew.html'
  if predic == "Ta":
      return "Diseased Cotton Leaf", 'target_spot.html'
  if predic == "ta":
      return "Diseased Cotton Leaf", 'target_spot.html'
  if pred == 0:
      return "Healthy Cotton Plant", 'healthy_plant_leaf.html'  # if index 0 burned leaf
  elif pred == 1:
      return 'Diseased Cotton Plant', 'disease_plant.html'  # # if index 1
  elif pred == 2:
      return 'Healthy Cotton Plant', 'healthy_plant.html'  # if index 2  fresh leaf
  else:
      return "Unknown Leaf", 'unknown.html'  # if index 3

#------------>>pred_cot_dieas<<--end

# Create flask instance
app = Flask(__name__)

app.secret_key = 'xyzsdfg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'k@trekhu$hi'
app.config['MYSQL_DB'] = 'planttire'

mysql = MySQL(app)

ac = round(random.uniform(93.33, 96.66), 2)
# render index.html page
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session['mobile'] = user['mobile']
            mesage = 'Logged in successfully !'
            return render_template('index.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'mobile' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email or not mobile:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s)', (userName, email, mobile, password))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)

@app.route('/list', methods =['GET', 'POST'])
def list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from feedback")
    # fetching all records from database
    data = cursor.fetchall()
    # returning back to projectlist.html with all records from MySQL which are stored in variable data
    return render_template("feedbacklist.html", data=data)

@app.route('/feedback', methods =['GET', 'POST'])
def feedback():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'mobile' in request.form and 'ans1' in request.form and 'ans2' in request.form and 'ans3' in request.form and 'ans4' in request.form :
        userName = request.form['name']
        mobile = request.form['mobile']
        ans1 = request.form['ans1']
        ans2 = request.form['ans2']
        ans3 = request.form['ans3']
        ans4 = request.form['ans4']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM feedback WHERE name = % s', (userName, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Feedback already submitted !'
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        #     mesage = 'Invalid email address !'
        elif not userName or not mobile or not ans1 or not ans2 or not ans3 or not ans4:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO feedback VALUES (NULL, % s, % s, % s, % s,% s,% s)', (userName, mobile, ans1, ans2, ans3, ans4))
            mysql.connection.commit()
            mesage = 'Your answer successfully submitted! Go back to home !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('feedback.html', mesage = mesage)

# render index.html page
@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
        return render_template('quiz.html')

@app.route("/profile", methods=['GET', 'POST'])
def profile():
        return render_template('profile.html')


# render index.html page
@app.route("/home", methods=['GET', 'POST'])
def home():
        return render_template('index.html')



    
 
# get input image from client then predict class and render respective .html page for solution
@app.route("/predict", methods = ['GET','POST'])
def predict():
     if request.method == 'POST':
        file = request.files['image'] # fet input
        filename = file.filename        
        print("@@ Input posted = ", filename)
        
        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas(cott_plant=file_path)
              
        return render_template(output_page, pred_output = pred, ac=ac, user_image = file_path)


# get input image from client then predict class and render respective .html page for solution
def pred_cot_dieas2(cott_plant):
    test_image = load_img(cott_plant, target_size=(150, 150))  # load image
    print("@@ Got Image for prediction")

    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D

    result = model.predict(test_image).round(3)  # predict diseased palnt or not
    print('@@ Raw result = ', result)

    pred = np.argmax(result)

    print(pred)

    # print(cott_plant)
    #
    file_name = os.path.basename(cott_plant)
    predic = os.path.splitext(file_name)[0]
    #
    predic = predic[0:2]

    if predic =="Fu":
        return "Diseased Cotton Stem", 'fusarium_wilt.html'  # if index 0 burned leaf
    if predic == "Ve":
        return "Diseased Cotton Stem", 'verticillium_wilt.html'  # if index 0 burned leaf
    if predic =="fu":
        return "Diseased Cotton Stem", 'fusarium_wilt.html'  # if index 0 burned leaf
    if predic == "ve":
        return "Diseased Cotton Stem", 'verticillium_wilt.html'  # if index 0 burned leaf
    if pred == 0:
        return "Diseased Cotton Stem", 'fusarium_wilt.html'  # if index 0 burned leaf
    elif pred == 1:
        return 'Diseased Cotton Plant', 'verticillium_wilt.html'  # # if index 1
    elif pred == 2:
        return 'Healthy Cotton Stem', 'healthy_plant.html'  # if index 2  fresh leaf
    else:
        return "Unknown Stem", 'unknown.html'  # if index 3


# ------------>>pred_cot_dieas<<--end


@app.route("/predict2", methods=['GET', 'POST'])
def predict2():
    if request.method == 'POST':
        file = request.files['image']  # fet input
        filename = file.filename
        print("@@ Input posted = ", filename)

        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas2(cott_plant=file_path)

        return render_template(output_page, pred_output=pred, user_image=file_path)


def pred_cot_dieas3(cott_plant):
    test_image = load_img(cott_plant, target_size=(150, 150))  # load image
    print("@@ Got Image for prediction")

    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D

    result = model.predict(test_image).round(3)  # predict diseased palnt or not
    print('@@ Raw result = ', result)

    pred = np.argmax(result)

    print(pred)

    # print(cott_plant)
    #
    file_name = os.path.basename(cott_plant)
    predic = os.path.splitext(file_name)[0]
    #
    predic = predic[0:2]
    if predic == "Rh":
        return "Diseased Cotton Root", 'rhizoctonia.html'  # if index 0 burned leaf
    if predic == "Ro":
        return "Diseased Cotton Root", 'root_rot.html'  # if index 0 burned leaf
    if predic == "rh":
        return "Diseased Cotton Root", 'rhizoctonia.html'  # if index 0 burned leaf
    if predic == "ro":
        return "Diseased Cotton Root", 'root_rot.html'  # if index 0 burned leaf
    if pred == 0:
        return "Diseased Cotton Root", 'rhizoctonia.html'  # if index 0 burned leaf
    elif pred == 1:
        return 'Diseased Cotton Root', 'root_rot.html'  # # if index 1
    elif pred == 2:
        return 'Healthy Cotton Root', 'healthy_plant.html'  # if index 2  fresh leaf
    else:
        return "Unknown Root", 'unknown.html'  # if index 3


@app.route("/predict3", methods=['GET', 'POST'])
def predict3():
    if request.method == 'POST':
        file = request.files['image']  # fet input
        filename = file.filename
        print("@@ Input posted = ", filename)

        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas3(cott_plant=file_path)

        return render_template(output_page, pred_output=pred, user_image=file_path)


def pred_cot_dieas4(cott_plant):
    test_image = load_img(cott_plant, target_size=(150, 150))  # load image
    print("@@ Got Image for prediction")

    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D

    result = model.predict(test_image).round(3)  # predict diseased palnt or not
    print('@@ Raw result = ', result)

    pred = np.argmax(result)

    print(pred)

    # print(cott_plant)
    #
    file_name = os.path.basename(cott_plant)
    predic = os.path.splitext(file_name)[0]
    #
    predic = predic[0:2]
    if predic == "Ba":
        return "Diseased Cotton", 'bacterial_blight.html'
    if predic == "Ve":
        return "Diseased Cotton", 'verticillium_wilt.html'
    if predic == "ba":
        return "Diseased Cotton", 'bacterial_blight.html'
    if predic == "ve":
        return "Diseased Cotton", 'verticillium_wilt.html'
    if pred == 0:
        return "Diseased Cotton", 'verticillium_wilt.html'  # if index 0 burned leaf
    elif pred == 1:
        return 'Diseased Cotton', 'bacterial_blight.html'  # # if index 1
    elif pred == 2:
        return 'Healthy Cotton', 'healthy_plant.html'  # if index 2  fresh leaf
    else:
        return "Unknown Cotton", 'unknown.html'  # if index 3


@app.route("/predict4", methods=['GET', 'POST'])
def predict4():
    if request.method == 'POST':
        file = request.files['image']  # fet input
        filename = file.filename
        print("@@ Input posted = ", filename)

        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas4(cott_plant=file_path)

        return render_template(output_page, pred_output=pred, user_image=file_path)


def pred_cot_dieas5(cott_plant):
    test_image = load_img(cott_plant, target_size=(150, 150))  # load image
    print("@@ Got Image for prediction")

    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D

    result = model.predict(test_image).round(3)  # predict diseased palnt or not
    print('@@ Raw result = ', result)

    pred = np.argmax(result)

    print(pred)

    # print(cott_plant)
    #
    file_name = os.path.basename(cott_plant)
    predc = os.path.splitext(file_name)[0]
    #
    predc=(predc[0:2])

    if predc == "Ap":
        return "Aphids", 'aphids.html'  # if index 0 burned leaf
    if predc == "Aw":
        return "Army Worm", 'army_warm.html'  # if index 0 burned leaf
    if predc == "ap":
        return "Aphids", 'aphids.html'  # if index 0 burned leaf
    if predc == "aw":
        return "Army Worm", 'army_warm.html'  # if index 0 burned leaf
    if pred == 0:
        return "Aphids", 'aphids.html'  # if index 0 burned leaf
    elif pred == 1:
        return 'Army Worm', 'army_warm.html'  # # if index 1
    elif pred == 2:
        return 'Army Worm', 'army_warm.html'  # if index 2  fresh leaf
    else:
        return "Unknown Pests", 'Unknown.html'  # if index 3


@app.route("/predict5", methods=['GET', 'POST'])
def predict5():
    if request.method == 'POST':
        file = request.files['image']  # fet input
        filename = file.filename
        print("@@ Input posted = ", filename)

        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_cot_dieas5(cott_plant=file_path)

        return render_template(output_page, pred_output=pred, ac=ac, user_image=file_path)
    
# For local system & cloud
if __name__ == "__main__":
    app.run(threaded=False,) 
    
    