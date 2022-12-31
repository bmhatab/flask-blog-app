from flask import Flask, render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

#create an instance of flask
app = Flask(__name__)
app.debug = True

#creating an ENV variable for WTForms CSRF token for encryption
app.config['SECRET_KEY']="secret"   #private key to be hidden



class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")






#----------------------------------------------------------------------------------------------------
#create a route decorator
@app.route('/')
def index():
    return render_template("index.html",name="Home")

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

#create a Form Class
# Creating a class for the user form
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
