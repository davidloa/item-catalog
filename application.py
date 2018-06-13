from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify, make_response
from flask import session as login_session
from functools import wraps
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests
import httplib2
import json
import random
import string

app = Flask(__name__)

# GConnect CLIENT_ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalop App"


# Connect to database and create database session
engine = create_engine(
            'sqlite:///catalogapp.db',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login section
# Store it in the session for later validation
# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# google sign in connection
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gathers data from Google Sign In API and places it inside
    a session variable.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# if user ID is passed into this method, it returns user object associated
# with this ID number
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# passed in email address and return an ID number that email add belongs to
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# log in is required before accessing additional features
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # redirect to home page after logout
        response = redirect(url_for('showCatalog'))
        flash("You have logged out.")
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# initial page when user starts the page by typing
# http://localhost:5000 or http://localhost:5000/catalog/
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id))
    return render_template('catalog.html',
                           categories=categories,
                           items=items)


# Items are displayed based on category
# e.g. http://localhost/catalog/category/1/
# user is able to view specific category items after click on each category
@app.route('/catalog/category/<int:category_id>/')
def categoryList(category_id):
    # select category based on category id
    category = session.query(Category).filter_by(id=category_id).one()
    # select all categories
    categories = session.query(Category).order_by(asc(Category.name))
    # select items based on category id
    items = session.query(CategoryItem).filter_by(category_id=category_id)\
        .order_by(desc(CategoryItem.id))
    # count all items in specific category
    countItems = session.query(CategoryItem)\
        .filter_by(category_id=category_id).count()
    return render_template('category.html',
                           countItems=countItems,
                           category=category,
                           categories=categories,
                           items=items)


# Display the item in detailed
# e.g. http://localhost/catalog/category/1/item/1/
# after user click on item, the full detailed will be displayed
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/')
def itemDisplay(category_id, item_id):
    # select category item based on item id
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('item.html',
                           category_id=category_id,
                           item_id=item_id,
                           item=item)


# add the item into selected category
# e.g. http://localhost:5000/catalog/category/item/new/
@app.route('/catalog/category/item/new/', methods=['GET', 'POST'])
# user is only allowed to add new item after login
@login_required
def newCategoryItem():
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = CategoryItem(
            title=request.form['title'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New %s Item is successfully created' % (newItem.title))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newItem.html', categories=categories)


# edit category item
# e.g. http://localhost:5000/catalog/category/1/item/1/edit/
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/edit/',
           methods=['GET', 'POST'])
# user is only allowed to add new item after login
@login_required
def editCategoryItem(category_id, item_id):
    itemToEdit = session.query(CategoryItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    """
    Unauthorized user is not allowed to edit the item
    """
    if itemToEdit.user_id != login_session['user_id']:
        noOAuth = ''
        noOAuth += '<script>'
        noOAuth += 'function myFunction() {'
        noOAuth += 'alert("You are not authroized to edit this item. '
        noOAuth += 'Please create your own item in order to edit");'
        noOAuth += '}'
        noOAuth += '</script>'
        noOAuth += '<body onload="myFunction(); window.history.go(-1);">'
        return noOAuth
    # item submission for edit
    if request.method == 'POST':
        if request.form['title']:
            itemToEdit.title = request.form['title']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        flash('Category Item has been edited')
        return redirect(url_for('itemDisplay',
                                category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('editItem.html',
                               category_id=category.id,
                               item_id=item_id,
                               item=itemToEdit,
                               category=category)


# delete category item
# e.g. http://localhost:5000/catalog/category/1/item/1/delete/
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/delete/',
           methods=['GET', 'POST'])
# user is only allowed to add new item after login
@login_required
def deleteCategoryItem(category_id, item_id):
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    """
    Unauthorized user is not allowed to delete the item
    """
    if itemToDelete.user_id != login_session['user_id']:
        noOAuth = ''
        noOAuth += '<script>'
        noOAuth += 'function myFunction() {'
        noOAuth += 'alert("You are not authroized to delete this item. '
        noOAuth += 'Please create your own item in order to delete");'
        noOAuth += '}'
        noOAuth += '</script>'
        noOAuth += '<body onload="myFunction(); window.history.go(-1);">'
        return noOAuth
    # item submission for delete
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Category Item has been deleted')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html',
                               category_id=category.id,
                               item_id=item_id,
                               category=category,
                               item=itemToDelete)


# JSON APIs to view all Category & item Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    category_dict = [category.serialize for category in categories]
    # Convert list indices to integers not str
    for num in range(len(category_dict)):
        items = session.query(CategoryItem)\
                .filter_by(category_id=category_dict[num]["id"]).all()
        item_dict = [i.serialize for i in items]
        # if item is not empty
        if item_dict:
            category_dict[num]["Item"] = item_dict
    return jsonify(Category=category_dict)


# JSON APIs to view all Categories only
@app.route('/catalog/category/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# JSON APIs to view all items based on category selected
@app.route('/catalog/category/<int:category_id>/item/JSON')
def categoryItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem)\
        .filter_by(category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


# JSON APIs to view the selected item in detailed
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
