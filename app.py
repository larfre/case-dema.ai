# app.py
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from models import db, Inventory, Order
from sqlalchemy.sql import func
from sqlalchemy import text

# Configure logging
logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/inventory', methods=['GET'])
def list_inventory():
    try:
        # Retrieve query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', type=str)
        sub_category = request.args.get('sub_category', type=str)
        only_in_stock = request.args.get('only_in_stock', 'false', type=str).lower() == 'true'
        sort_by = request.args.get('sort_by', type=str)  # Default sorting by quantity

        # Constructing the base query by joining Inventory with Order table, and count orders for each inventory item
        query = Inventory.query.outerjoin(Order).group_by(Inventory.product_id).add_columns(
            func.count(Order.id).label('order_count')
        )
    
        # Apply filtering
        if category:
            query = query.filter(Inventory.category == category)
        if sub_category:
            query = query.filter(Inventory.sub_category == sub_category)
        if only_in_stock:
            query = query.filter(Inventory.quantity > 0)

        # Apply sorting
        if sort_by == 'quantity':
            query = query.order_by(Inventory.quantity)
        elif sort_by == 'order_count':
            query = query.order_by('order_count')

        # Pagination implementation
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        inventories = pagination.items

        # Preparing the response
        inventory_list = []
        for inventory, order_count in inventories:
            orders = [{'order_id': order.order_id, 
                    'currency': order.currency, 
                    'quantity': order.quantity, 
                    'shipping_cost': order.shipping_cost, 
                    'amount': order.amount, 
                    'channel': order.channel, 
                    'channel_group': order.channel_group, 
                    'campaign': order.campaign, 
                    'date_time': order.date_time
                    } for order in inventory.orders]

            inventory_list.append({
                'product_id': inventory.product_id,
                'product_name': inventory.product_name,
                'quantity': inventory.quantity,
                'category': inventory.category,
                'sub_category': inventory.sub_category,
                'orders': orders,
                'order_count': order_count  # Extracted from the tuple
            })

        return jsonify(inventory_list)

    except Exception as e:
        # Logging any exceptions
        logging.error(f"API error in list_inventory: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/inventory/<string:product_id>', methods=['PUT'])
def update_inventory(product_id):
    try:
        data = request.json

        # Retrieve the inventory item by product_id, or return 404 if not found
        inventory = Inventory.query.get_or_404(product_id)
    
        # Updating inventory item properties with provided data
        inventory.product_name = data.get('product_name', inventory.product_name)
        inventory.quantity = data.get('quantity', inventory.quantity)
        inventory.category = data.get('category', inventory.category)
        inventory.sub_category = data.get('sub_category', inventory.sub_category)
        db.session.commit()

        # Preparing the response, including associated orders
        orders = [{'order_id': order.order_id, 
                    'currency': order.currency, 
                    'quantity': order.quantity, 
                    'shipping_cost': order.shipping_cost, 
                    'amount': order.amount, 
                    'channel': order.channel, 
                    'channel_group': order.channel_group, 
                    'campaign': order.campaign, 
                    'date_time': order.date_time
                    } for order in inventory.orders]

        return jsonify({
            'product_id': inventory.product_id, 
            'product_name': inventory.product_name, 
            'quantity': inventory.quantity, 
            'category': inventory.category, 
            'sub_category': inventory.sub_category,
            'orders': orders
        })
    except Exception as e:
        # Logging any exceptions
        logging.error(f"API error in update_inventory: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/inventory/bulk_update', methods=['PUT'])
def bulk_update_inventory():
    try:
        data = request.json
        succesful_product_ids = []
        unsuccesful_product_ids = []
        for item in data:
            # Attempt to update each inventory item
            inventory = Inventory.query.get(item['product_id'])
            if inventory:
                inventory.product_name = item.get('product_name', inventory.product_name)
                inventory.quantity = item.get('quantity', inventory.quantity)
                inventory.category = item.get('category', inventory.category)
                inventory.sub_category = item.get('sub_category', inventory.sub_category)
                db.session.commit()
                succesful_product_ids.append(item['product_id'])
            else:
                unsuccesful_product_ids.append(item['product_id'])
        return jsonify({'message': 'Bulk update complete', 'successful updates': succesful_product_ids, 'unsuccessful updates': unsuccesful_product_ids})
    except Exception as e:
        # Logging any exceptions
        logging.error(f"API error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

with app.app_context():
    db.create_all()   # Create database tables

if __name__ == '__main__':
    app.run(debug=True)
