from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import Base, Category, CatalogItems, Database

'''database setup'''
db = Database()

'''Start of Application'''

app = Flask(__name__, static_url_path = "/images", static_folder = "images")

@app.route("/")
@app.route("/catalog")
def index():
	items = db.get_items()
	categories = db.get_categories()
	return render_template('index.html', items=items, categories=categories)

@app.route("/catalog.json")
@app.route("/catalog/catalog.json")
def catalog_json():

	return db.get_items(True)

@app.route("/catalog/categories.json")
@app.route("/categories.json")
def categories_json():

	return db.get_categories(True)

@app.route("/add")
def add():
	categories = db.get_categories()
	return render_template('form.html', categories=categories, item=[])

@app.route("/create" , methods=['POST'])
def create():
	if request.form['title'] == '':
		flash('The item must have a title', 'error')
		return redirect(url_for("add"))

	if request.method == 'POST':
		db.add_item(request)
		flash('The item ' + request.form['title'] + ' has been succesfully added.', 'success')
	
	return redirect(url_for("index"))

@app.route("/update" , methods=['POST'])
def update():
	if request.form['title'] == '':
		flash('The item must have a title', 'error')
		item = db.get_item(request.form['item_id'])
		return redirect(url_for('edit_item', category_name=item.category.category_name, category_id=item.category.category_id, item_title=item.item_title, item_id=item.item_id))

	if request.method == 'POST':
		db.update_item(request)
		flash('The item ' + request.form['title'] + ' has been succesfully updated.', 'success')
	
	return redirect(url_for("index"))

@app.route("/catalog/<category_name>-cat<int:category_id>")
def view_category(category_name, category_id):
	items = db.get_items_by_category_id(category_id)
	categories = db.get_categories()
	return render_template('index.html', items=items, categories=categories, category_id=category_id)

@app.route("/catalog/<category_name>-cat<int:category_id>/JSON")
def view_category_json(category_name, category_id):
	return db.get_items_by_category_id(category_id, True)

@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>")
def view_item(category_name, category_id, item_title, item_id):
	item = db.get_item(item_id)
	categories = db.get_categories()
	return render_template('item.html', categories=categories, item=item)

@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/JSON")
def view_item_json(category_name, category_id, item_title, item_id):
	return db.get_item(item_id, True)

@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/edit")
def edit_item(category_name, category_id, item_title, item_id):
	item = db.get_item(item_id)
	categories = db.get_categories()
	return render_template('form.html', categories=categories, item=item)

@app.route("/catalog/<category_name>-cat<int:category_id>/<item_title>-item<int:item_id>/delete")
def delete_item(category_name, category_id, item_title, item_id):
	db.delete_item(item_id)
	return redirect(url_for("index"))


@app.route("/setup")
def setup():
	db.generate_categories()
	return redirect(url_for("index"))


if __name__ == "__main__":
	''' Run the web server on all external ports (we need this for the vagrant machine)
	and on port 8000. debugging for now is allowed so changes can be tested quickly
	and we can see any error messages.
	'''
	app.secret_key = 'A0Zr98j/3yX T~XH--jmN]LWX/,?RT'
	app.run(host='0.0.0.0', port=8000, debug=True)