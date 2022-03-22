"""Functions to import data and create products
by checking the provided attributes match the
expected ones depending on product category.
"""
import random
from typing import Optional
from neomodel import db

from src.attr_in_neo.models import Attribute, Category, Product


# ===============
# Importers
# ===============

def _import_attributes(attribute_data: dict) -> dict[str, Attribute]:
    """Attribute data is an item of the attributes.json file
    """
    attributes = {}
    for attr_data in attribute_data:
        attr = Attribute(**attr_data).save()
        attributes[attr_data["name"]] = attr
    return attributes


def _import_category(
        cat_data: dict,
        categories: dict[str, Category],
        attributes: dict[str, Attribute]
):
    # create category and relationships to super cat
    # and attributes in a transaction
    # (everything succeed or everything fails)
    with db.transaction():
        # we create the category with given name
        cat = Category(name=cat_data["name"]).save()
        # we try and connect super category if it was provided
        # NB: I have chosen to keep it simple for now, and super category
        # needs to be already in the graph
        sup_cat = cat_data.get("super")
        if sup_cat:
            cat.sup_categories.connect(categories[sup_cat])
        # then we deal with attributes
        attrs = cat_data.get("attributes", [])
        for a in attrs:
            attr_name = a.pop("attr_name")
            attr = attributes[attr_name]
            cat.attributes.connect(
                attr,
                a,
            )
        return cat


def import_data(attribute_data: list[dict], category_data: list[dict]):
    """Import data

    :param attribute_data: list of dicts from attributes.json
    :param category_data: list of dicts from categories.json
    """
    attributes = _import_attributes(attribute_data)
    categories = {}
    for cat_data in category_data:
        cat = _import_category(cat_data, categories, attributes)
        categories[cat_data["name"]] = cat


# ===============
# Some helper functions to create products
# ===============

def attributes_to_define(cat: Category) -> list:
    """For a given category, returns a list of attributes to be defined
    for a product in this category

    Recursive function that finds attribute nodes attached to cat, and
    the attributes attached to cat parents.

    NB: as it is, this function performs many queries. It is possible
    to get the same result with one single Cypher query:

        MATCH (cat:Category {name: "Desktop"})
            # get all "super" categories (direction of
            # relationship matters), including cat
            # since number of hops starts from 0
            <-[:SUBCATEGORY*0..20]-(:Category)
            # get all attributes for each super cat
            -[ra:ATTRIBUTE]->(a:Attribute)
        RETURN a {
            .*
            rel_data: ra {.*}
        }

    to be improved if we go in this direction
    """
    result = []
    # all attribute nodes directly attached to 'cat':
    attrs = cat.attributes.all()
    for a in attrs:
        # we find the relationship between cat and the given attribute 'a'
        # to extract relationship properties
        rel = cat.attributes.relationship(a)
        result.append({
            "name": rel.name,
            "required": rel.required,
            "default_value": rel.default_value,
            "unit": a.unit,
        })
    # then we do the same for all 'super' categories of 'cat':
    for c in cat.sup_categories.all():
        result.extend(attributes_to_define(c))
    return result


def create_product(
        category_name: str,
        attribute_values: dict,
        sku: Optional[int] = None,
) -> Product:
    """Create a product node, after having checked that
    the provided attribute_values match the expectations
    of category uniquely identified by category_name

    :param category_name: name of category the product belongs to
    :param attribute_values:
    :param sku:
    :return:
    """
    # get attributes for this category
    category = Category.nodes.get_or_none(name=category_name)
    attributes_for_cat = attributes_to_define(category)
    # build product_data dict to be saved on Product node
    product_data = {
        # generate random sku if not provided
        "sku": sku or random.randint(0, 1000),
    }
    # iterate over attributes configured for `cat`
    for attr_def in attributes_for_cat:
        attr_name = attr_def["name"]
        # check if the attribute value is set
        # for this product
        attr_value = attribute_values.get(attr_name)
        # if it is not set but expected (required),
        # raise en error:
        if (
                attr_value is None
                and attr_def["required"]
                and not attr_def["default_value"]
        ):
            raise ValueError(
                f"Attribute {attr_name} is required "
                f"for {category.name} but not provided"
            )
        # otherwise, save the value in product_data dict
        product_data[attr_name] = attr_value or attr_def["default_value"]
    # finally, create product node
    p = Product(**product_data).save()
    # and connect it to its category
    p.category.connect(category)
    return p
