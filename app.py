from flask import Flask, render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import Form,StringField,SubmitField,PasswordField,ValidationError
from wtforms.validators import DataRequired,EqualTo,Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user


#----------------------------------------------------------------------------------------------------
#create an instance of flask
app = Flask(__name__)
app.debug = True
#creating an ENV variable for WTForms CSRF token for encryption
app.config['SECRET_KEY']="secret"   #private key to be hidden
#Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Initialize database
db = SQLAlchemy(app)
# Using flask-migrate Migrate
migrate = Migrate(app=app,db=db)
#turn it on in terminal with 
# db.init_app(app=app)
#----------------------------------------------------------------------------------------------------

#Login components
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# create database model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # password work stuff
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='poster') #name to use for referencing

    @property
    def password(self):
        raise AttributeError('Password does not have a read attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash

    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)


    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name 

#Instance a new database table "once" from python interpreter 
#Type "python" in terminal
#>> from app import db,app
#>> db.init_app(app=app)
#>> with app.app_context():
#....   db.create_all()  
#>> exit()

# Creating a Blog post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255)) # An alias for the url
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

#----------------------------------------------------------------------------------------------------
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Name : ", validators=[DataRequired()])
    email = StringField("Email : ", validators=[DataRequired()])
    submit = SubmitField("Submit")
    password_hash = PasswordField("Password : ", validators=[DataRequired(),EqualTo('password_hash_v',message="Passwords must match!")])
    password_hash_v = PasswordField("Confirm Password : ", validators=[DataRequired()])

    
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField()




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

@app.route('/login',methods=['GET','POST']) #post method needed for page containing forms
def login():
    form = LoginForm()
    #validating form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # checking the hash
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('dashboard'))
                
            else:
                flash("Wrong password -- Try again")
        else:
            flash("That user doesn't exist -- Try again")
    
    else:
        return render_template("login.html",form=form)

@app.route('/dashboard', methods=["GET","POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You are logged out!")
    return render_template("index.html")



@app.route('/add-post', methods = ['POST','GET'])
@login_required
def add_post():
    post = None
    content = None
    slug = None
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
        content = form.content.data,
        poster_id = poster,
        slug = form.slug.data,
        )
        form.title.data = ''
        form.content.data = ''
       # form.author.data = ''
        form.slug.data = ''
# Add Log post to database 
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Sucessfully")
        return render_template("add_post.html",form=form,post=post,content=content,slug=slug)
    else:
        return render_template("add_post.html",form=form,post=post,content=content,slug=slug)
        
   
@app.route('/posts')
@login_required
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)

@app.route('/post/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Blog post was deleted")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)

    
    
    except:
        flash("There was a problem deleting post..try again")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)


@app.route('/post/edit/<int:id>', methods = ["GET","POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
       # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
   # form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)




@app.route('/user/add', methods =['GET','POST'])
def add_user(): 
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash password first
            hash_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data,email=form.email.data,password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User Added Sucessfully")
    #To display user names on the page 
    our_users = Users.query.order_by(Users.date_added)   
    return render_template('add_user.html',form=form,name=name,our_users=our_users)

#update database
@app.route('/update/<int:id>', methods =['GET','POST'])
@login_required
def update(id):
    name_to_update = Users.query.get_or_404(id)
    form = UserForm()
    form.name.data = name_to_update.name
    form.email.data = name_to_update.email
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # Hash password first
            hash_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data,email=form.email.data,password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User Added Sucessfully")
    #To display user names on the page 
    our_users = Users.query.order_by(Users.date_added)   
    return render_template('update.html',form=form,our_users=our_users,name_to_update=name_to_update)


@app.route('/delete/<int:id>', methods =['GET','POST'])
@login_required
def delete(id):
    user = db.session.query(Users).get(id)
    form = UserForm(request.form)
    if request.method == "GET":
        db.session.delete(user)
        db.session.commit()
        flash("User Deleted Sucessfully")
        return render_template("add_user.html",form=form,user=user)
    
    else:
        return render_template("add_user.html",form=form,user=user)


  
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

