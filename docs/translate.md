# Translations

Ideascube is [translated in Transifex](https://www.transifex.com/ideascube/ideascube/).

Head over there if you're interested in helping translate Ideascube in your
language.

The rest of this documentation is for Ideascube developers to manage the
translations.

## Fetch the latest translations from Transifex

First, download the latest `.po` files with the work from the translators:

    $ make pull_translations

Next, compile the translations into the `.mo` files as used by Gettext:

    $ make compile_translations

## Send the latest strings to Transifex

First, update the `.pot`/`.po` files with the latest strings from the source
code:

    $ make collect_translations

Next, send those over to Transifex:

    $ make push_translations
