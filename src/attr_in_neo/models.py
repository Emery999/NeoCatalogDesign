import enum

from neomodel import (
    StructuredNode, StructuredRel,
    RelationshipTo, RelationshipFrom,
    One, ZeroOrOne,
    StringProperty, BooleanProperty,
    FloatProperty, IntegerProperty,
)
from neomodel.contrib import SemiStructuredNode


class AttributeUnitEnum(enum.Enum):
    """The different units that can be attached to Attribute below
    """
    METER = "m"
    INCH = "inch"
    GRAM = "g"
    KILOGRAM = "kg"
    US_DOLLAR = "USD"
    MHZ = "MHz"
    PIECE = "pcs."

    @classmethod
    def to_dict(cls):
        """Returns a dict of item.name => item.value
        for each enum item.

        E.g.: {"METER": "m", "INCH": "inch", ....}

        :return:
        """
        return {item.name: item.value for item in cls}


class AttributeRelationship(StructuredRel):
    """The model for the relationship between an Attribute
    and a Category, containing the attribute specific properties
    for this category.
    """
    # properties
    name = StringProperty()
    """Attribute name"""
    required = BooleanProperty()
    """If True, the attribute must be set for this category"""
    default_value = FloatProperty()
    """A possible default value if the attribute is not provided"""


class Attribute(StructuredNode):
    """Attribute node"""
    # fixme: why PyCharm is complaining about a missing
    #   "category" classmethod for all StructuredNode?
    # properties
    name = StringProperty()
    unit = StringProperty(
        choices=AttributeUnitEnum.to_dict()
    )
    # we could add here a "dtype" (data type)
    # relationship to Category nodes
    categories = RelationshipFrom(
        "Category", "ATTRIBUTE",
        model=AttributeRelationship,
    )


class Category(StructuredNode):
    """A category node"""
    # properties
    name = StringProperty()
    # relationships
    sub_categories = RelationshipTo(
        "Category", 'SUBCATEGORY'
    )
    attributes = RelationshipTo(
        "Attribute", "ATTRIBUTE",
        model=AttributeRelationship,
    )
    # reverse relationships
    sup_categories = RelationshipFrom(
        "Category", "SUBCATEGORY",
        cardinality=ZeroOrOne,
    )

    # def attributes_to_define(self):
    #     results, columns = self.cypher(
    #           "MATCH (a)-[:ATTRIBUTE]->(b) WHERE id(a)={self} RETURN b"
    #     )
    #     return [Attribute.inflate(row[0]) for row in results]


class Product(SemiStructuredNode):
    """A product defined from its 'sku' (ID) and some unstructured data
    whose definition depends on the product category

    NB: that means there is no type-check performed here, we could
    create a product whose price="one hundred"
    These checks will have to be performed earlier
    """
    # properties
    sku = IntegerProperty()
    # relationships
    category = RelationshipTo("Category", "CATEGORY", cardinality=One)
    """Here I assume that one product belongs to one and only one
    category - not really realistic?
    """
