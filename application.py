from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from database import Base, Category, CatalogItems, Database
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

'''database setup'''
db = Database()

'''Start of Application'''

app = Flask(__name__, static_url_path = "/images", static_folder = "images")

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Python Catalog"


@app.route("/")
@app.route("/catalog")
def index():
	'''The index path of the app to show all categories

	Returns:
      A rendered index view.
     '''
	items = db.get_items()
	categories = db.get_categories()
	return render_template('index.html', items=items, categories=categories)


@app.route("/catalog.json")
@app.route("/catalog/catalog.json")
def catalog_json():
	'''/catalog.json this will display all items as json data'''

	return db.get_items(True)

@app.route("/catalog/categories.json")
@app.route("/categories.json")
def categories_json():
	'''/categories.json this will display all categories as json data'''
	return db.get_categories(True)

@app.route("/add")
def add():
	'''The add path this shows logged in users the form to add items

	Returns:
      A rendered form view.
     '''
	if(get_user_id() == 0):
		flash('You must be logged in to add an item', 'error')
		return redirect(url_for("index"))
	categories = db.get_categories()
	return render_template('form.html', categories=categories, item=[])


@app.route("/create" , methods=['POST'])
def create():
	'''The path to handle all new item creations'''
	if session.get('token', None) != request.form['csrf_token']:
		flash('Incorrect token', 'error')
		return redirect(url_for("add"))

	if(get_user_id() == 0):
		flash('You must be logged in to add an item', 'error')
		return redirect(url_for("index"))

	if request.form['title'] == '':
		flash('The item must have a title', 'error')
		return redirect(url_for("add"))

	if request.method == 'POST':
		db.add_item(request, get_user_id())
		flash('The item ' + request.form['title'] + ' has been succesfully added.', 'success')
	
	return redirect(url_for("index"))

@app.route("/update" , methods=['POST'])
def update():
	'''The add to handle all update requests to items'''

	item = db.get_item(request.form['item_id'])

	if(get_user_id() == 0):
		flash('You must be logged in to update an item', 'error')
		return redirect(url_for("index"))

	if(get_user_id() != item.user_id):
		flash('You do not have permission to update this item', 'error')
		return redirect(url_for("index"))


	if request.form['title'] == '':
		flash('The item must have a title', 'error')
		return redirect(url_for('edit_item', category_name=item.category.category_name, category_id=item.category.category_id, item_title=item.item_title, item_id=item.item_id))

	if request.method == 'POST':
		db.update_item(request)
		flash('The item ' + request.form['title'] + ' has been succesfully updated.', 'success')
	
	return redirect(url_for("index"))


@app.route("/catalog/<category_name>-cat<int:category_id>")
def view_category(category_name, category_id):
	'''Route to show all items in a category using the catgory id to get the category encase the names are duplicated

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
	'''
	items = db.get_items_by_category_id(category_id)
	categories = db.get_categories()
	return render_template('index.html', items=items, categories=categories, category_id=category_id)


@app.route("/catalog/<category_name>-cat<int:category_id>/JSON")
def view_category_json(category_name, category_id):
	'''Shows all the items in a category as json

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
	'''
	return db.get_items_by_category_id(category_id, True)



@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>")
def view_item(category_name, category_id, item_title, item_id):
	'''Shows an item using the item id

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
      item_name:  the name of the item
      item_id:  the id of the item
	'''
	item = db.get_item(item_id)
	categories = db.get_categories()
	return render_template('item.html', categories=categories, item=item)

@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/JSON")
def view_item_json(category_name, category_id, item_title, item_id):
	'''Shows an item as json

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
      item_name:  the name of the item
      item_id:  the id of the item
	'''
	return db.get_item(item_id, True)


@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/edit")
def edit_item(category_name, category_id, item_title, item_id):
	'''Renders the item form to update an item

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
      item_name:  the name of the item
      item_id:  the id of the item
	'''
	item = db.get_item(item_id)
	categories = db.get_categories()
	return render_template('form.html', categories=categories, item=item)


@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/delete")
def delete_item(category_name, category_id, item_title, item_id):
	'''Handles a delete request to an item

	Args:
      category_name:  the name of the category
      category_id:  the id of the category
      item_name:  the name of the item
      item_id:  the id of the item
	'''
	item = db.get_item(item_id)

	if(get_user_id() != item.user_id):
		flash('You do not have permission to delete this item', 'error')
		return redirect(url_for("index"))

	db.delete_item(item_id)
	return redirect(url_for("index"))

@app.route("/setup")
def setup():
	'''Generates 10 categories and 10 items for who ever is logged in'''
	id = get_user_id()
	db.generate_data(id)
	return redirect(url_for("index"))

@app.route("/logout")
def logout():
	'''destroys the session data to log the user out'''
	session.clear()
	flash("You have been successfully logged out", 'success')
	return redirect(url_for("index"))

@app.route('/gconnect', methods=['POST'])
def gconnect():
	'''Handles the gplus login requests'''
    #check the token from google with the application token
	if request.args.get('state') != session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
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

	# check token
	google_plus_id = credentials.id_token['sub']
	if result['user_id'] != google_plus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

    # check the access for this app
		if result['issued_to'] != CLIENT_ID:
			response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = session.get('credentials')
	stored_google_plus_id = session.get('google_plus_id')
	if stored_credentials is not None and google_plus_id == stored_google_plus_id:
		response = make_response(json.dumps('Current user is already connected.'),
		                         200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# store user details in session
	session['credentials'] = credentials
	session['google_plus_id'] = google_plus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	session['username'] = data['name']
	#display message to the user that they have been logged in
	flash("You have been logged in as %s" % session['username'], 'success')
	return 'OK'


def generate_state():
	'''generates a random string to use for google plus'''
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
	                    for x in range(0,32))
	session['state'] = state
	return session['state']

def generate_token():
	'''Generates a random string to use with the forms'''
	token =  ''.join(random.choice(string.ascii_uppercase + string.digits)
	                    for x in range(0,32))
	session['token'] = token
	return session['token']

def get_user_id():
	'''gets the user id for the logged in user'''
	user_id = 0
	if(session.get('google_plus_id', None) is not None):
		user_id = session['google_plus_id']

	return user_id

def get_username():
	'''gets the username for the logged in user'''
	username = ''
	if(session['username'] != ''):
		username = session['username']

	return username


#global vars for our templates
app.jinja_env.globals['csrf_token'] = generate_token  
app.jinja_env.globals['STATE'] = generate_state
app.jinja_env.globals['google_plus_id'] = get_user_id
app.jinja_env.globals['google_plus_username'] = get_username


if __name__ == "__main__":
	''' Run the web server on all external ports (we need this for the vagrant machine)
	and on port 8000. debugging for now is allowed so changes can be tested quickly
	and we can see any error messages.
	'''
	app.secret_key = 'A0Zr98j/3yX T~XH--jmN]LWX/,?RT'
	app.run(host='0.0.0.0', port=8000)


