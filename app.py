from flask import Flask, render_template

#create an instance of flask
app = Flask(__name__)
app.debug = True

#create a route decorator
@app.route('/')
def index():
    return "<h1>hello12</h1>"

@app.route('/user/<name>')
def user(name):
    return render_template("user.html",user_name=name)

#create error handler for pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
     return render_template("404.html"), 404

#Invalid URL
@app.errorhandler(500)
def internal_server_error(e):
     return render_template("500.html"), 500