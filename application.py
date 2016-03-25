from flask import Flask, render_template
from database import Base, Category, CatalogItems, Database

'''database setup'''
db = Database()

'''Start of Application'''

app = Flask(__name__)

@app.route("/")
def index():
	items = db.get_items()
	categories = db.get_categories()
	return render_template('index.html', items=items, categories=categories)

@app.route("/setup")
def setup():
	db.generate_categories()
	return 'Application Setup!'

if __name__ == "__main__":
	''' Run the web server on all external ports (we need this for the vagrant machine)
	and on port 8000. debugging for now is allowed so changes can be tested quickly
	and we can see any error messages.
	'''
	app.run(host='0.0.0.0', port=8000, debug=True)