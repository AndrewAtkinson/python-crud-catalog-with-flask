import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from faker import Faker #sudo pip install fake-factory

Base = declarative_base()

class Category(Base):
	__tablename__ = 'categories' 

	category_id = Column(Integer, primary_key=True)
	category_name = Column(String(250), nullable=False)


class CatalogItems(Base):
	__tablename__ = 'catalog_items' 

	item_id = Column(Integer, primary_key=True)
	item_title = Column(String(250), nullable=False)
	item_description = Column(Text)
	item_image = Column(String(250))
	category_id = Column(Integer, ForeignKey('categories.category_id'))
	category = relationship(Category)


class Database:
	def __init__(self):
		engine = create_engine('sqlite:///catalog.db')
		Base.metadata.create_all(engine)
		db_session = sessionmaker(bind=engine)
		self.db = db_session()

	def get_items(self):
		return self.db.query(CatalogItems).all()

	def add_item(self, request):
		item = CatalogItems(
			item_title = request.form['title'],
			item_description = request.form['description'],
			category_id = request.form['category_id']
			)
		self.db.add(item)
		self.db.commit()


	def get_categories(self):
		return self.db.query(Category).all()

	def generate_categories(self):
		fake = Faker()
		for _ in range(0,10):
			category = Category(category_name = fake.word())
			self.db.add(category)
			print(category.category_name)

		self.db.commit()