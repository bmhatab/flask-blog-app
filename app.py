from flask import Flask, render_template,flash,request
from flask_wtf import FlaskForm
from wtforms import Form,StringField,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#create an instance of flask
app = Flask(__name__)
app.debug = True
#creating an ENV variable for WTForms CSRF token for encryption
app.config['SECRET_KEY']="secret"   #private key to be hidden
#Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Initialize database
db = SQLAlchemy(app)

# create database model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name 

#Instance a new database table once from python interpreter 
#Type "python" in terminal
#>> from app import db,app
#>> db.init_app(app=app)
#>> with app.app_context():
#....   db.create_all()  
#>> exit()
#



class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")



#create a Form Class
# Creating a class for the user form
class UserForm(FlaskForm):
    name = StringField("Name : ", validators=[DataRequired()])
    email = StringField("Email : ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UpdateForm(FlaskForm):
    name = StringField("Name : ", validators=[DataRequired()])
    email = StringField("Email : ", validators=[DataRequired()])
    submit = SubmitField("Submit")



#----------------------------------------------------------------------------------------------------
#create a route decorator
@app.route('/')
def index():
    return render_template("base_index.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html",user_name=name)

#create a name page
@app.route('/name',methods=['GET','POST']) #post method needed for page containing forms
def name():
    name = None
    form = NamerForm()
    #validating form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data =''
        flash("Form submitted successfully!")
        
    return render_template("name.html",name=name,form=form)


@app.route('/user/add', methods =['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data,email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Sucessfully")
    #To display user names on the page 
    our_users = Users.query.order_by(Users.date_added)   
    return render_template('add_user.html',form=form,name=name,our_users=our_users)

#update database
@app.route('/update/<int:id>', methods =['GET','POST'])
def update(id):
    user = db.session.query(Users).get(id)
    form = UpdateForm(request.form)
    if request.method == "POST" and form.validate():
        user.name = form.name.data
        user.email = form.email.data
        db.session.commit()
        flash("User Added Sucessfully")
        return render_template("update.html",form=form,user=user)
    
    else:
        return render_template("update.html",form=form,user=user)
    
  
    #user = db.get_or_404(Users, id)

#create error handler for pages
#----------------------------------------------------------------------------------------------------
#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
     return render_template("404.html"), 404

#Invalid URL
@app.errorhandler(500)
def internal_server_error(e):
     return render_template("500.html"), 500



#----------------------------------------------------------------------------------------------------

