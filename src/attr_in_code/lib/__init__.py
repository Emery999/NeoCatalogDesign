"""Functions to import data and create products,
relying on neomodel internal checks
"""
from neomodel import db
from src.attr_in_code.models import ProductV2, CategoryV2, ComputerProductData


# ===============
# Importers
# ===============

def import_data(category_data: list[dict]):
    """Import data (only categories)

    :param category_data: list of dicts from categories.json
    """
    categories = {}
    for cat_data in category_data:
        cat = CategoryV2(name=cat_data["name"]).save()
        categories[cat_data["name"]] = cat
        sup_cat = cat_data.get("super")
        if sup_cat:
            cat.sup_categories.connect(categories[sup_cat])


# ===============
# Some helper functions to create products
# ===============

def create_product(category_name: str, attribute_values: dict) -> ProductV2:
    """Create a product and attach it to category `category_name`.
    Attribute types and required status are performed by neomodel.

    :param category_name:
    :param attribute_values:
    :return:
    """
    cat = CategoryV2.nodes.get_or_none(name=category_name)
    # computer_data, if any
    c_data = attribute_values.pop("computer", None)
    # create product and related node in
    # a transaction (everything succeed or everything fails)
    with db.transaction():
        p = ProductV2(**attribute_values).save()
        p.category.connect(cat)
        if c_data:
            # if computer data provided, create related node
            # and connect both nodes
            cd = ComputerProductData(**c_data).save()
            cd.product.connect(p)
        return p
