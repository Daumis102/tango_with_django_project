import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    python_pages = [
        {"title": "Official Python Tutorial",
         "url":"https://docs.python.org/2/tutorials/",
         "views":5},
        {"title": "How to think like computer scientist",
         "url":"https://www.greenteapress.com/thinkpython",
         "views":50},
        {"title": "Learn python in 10 minutes",
         "url":"https://www.karokithakis.net/tutorials/python",
         "views":70}]

    django_pages = [
        {"title": "Official Django Tutorial",
         "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
         "views":80},
        {"title": "Django Rocks",
         "url":"http://www.djangorocks.com/",
         "views":100},
        {"title": "How to Tango with Django",
         "url":"http://www.tangowithdjango.com/",
         "views":10}]

    other_pages = [
        {"title": "Bottle",
         "url":"http://bottlepy.org/docs/dev/",
         "views":6},
        {"title": "Flask",
         "url":"http://flask.pocoo.org",
         "views":3}]

    cats = {"Python":{"pages":python_pages, "likes":64, "views":128},
            "Django":{"pages":django_pages, "likes":32, "views":64},
            "Other Frameworks":{"pages":other_pages, "likes":16,"views":32}}



    def add_page(cat, title, url, views=0):
        p = Page.objects.get_or_create(category=cat,title=title, url = url, views = views)[0]
        c.save()
        return c

    def add_cat(name, likes, views):
        c = Category.objects.get_or_create(name=name, views = views, likes = likes)[0]
        c.save()
        return c

    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data["likes"], cat_data["views"])
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    for c in Category.objects.all():
        for p in Page.objects.filter(category = c):
            print("- {0}  - {1}".format(str(c), str(p)))

if __name__ == '__main__':
    print("Starting Rango Population script...")
    populate()
