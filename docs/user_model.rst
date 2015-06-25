User Fields
==========

As every box can have its own needs about users fields, there is a mecanism
to define the user model that a box will use.

All user models are defined in `ideasbox/models.py`.

Fields definitions are made through mixings, for example `KirundiLangMixin`
will add a field to the user model allowing to define the user Kirundi level.

If none of the already defined models suit your needs, you'll need to add one,
and commit your changes to have everything versionned.

To add a new user model, you just need to create a new python class, with a
unique name dedicated to the box context (for example `BurundiRefugeeUser` is
used for the boxes that have been installed into refugees camp in Burundi), and
then include as class parents at least `AbstractUser`, and all the mixins you
need.

For example::

    class MyCustomUserModel(AbstractUser, ProfileMixin, RefugeeMixin,
                         SwahiliLangMixin, FrenchLangMixin, KirundiLangMixin):
        """
        User for my custom boxes installation.
        """
        mycustomfield = models.CharField(_('Custom'), max_length=100)

If not all the needed fields are available in mixins, you can add fields to
your user, or, if you think those fields can be used also by other users in the
future, you can create new mixins.

Then you need to set an environment variable, **before running the initial
project migration**, with the name of your model, for example::

    export AUTH_USER_MODEL=ideasbox.MyCustomUserModel
