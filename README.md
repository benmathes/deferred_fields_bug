

# Django bug in deferred fields


installed using:

* python 3.6.4
* Django==2.0.4
* pytz==2018.4


To see the bug in action, run

    $ cd $git_root/deferred_fields_bug
    $ python ./manage.py test


## explanation:

    # with a renamed db column, "_field" is in self.__dict__, but "field" is not,
    #  def get_deferred_fields(self):
    #      """
    #      Return a set containing names of deferred fields for this instance.
    #      """
    #      return {
    #          f.attname for f in self._meta.concrete_fields
    #          if f.attname not in self.__dict__
    #      }
    #
    # and then field is not saved in .save(), because django _mistakenly_ thinks
    # "field" is deferred, so it is ignored during .save() https://github.com/django/django/blob/93331877c81c1c6641b163b97813268f483ede4b/django/db/models/base.py#L712
    # ...
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
    # ...

    # asserting that django thinks "field" is deffered (not that .models does NOT tell it to defer this field!)
