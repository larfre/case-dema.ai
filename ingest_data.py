import logging
import csv
from datetime import datetime
from app import app, db
from models import Inventory, Order

# Configure logging
logging.basicConfig(filename='data_ingestion.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def parse_date(date_string):
    # There are two different time formats in the data, so this function is used to handle either
    for fmt in ('%Y-%m-%dT%H:%MZ', '%Y-%m-%dT%H:%M:%SZ'):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError(f'No valid date format found for {date_string}')

def add_inventory_data():
    with open('inventory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                item = Inventory(
                    product_id=row['productId'],
                    product_name=row['name'],
                    quantity=int(row['quantity']),
                    category=row['category'],
                    sub_category=row['subCategory']
                )
                db.session.add(item)
            except Exception as e:
                # Log the error and the row that caused it
                logging.error(f"Error adding inventory: {e}. Row: {row}")
    db.session.commit()

def add_orders_data():
    with open('orders.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                order = Order(
                    order_id=row['orderId'],
                    product_id=row['productId'],
                    currency=row['currency'],
                    quantity=int(row['quantity']),
                    shipping_cost=float(row['shippingCost']),
                    amount=float(row['amount']),
                    channel=row['channel'],
                    channel_group=row['channelGroup'],
                    campaign=row['campaign'],
                    date_time=parse_date(row['dateTime'])
                )
                db.session.add(order)
            except Exception as e:
                # Log the error and the row that caused it
                logging.error(f"Error adding order: {e}. Row: {row}")
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create database tables
        add_inventory_data() # Add inventory data
        add_orders_data() # Add orders data

