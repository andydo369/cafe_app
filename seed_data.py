from datetime import date, timedelta

import db

# Adds sample data to the database so the app can be tested without typing everything in.
# Every table except Users ends up with exactly 15 rows.
# Run with: python seed_data.py
# WARNING: this clears all tables except Users first, so any real menu/order data is removed.

INGREDIENTS = [ # (name, current_stock, reorder_level)
    ("Black Tea Leaves",    5000,  1000),
    ("Green Tea Leaves",    4000,  1000),
    ("Oolong Tea Leaves",   3000,  1000),
    ("Thai Tea Mix",        6000,  1500),
    ("Milk",                20000, 5000),
    ("Sugar Syrup",         10000, 3000),
    ("Tapioca Pearls",      8000,  2000),
    ("Strawberry Syrup",    8000,  2000),
    ("Mango Syrup",         1500,  2000), # below reorder level, shows the low stock warning
    ("Passion Fruit Syrup", 7000,  2000),
    ("Taro Powder",         5000,  1500),
    ("Cheese Foam Mix",     800,   1000), # below reorder level, shows the low stock warning
    ("Grass Jelly",         6000,  1500),
    ("Pudding",             5000,  1500),
    ("Coffee Powder",       4000,  1000),
]

ITEMS = [ # (name, price, [(ingredient name, quantity used)])
    ("Classic Milk Tea",        45000, [("Black Tea Leaves", 10)]),
    ("Thai Milk Tea",           50000, [("Thai Tea Mix", 30)]),
    ("Jasmine Green Tea",       35000, [("Green Tea Leaves", 10)]),
    ("Oolong Milk Tea",         50000, [("Oolong Tea Leaves", 10)]),
    ("Strawberry Milk Tea",     55000, [("Strawberry Syrup", 40)]),
    ("Mango Fruit Tea",         50000, [("Mango Syrup", 40)]),
    ("Passion Fruit Green Tea", 45000, [("Passion Fruit Syrup", 40)]),
    ("Taro Milk Tea",           55000, [("Taro Powder", 40)]),
    ("Coffee Milk Tea",         55000, [("Coffee Powder", 20)]),
    ("Brown Sugar Boba Milk",   55000, [("Tapioca Pearls", 80)]),
    ("Fresh Milk Latte",        40000, [("Milk", 300)]),
    ("Cheese Foam Black Tea",   50000, [("Cheese Foam Mix", 40)]),
    ("Grass Jelly Milk Tea",    45000, [("Grass Jelly", 60)]),
    ("Pudding Milk Tea",        50000, [("Pudding", 60)]),
    ("Sweet Iced Tea",          30000, [("Sugar Syrup", 40)]),
]

SUBCATEGORIES = [ # (name, price, [(ingredient name, quantity used)])
    ("Extra Boba",         5000,  [("Tapioca Pearls", 50)]),
    ("Cheese Foam",        10000, [("Cheese Foam Mix", 30)]),
    ("Grass Jelly",        5000,  [("Grass Jelly", 50)]),
    ("Pudding",            8000,  [("Pudding", 50)]),
    ("Extra Milk",         5000,  [("Milk", 100)]),
    ("Extra Sugar",        0,     [("Sugar Syrup", 20)]),
    ("Less Sugar",         0,     []),
    ("No Sugar",           0,     []),
    ("Less Ice",           0,     []),
    ("No Ice",             0,     []),
    ("Large Size",         10000, [("Milk", 100), ("Sugar Syrup", 15), ("Black Tea Leaves", 5)]),
    ("Extra Tea Shot",     5000,  [("Black Tea Leaves", 5)]),
    ("Coffee Shot",        10000, [("Coffee Powder", 15)]),
    ("Taro Topping",       8000,  [("Taro Powder", 20), ("Milk", 50)]),
    ("Fruit Jelly Mix",    8000,  [("Strawberry Syrup", 20), ("Passion Fruit Syrup", 20)]),
]

