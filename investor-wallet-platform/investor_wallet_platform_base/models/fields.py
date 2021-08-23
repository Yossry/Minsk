from odoo.fields import Html
from odoo.tools import html_sanitize

"""
For an integration matter we override these two methods from
the Html field class in order to return None in case of the field is empty.
Cause Odoo fill those empty field with <p><br></p> instead of leaving it
None or empty.
"""


def convert_to_column(self, value, record, values=None, validate=True):
    if value is None or value is False:
        return None
    if self.sanitize:
        value = html_sanitize(
                value, silent=True,
                sanitize_tags=self.sanitize_tags,
                sanitize_attributes=self.sanitize_attributes,
                sanitize_style=self.sanitize_style,
                strip_style=self.strip_style,
                strip_classes=self.strip_classes)
    if value == '<p><br></p>' or value == '<p></p>':
        return None
    return value


def convert_to_cache(self, value, record, validate=True):
    if value is None or value is False:
        return False
    if validate and self.sanitize:
        value = html_sanitize(
                value, silent=True,
                sanitize_tags=self.sanitize_tags,
                sanitize_attributes=self.sanitize_attributes,
                sanitize_style=self.sanitize_style,
                strip_style=self.strip_style,
                strip_classes=self.strip_classes)
    if value == '<p><br></p>' or value == '<p></p>':
        return None
    return value


Html.convert_to_column = convert_to_column
Html.convert_to_cache = convert_to_cache
