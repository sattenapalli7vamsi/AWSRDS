from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text

# Flask app setup
app = Flask(__name__)

# RDS connection details
# DB_USERNAME = "your_rds_username"
# DB_PASSWORD = "your_rds_password"
# DB_HOST = "your_rds_endpoint"  # e.g., "your-instance-name.abc123xyz.us-east-1.rds.amazonaws.com"
# DB_PORT = "3306"
# DB_NAME = "your_database_name"

# SQLAlchemy engine for RDS connection
# engine = create_engine(f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
engine = create_engine("mysql+pymysql://admin:1210Vamsi@database-1.cpakmco2srxz.us-east-1.rds.amazonaws.com:3306/rds1")

# Route: Get all products
@app.route("/products", methods=["GET"])
def get_products():
    try:
        # Execute the query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM Products"))
            
            # Process rows correctly by using positional access (tuples)
            products = []
            for row in result:
                products.append({
                    "ProductID": row[0],   # Index-based access
                    "Name": row[1],
                    "Category": row[2],
                    "Price": row[3],
                    "StockQuantity": row[4]
                })
        
        return jsonify(products)  # Convert to JSON and return
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route: Add a new product
@app.route("/products", methods=["POST"])
def add_product():
    try:
        # Get JSON data from the request
        data = request.get_json()
        name = data["name"]
        category = data["category"]
        price = data["price"]
        stock_quantity = data["stock_quantity"]
        
        # Insert the product into the database
        query = text("""
            INSERT INTO Products (Name, Category, Price, StockQuantity)
            VALUES (:name, :category, :price, :stock_quantity)
        """)
        
        # Use connection and commit changes
        with engine.connect() as connection:
            transaction = connection.begin()  # Start a transaction
            connection.execute(query, {
                "name": name,
                "category": category,
                "price": price,
                "stock_quantity": stock_quantity
            })
            transaction.commit()  # Commit the transaction
        
        return jsonify({"message": "Product added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route: Update stock quantity
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_stock(product_id):
    try:
        # Get the JSON data from the request
        data = request.get_json()
        new_stock = data["stock_quantity"]

        # Update query
        query = text("""
            UPDATE Products
            SET StockQuantity = :stock_quantity
            WHERE ProductID = :product_id
        """)
        
        # Use connection and commit changes
        with engine.connect() as connection:
            transaction = connection.begin()  # Start a transaction
            result = connection.execute(query, {
                "stock_quantity": new_stock,
                "product_id": product_id
            })
            transaction.commit()  # Commit the transaction

        # Check if any rows were updated
        if result.rowcount == 0:
            return jsonify({"message": f"No product found with ProductID {product_id}"}), 404
        
        return jsonify({"message": "Stock updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route: Delete a product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        # Delete query
        query = text("DELETE FROM Products WHERE ProductID = :product_id")
        
        # Use connection and commit changes
        with engine.connect() as connection:
            transaction = connection.begin()  # Start a transaction
            result = connection.execute(query, {"product_id": product_id})
            transaction.commit()  # Commit the transaction

        # Check if any rows were deleted
        if result.rowcount == 0:
            return jsonify({"message": f"No product found with ProductID {product_id}"}), 404
        
        return jsonify({"message": "Product deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

