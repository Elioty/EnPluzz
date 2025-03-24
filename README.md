EnPluzz
=======

# Website

The website runs on the Django Python web framework. It has been developed and tested with Django version 5.1.4. You can try to run it with a more recent version (which we will definitely update to at some point) but that is at your own risk.
The other dependency is the django-debug-toolbar package which gives a very useful debug sidebar (when debug is enabled) for development and debugging purposes.

Commands to start working (the first time):
```
python -m pip install Django==5.1.4
python -m pip install django-debug-toolbar==5.0.1
cd website
cp enpluzz/settings.orig.py enpluzz/settings.py
python manage.py migrate
python manage.py enpluzz_import --verbose <path_to_game_data_archive>
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
The output of the last command is the value to set to the `SECRET_KEY` variable in `website/enpluzz/settings.py`.
A sample game data archive will be provided later on to have a minimal set of data to work with.

Then, each time you want to do some work, you can run the Django's built-in development server:
```
python manage.py runserver
```
and open http://127.0.0.1:8000/. Then simply type `CONTROL-C` to stop the server.

> [!WARNING]
> Since the website is still in ***early*** development, the migration files might be overwritten. In such case, you should remove the `db.sqlite3` file (if you use the default settings) and run the `migrate` and `enpluzz_import` commands again.

# Desktop app

Development of the desktop app to automatically retrieve the player's progress from an Android Virtual Machine (BlueStacks, MEmu, etc...) and upload it to EnPluzz website has not begun yet as more work needs to be done on the website first. However, that is definitely part of the roadmap to hopefully give a much greater experience than other comparable tools.

# Mobile app

Sadly, it will not be posible to make a mobile app that could do the same as the desktop app since Android's and iOS's security systems prevent applications from reading other applications' cached data.
