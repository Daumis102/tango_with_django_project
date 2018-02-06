from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required



def index(request):

    request.session.set_test_cookie()
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
    if request.session.test_cookie_worked():
        print('TEST COOKIE WORKED!')
    
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

def register(request):
    # a boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # if its a HTTP POST we're interested in processing form data.
    if request.method == "POST":
        # atempt to frab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if the two forms are valud...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            #Now sort out the UserProfile instance.
            # since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems

            profile = profile_form.save(commit=False)
            profile.user = user                           

            # did the user provide a profile picture?
            # if so, we need to get it from the input form and
            # put it in the UserProfileModel.

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance
            profile.save()
            # Update our variable to indicate that the template
            # Registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for the user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render the template depending on context
    return render(request,
                  'rango/register.html',
                  {'user_form':user_form,
                   'profile_form': profile_form,
                   'registered': registered})
        
def user_login(request):
    # if the request is a HTTP POST, try to pull out the relevant information
    if request.method == 'POST':
        # Gather the username and password provided by the user
        # This information is obtained from the login form/
        # We user request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while other will raise a KeyError exception.

        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is
        user = authenticate(username=username, password=password)

        # if we have a User object, the details are correct.
        # if None, no user with matching credentials was found

        if user:
            # Is the account active? It could have been dissabled.
            if user.is_active:
                # if the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # an inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login credentials were provided. So we can't log the user in.
            print("invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be HTTP GET
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object..
        return render(request, 'rango/login.html',{})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

# use the login_required() decorator to ensure only those logged in can access the view
@login_required
def user_logout(request):
    # since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage
    return HttpResponseRedirect(reverse('index'))

                                       
    