ORDERS = [ # (days ago, item name, [subcategory names]), one drink per order
    (0,  "Classic Milk Tea",        ["Extra Boba", "Less Ice"]),
    (1,  "Thai Milk Tea",           ["Extra Boba"]),
    (1,  "Taro Milk Tea",           ["Pudding"]),
    (2,  "Jasmine Green Tea",       []),
    (3,  "Brown Sugar Boba Milk",   ["Cheese Foam", "Less Sugar"]),
    (4,  "Mango Fruit Tea",         ["No Sugar"]),
    (5,  "Oolong Milk Tea",         ["Grass Jelly"]),
    (6,  "Strawberry Milk Tea",     []),
    (7,  "Passion Fruit Green Tea", ["No Ice"]),
    (8,  "Coffee Milk Tea",         ["Coffee Shot", "Large Size"]),
    (9,  "Classic Milk Tea",        ["Extra Milk"]),
    (10, "Fresh Milk Latte",        ["Extra Sugar"]),
    (11, "Cheese Foam Black Tea",   []),
    (12, "Pudding Milk Tea",        ["Taro Topping"]),
    (13, "Grass Jelly Milk Tea",    ["Fruit Jelly Mix"]),
]

OTHER_TABLES = [ # children first so foreign keys don't block the delete
    "Ordered_Items_Subcategories", "Ordered_Items", "Orders",
    "Items_Ingredients", "Subcategories_Ingredients",
    "Items", "Subcategories", "Ingredients",
]


def seed():
    conn = db.get_connection()
    cursor = conn.cursor()

    # empty every table except Users, and reset the IDs so they start at 1 again
    for table in OTHER_TABLES:
        cursor.execute(f"DELETE FROM {table}")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name != 'Users'")

    # Ingredients
    for name, current_stock, reorder_level in INGREDIENTS:
        cursor.execute(
            "INSERT INTO Ingredients (name, current_stock, reorder_level) VALUES (?, ?, ?)",
            (name, current_stock, reorder_level)
        )
    ingredient_ids = dict(cursor.execute("SELECT name, ingredient_id FROM Ingredients").fetchall()) # name -> id

    # Items and their ingredients
    item_ids = {}
    item_prices = {}
    for item_name, item_price, item_ingredients in ITEMS:
        cursor.execute("INSERT INTO Items (name, price) VALUES (?, ?)", (item_name, item_price))
        item_ids[item_name] = cursor.lastrowid
        item_prices[item_name] = item_price
        for ingredient_name, quantity in item_ingredients:
            cursor.execute(
                "INSERT INTO Items_Ingredients (item_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                (item_ids[item_name], ingredient_ids[ingredient_name], quantity)
            )

    # Subcategories and their ingredients
    subcategory_ids = {}
    subcategory_prices = {}
    for subcategory_name, subcategory_price, subcategory_ingredients in SUBCATEGORIES:
        cursor.execute(
            "INSERT INTO Subcategories (name, price) VALUES (?, ?)",
            (subcategory_name, subcategory_price)
        )
        subcategory_ids[subcategory_name] = cursor.lastrowid
        subcategory_prices[subcategory_name] = subcategory_price
        for ingredient_name, quantity in subcategory_ingredients:
            cursor.execute(
                "INSERT INTO Subcategories_Ingredients (subcategory_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                (subcategory_ids[subcategory_name], ingredient_ids[ingredient_name], quantity)
            )

    # Orders, price worked out from the item and the options picked
    for days_ago, item_name, subcategory_names in ORDERS:
        order_date = (date.today() - timedelta(days=days_ago)).isoformat()
        total = item_prices[item_name] + sum(subcategory_prices[name] for name in subcategory_names)
        cursor.execute("INSERT INTO Orders (date, price) VALUES (?, ?)", (order_date, total))
        order_id = cursor.lastrowid
        cursor.execute("INSERT INTO Ordered_Items (order_id, item_id) VALUES (?, ?)", (order_id, item_ids[item_name]))
        ordered_item_id = cursor.lastrowid
        for subcategory_name in subcategory_names:
            cursor.execute(
                "INSERT INTO Ordered_Items_Subcategories (ordered_item_id, subcategory_id) VALUES (?, ?)",
                (ordered_item_id, subcategory_ids[subcategory_name])
            )

    conn.commit()

    # show how many rows each table has now
    for table in ["Users"] + OTHER_TABLES:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count}")
    conn.close()


if __name__ == "__main__":
    db.create_tables()
    seed()
