from django.db import models




class SomeModel(models.Model):
    """
    a contrived model field where we want a "field" that is stored
    in a "field" column, but we use @property getter/setters so
    we name the SomeModel class's attribute as "_field".
    """
    name = models.TextField(null=True)
    _field = models.TextField(name="field")

    @property
    def field(self):
        return self._field.upper()

    @field.setter
    def field(self, new_value):
        self._field = new_value.lower()
