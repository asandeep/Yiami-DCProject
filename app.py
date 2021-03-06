import os

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from form import RegisterForm, LoginForm


app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'recipe_manager'
app.config["MONGO_URI"] = 'mongodb+srv://tokyo_ghoul:edna@myfirstcluster-uvyys.mongodb.net/recipe_manager?retryWrites=true&w=majority'
app.config['SECRET_KEY']=os.environ.get("SECRET_KEY")

# Set Randome Key
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


#All Recipes
all_recipes = mongo.db.recipes

#All Users
users=mongo.db.users


#Homepage

@app.route('/')
@app.route('/main')
def main():
    recipes = all_recipes.find()

    if 'user' in session:
        flash('Hello ' + session['user'] +'!')
        return render_template('main.html', username=session['user'], user_id=users['_id'])
    return render_template('main.html', recipes=recipes)    



#Show All Recipes

@app.route('/get_recipes')
def get_recipes():
    recipes = all_recipes.find()
    return render_template("recipes.html", recipes=recipes)

#Sort Recipes
@app.route('/sort_recipes', methods = ['GET','POST'])
def sort_recipes():
    if request.method == 'POST':
        recipes = all_recipes.find({ "$or": [ { "course": request.form["course"] }, { "category": request.form["category"] }] })
        print(request.form)
        return render_template('recipes.html', recipes=recipes)
    return render_template('recipes.html', recipes=recipes)

#Show Each Recipe
@app.route('/recipe/<recipe_id>')   
def recipe(recipe_id):
    recipes = all_recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template('eachRecipe.html', recipes=recipes)


#Sign In
@app.route('/logIn', methods=['POST','GET'])
def logIn():
    form = LoginForm()
    if form.validate_on_submit():
        loginUser = users.find_one({'username':request.form['username']})
        if loginUser and  check_password_hash(loginUser['password'], form.password.data):
            session['user'] = request.form['username']
            flash('Hello ' + session['user'] +'!')
            return redirect(url_for('get_recipes'))
        else:
           flash('Invalid username/password combination') 
    return render_template('signIn.html', form=form)   




# Sign Up
@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    form = RegisterForm()
    if form.validate_on_submit():
      users = mongo.db.users
      existingUser = users.find_one({'username': request.form['username']}) 
      if existingUser is None:
            pw_hash =  generate_password_hash(request.form['password'])
            users.insert_one({'username': request.form['username'], 'email': request.form['email'],'password': pw_hash })
            session['user'] = request.form['username']
            return redirect(url_for('main'))

      flash("Sorry username already exists!")
    return render_template('signUp.html', form=form)

#Log Out
@app.route('/logOut')
def logOut():
    session.pop('user')
    flash("Successfully logged out")
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)