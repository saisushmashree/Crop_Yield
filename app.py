from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

model = pickle.load(open("RFmodel.pkl", "rb"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username 
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

    
@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/prediction1')
def prediction1():
    return render_template('prediction1.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/modelaccuracy')
def modelaccuracy():
    return render_template('modelaccuracy.html')

@app.route('/dataset')
def dataset():
    return render_template('dataset.html')


@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('uname')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        user = User(email=email, password=password, username=username, fname=fname, lname=lname)
        db.session.add(user)
        db.session.commit()
        flash('user has been registered successfully','success')
        return redirect('/login')
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect('/prediction')
        else:
            flash('Invalid Credentials', 'warning')
            return redirect('/login')
    return render_template("login.html")


@app.route("/predict", methods = ["GET", "POST"])
def predict():
    if request.method == "POST":
        
        # Nitrogen
        nitrogen = float(request.form["nitrogen"])
        
        # Phosphorus
        phosphorus = float(request.form["phosphorus"])
        
        # Potassium
        potassium = float(request.form["potassium"])
        
        # Temperature
        temperature = float(request.form["temperature"])
        
        # Humidity Level
        humidity = float(request.form["humidity"])
        
        # PH level
        phLevel = float(request.form["ph-level"])
        
        # Rainfall
        rainfall = float(request.form["rainfall"])
        
        # Making predictions from the values:
        predictions = model.predict([[nitrogen, phosphorus, potassium, temperature, humidity, phLevel, rainfall]])
        
        output = predictions[0]
        finalOutput = output.capitalize()
        
        if (output == "rice" or output == "blackgram" or output == "pomegranate" or output == "papaya"
            or output == "cotton" or output == "orange" or output == "coffee" or output == "chickpea"
            or output == "mothbeans" or output == "pigeonpeas" or output == "jute" or output == "mungbeans"
            or output == "lentil" or output == "maize" or output == "apple"):
            cropStatement = finalOutput + " should be harvested. It's a Kharif crop, so it must be sown at the beginning of the rainy season e.g between April and May."
                            

        elif (output == "muskmelon" or output == "kidneybeans" or output == "coconut" or output == "grapes" or output == "banana"):
            cropStatement = finalOutput + " should be harvested. It's a Rabi crop, so it must be sown at the end of monsoon and beginning of winter season e.g between September and October."
            
        elif (output == "watermelon"):
            cropStatement = finalOutput + " should be harvested. It's a Zaid Crop, so it must be sown between the Kharif and rabi season i.e between March and June."
        
        elif (output == "mango"):
            cropStatement = finalOutput + " should be harvested. It's a cash crop and also perennial. So you can grow it anytime."
                
    return render_template('result.html', prediction_text=cropStatement)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8081, debug=True)
