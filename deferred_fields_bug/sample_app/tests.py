from django.test import TestCase
from .models import SomeModel

class TestSomeModel(TestCase):

    def test_field_with_renamed_db_column(self):
        instance = SomeModel()
        instance.save()
        # instance._state.db needs to be True to get into the offending execution block
        # in .save(), i.e. to satisy "not force_insert and deferred_fields and using == self._state.db"
        instance.refresh_from_db()

        # this call to save() does _NOT_ save the value of "field"
        # but _does_ save the value of "name"
        instance.name = "foo"
        instance.field = "bar"
        instance.save()

        reloaded = SomeModel.objects.get(id=instance.id)
        # normal text field, class property and db column name match
        self.assertEqual(reloaded.name, instance.name)
        # with a renamed db column, "_field" is in self.__dict__, but "field" is not,
        #  def get_deferred_fields(self):
        #      """
        #      Return a set containing names of deferred fields for this instance.
        #      """
        #      return {
        #          f.attname for f in self._meta.concrete_fields
        # ->       if f.attname not in self.__dict__
        #      }
        #
        # and then field is not saved in .save(), because django _mistakenly_ thinks
        # "field" is deferered, so it is ignored during .save() https://github.com/django/django/blob/93331877c81c1c6641b163b97813268f483ede4b/django/db/models/base.py#L712
        #
        #     elif not force_insert and deferred_fields and using == self._state.db:
        #         field_names = set()
        #         for field in self._meta.concrete_fields:
        #             if not field.primary_key and not hasattr(field, 'through'):
        #                 field_names.add(field.attname)
        # ->      loaded_fields = field_names.difference(deferred_fields)
        #         if loaded_fields:
        #             update_fields = frozenset(loaded_fields)
        #
        #     self.save_base(using=using, force_insert=force_insert,
        #                    force_update=force_update, update_fields=update_fields)
        #

        # asserting that django thinks "field" is deffered (not that .models does NOT tell it to deferr this field!)
        self.assertEqual(instance.get_deferred_fields(), {'field'})
        self.assertEqual(instance.field, reloaded.field)
