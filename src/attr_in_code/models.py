import random

from neomodel import (
    StructuredNode,
    RelationshipTo, RelationshipFrom,
    One, ZeroOrOne,
    StringProperty, FloatProperty, IntegerProperty,
)


class CategoryV2(StructuredNode):
    """A category node

    A category is connected to its subcategories.
    """
    # properties
    name = StringProperty()
    # relationships
    sub_categories = RelationshipTo(
        "CategoryV2", 'SUBCATEGORY'
    )
    # reverse relationships
    sup_categories = RelationshipFrom(
        "CategoryV2", "SUBCATEGORY",
        cardinality=ZeroOrOne,
    )


class ProductV2(StructuredNode):
    """A product defined from its 'sku' (ID)
    and all structured data
    """
    # properties
    sku = IntegerProperty(default=lambda: random.randint(0, 1000))
    name = StringProperty(required=True)
    price = FloatProperty(required=True)
    weight = FloatProperty()
    shipping_weight = FloatProperty()
    # relationships
    category = RelationshipTo("CategoryV2", "CATEGORY", cardinality=One)
    """Here I assume that one product belongs to one and only one
    category - not really realistic?
    """
    computer_data = RelationshipTo(
        "ComputerProductData", "COMPUTER",
        cardinality=ZeroOrOne,
    )


class ComputerProductData(StructuredNode):
    """Not mandatory, but we can consider splitting product data
     into several nodes

     TODO: make this node mandatory for some categories?
     """
    cpu_frequency = IntegerProperty(required=True)
    expansion_slots = IntegerProperty(default=4)
    product = RelationshipFrom("ProductV2", "COMPUTER", cardinality=One)
