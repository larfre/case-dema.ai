# models.py
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy for database interactions
db = SQLAlchemy()

class Inventory(db.Model):
    # Define the Inventory model with its fields and relationships
    product_id = db.Column(db.String, primary_key=True)
    product_name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    sub_category = db.Column(db.String, nullable=False)
    
    # Relationship with Order model. Each inventory item can have multiple orders.
    orders = db.relationship('Order', backref='product', lazy=True)

class Order(db.Model):
    # Define the Order model with its fields and relationships
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False)
    product_id = db.Column(db.String, db.ForeignKey('inventory.product_id'), nullable=False)
    currency = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    channel = db.Column(db.String, nullable=False)
    channel_group = db.Column(db.String, nullable=False)
    campaign = db.Column(db.String, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

