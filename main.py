"""Main script, example data import
and product creation

- Configure db connection parameter in
    `config.DATABASE_URL`
- Choose whether you want to execute 'attr_in_neo_example'
or 'attr_in_code_example' in the `if __name__ == '__main__'`
section at the end of the script

WARNING: functions creating categories (and attributes)
are not re-entrant and should be run only once
"""
import json

from neomodel import config, RequiredProperty
from src.attr_in_neo.lib import (
    import_data as import_data_neo,
    attributes_to_define,
    create_product as create_product_neo,
)
from src.attr_in_neo.models import Category
from src.attr_in_code.lib import (
    import_data as import_data_code,
    create_product as create_product_code,
)

# database connection URL
# bolt://<username>:<password>@<host>:<post>
config.DATABASE_URL = 'bolt://neo4j:admin@localhost:7687'
# todo: read connection parameters from env


def attr_in_neo_data_import():
    with open("src/attr_in_neo/data/attributes.json") as f:
        attributes = json.load(f)
    with open("src/attr_in_neo/data/categories.json") as f:
        categories = json.load(f)
    import_data_neo(attributes, categories)


def attr_in_neo_example():
    # get a category and possible attributes for products in this category
    cat = Category.nodes.get_or_none(name="Desktop")
    print("Retrieved category", cat)
    print("Attributes to define for this category", attributes_to_define(cat))
    # create a product
    p = create_product_neo(
        "Desktop",
        {
            "Name": "Desktop 1",
            "CPU frequency": 100,
            "Shipping weight": 1,
            "Weight": 0.8,
            "Price": 999,
        }
    )
    print("Created product:", p)
    # try creating a product with missing fields
    try:
        create_product_neo(
            "Desktop",
            {
                # name is required, will raise an error
                "CPU frequency": 100,
                "Shipping weight": 1,
                "Weight": 0.8,
                "Price": 999,
            }
        )
    except ValueError as e:
        print("Create product failed, but this is expected. Error is:", e)


def attr_in_code_import_data():
    with open("src/attr_in_code/data/categories.json") as f:
        categories = json.load(f)
    import_data_code(categories)


def attr_in_code_example():
    p = create_product_code(
        "Desktop",
        {
            "name": "Desktop 1",
            "shipping_weight": 1,
            "weight": 0.8,
            "price": 999,
            "computer": {
                "cpu_frequency": 100,
            }
        }
    )
    print("Created product:", p)
    # try creating a product with missing fields
    try:
        create_product_code(
            "Desktop",
            {
                # name is required, will raise an error
                "shipping_weight": 1,
                "weight": 0.8,
                "price": 999,
                "computer": {
                    "cpu_frequency": 100,
                }
            }
        )
    except RequiredProperty as e:  # error from neomodel
        print("Create product failed, but this is expected. Error is:", e)


if __name__ == '__main__':
    # ===========================
    # Attributes in database (neo4j)
    # ===========================
    # # import data (run only once)
    # # attr_in_neo_data_import()
    # fetch categories, create products
    # attr_in_neo_example()

    # ===========================
    # Attributes in code
    # ===========================
    # # import data (run only once)
    # attr_in_code_import_data()
    # fetch categories, create products
    attr_in_code_example()
