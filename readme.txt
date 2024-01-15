
#### Instructions ####

# Files
 - requirements.txt: Depending python libs
 - app.py: Flask web app
 - models.py: SQLAlchemy data models
 - ingest_data.py: Helper script to ingest case data
 - orders.csv and inventory.csv: Case data

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ingest data
python3 ingest_data.py

# Start web application
flask run -h localhost -p 5001

# Test calls
curl "http://localhost:5001/inventory?per_page=4&sub_category=Boots&sort_by=order_count" | jq

curl -X PUT -H "Content-Type: application/json" -d '{"product_name": "New Product", "quantity": 100}' "http://localhost:5001/inventory/prod1566%23prod106041004115"

curl -X PUT -H "Content-Type: application/json" \
-d '[
      {"product_id": "prod1566#prod106041004115", "quantity": 150, "product_name": "Updated Product 1"},
      {"product_id": "prod3214#prod117021007065", "quantity": 200, "product_name": "Updated Product 2"}
    ]' \
"http://localhost:5001/inventory/bulk_update" | jq

