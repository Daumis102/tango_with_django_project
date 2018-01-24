from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    # Query the database for a list of all the categories currently storred
    # Order the categories by no. likes in descending order
    # Retrieve the top 5 only - or all if it is less than 5
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine

    categories = Category.objects.order_by('-likes')[:5]
    pages = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': categories,
                    'pages': pages}
    
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {}
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        #can we find a category name slug with the given name?
        # if we can't, the .get() method raises a DoesNotExist exception
        # So the .get() method returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category = category)

        # adds our results list to the template context under name pages
        context_dict['pages'] = pages

        # we also add the category object from
        # the database to the context dictionary
        # we will use this in the template to verify that the category exists.
        context_dict['category'] = category

    except Category.DoesNotExist:
        # We get here if we dont find the specified category
        # Dont do anything
        # The template will display the 'no category' message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    # Do render the response and return it to the client
    return render(request, 'rango/category.html', context = context_dict)    

def add_category(request):
    form = CategoryForm()

    # a HTTP POST?
    if request.method == "POST":
        form = CategoryForm(request.POST)
        print ("method: post")

    # Have we been provided with the valid form?
        if form.is_valid():
            print("form is valid")
            # save the new category to the database.
            form.save(commit=True)
            # now that hte category is saved
            # we could give a confirmation message
            # but since the most recent category added is on the index page
            # Then we can direct the user back to the index page.
            return index(request)
        else:
            # the supplied form contains errors -
            # just print them to the terminal.
            print(form.errors)

        # will handle the bad form, new form, or no form supplied classes.
        # render the form with the error messages.
    print ("returning")
    return render(request, "rango/add_category.html",{"form": form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {"form": form, "category":category}
    return render(request, "rango/add_page.html", context_dict)
    
