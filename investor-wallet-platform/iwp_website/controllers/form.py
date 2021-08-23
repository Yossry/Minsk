# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Inspired by Form and Field class of Django
# See: https://docs.djangoproject.com/en/2.2/_modules/django/forms/forms
# See: https://docs.djangoproject.com/en/2.2/_modules/django/forms/fields

"""Form factory for Odoo website"""

from collections import OrderedDict
from datetime import date, datetime
from inspect import signature


class FormValidationError(Exception):
    """Error raised when a value cannot be validated."""


class Choice:
    """Choices for a select field."""

    def __init__(self, value, display, att=None, obj=None):
        self.value = str(value)
        self.display = str(display)
        self.att = {key: str(val) for key, val in att.items()} if att else {}
        self.obj = obj


class Field:
    """The field of a form."""

    def __init__(
        self,
        label=None,
        required=False,
        readonly=False,
        hidden=False,
        att=None,
        content=None,
        input_type=None,
        choices=None,
        validators=None,
        template=None,
    ):
        self.label = label
        self.required = required
        self.readonly = readonly
        self.hidden = hidden
        self.att = att
        self.content = content
        self.input_type = input_type
        self.choices = choices  # A callable that return choices
        self.validators = [] if validators is None else validators
        self.template = template

    def to_python(self, value):
        """Transform the value to a python type value"""
        if self.input_type == "number" and value:
            return int(value)  # TODO: protect this by try except
        if self.input_type == "date" and value:
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

    def clean(self, value):
        """Clean value by running validators"""
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def validate(self, value):
        """Default validation for the field."""
        # Required fields
        if not value and self.required:
            raise FormValidationError("This field is required.")
        # Choices fields
        if self.choices is not None:
            choices_ids = [
                choice.value for choice in self.choices()
            ]
            if value not in choices_ids:
                raise FormValidationError(
                    "The selected item is not valid choice."
                )

    def run_validators(self, value):
        """
        This should raise ValidationError if it's not possible to
        validate.
        """
        for validator in self.validators:
            if len(signature(validator).parameters) > 1:
                validator(value=value, field=self)
            else:
                validator(value)


class Form:
    """A form"""

    def __init__(self, data=None, initial=None, context=None):
        # data should not be modified by the form
        self.is_bound = data is not None  # Tell if the form has been submitted
        self.data = {} if data is None else data
        self.initial = {} if initial is None else initial
        self.context = {} if context is None else context
        self.cleaned_data = None
        self._errors = None
        self.fields = OrderedDict()

    @property
    def errors(self):
        """Clean data of the form and returns errors found in this data."""
        if self._errors is None:
            self.full_clean()
        return self._errors

    def is_valid(self):
        """Return True if the form has no errors, or False otherwise."""
        return self.is_bound and not self.errors

    def full_clean(self):
        """Clean the form data."""
        self._errors = {}
        # Do not clean if form is not bound (has not been submitted)
        if not self.is_bound:
            return
        self.cleaned_data = {}
        self._clean_fields()
        self._clean_form()

    def add_error(self, name, err):
        """Update `self._errors`"""
        self._errors[name] = err

    def clean(self):
        """
        Overwrite this method to add general form validation.
        This method should return all the cleaned data.
        This method should raise FormValidationError if the form cannot
        be validated.
        """
        return self.cleaned_data

    def _clean_fields(self):
        """
        Call clean method of each fields and populate
        `self.cleaned_data`.
        """
        for name, field in self.fields.items():
            if field.readonly:
                value = self.initial.get(name)
            else:
                value = self.data.get(name)
            try:
                value = field.clean(value)
                self.cleaned_data[name] = value
            except FormValidationError as err:
                self.add_error(name, err)

    def _clean_form(self):
        """
        Clean the form after each fields have been cleaned. It populates
        `self._errors` with founded errors.
        """
        try:
            cleaned_data = self.clean()
        except FormValidationError as err:
            self.add_error("__all__", err)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data
