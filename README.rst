Hierarchical Django AJAX Forms
==============================

This project takes the gruntwork out of making Django forms with dynamic AJAX select fields for hierarchical data sets, such as (country, state, city, neighborhood) or (vehicle make, model, trim).

When you make a selection in the field higher in the hierarchy, AJAX calls automatically update the lower fields with the allowed data. 


Code layout
===========

Two key files contain all the code that you would need to incorporate into your own project::

    hierform/fields.py
    hierform/templates/hierform/djhform.js

The rest of the hierform folder exists as a demo project.

The location folder just contains some models for demo purposes.


Demo
====

It should be pretty easy to get the demo up and running if you have Django setup already.  Add the two folders, then modify INSTALLED_APPS in your settings.py::

    INSTALLED_APPS = (
        'location', # location module
        'hierform', # hierarchical ajax form
    )

You'll also need to add the URLs::

    urlpatterns = patterns('',
        ('^hierform/', include('hierform.urls'))
    )

The demo uses location.models as the hierarchical data.  To inject some test data into your database, run location.models.init_db() from the django shell::

    python manage.py shell
    >>> import location.models
    >>> location.models.init_db()

After launching the server, you should be able to access the demo at http://<host>/hierform/demoform


Building your own form
======================

Building a form is very simple, but this README assumes you have some basic experience with Django and Django forms.  Refer to the Django documentation for this.  All the steps are shown in the included demo.  A prerequisite is to have a hierarchical data set to use.  If not, check out the location models in the demo.

1. Define a model representing your form.  The model should contain foreign keys to models in your hierarchical data set.  However, instead of using the django ForeignKey field, use hierform.fields.HierarchicalForeignKey.  Example: hierform.models.DemoModel

2. Defined a form that uses your model, but inherit from hierform.fields.HierarchicalForm instead the django ModelForm.  This can be done in 4 lines, including the import.  Example: hierform.forms.DemoForm

3. Add a view to handle all the form requests.  This view needs three sections.
    i. You need to handle POST request to handle form submission.  This is the same as normal Django form submission, using the form class you created (in this case, DemoForm) to validate the form.
    ii. For generating the form, instead of just using DemoForm to create the form, use DemoForm().ajaxRequest(request.GET).  In the usual case, request.GET is empty and this call instantiates a normal unbound instance of DemoForm that you can render into a template to display.
    iii. If request.GET contains AJAX form submission fields from your hierarchical data set, ajaxRequest(request.GET) will generate a small HTML snippet that contains only the updated select fields.  In this case, you want to deliver this snippet straight back to the web page, without the rest of your HTML template.
Example: hierform.views.demoform

4. Add a view to deliver the Javascript to your form.  Really all this does is inject the html tag location of your form, and the URL of your form into the javascript.  Example: hierform.views.javascript

Limitations
-----------

So far this only works on a simple hierarchical data set, with each model in the hierarchy having a single ForeignKey up to the next model in the hierarchy.  This project needs to be modified to handle situations where a model in the hierarchy has multiple ForeignKeys.  The simplest way to do this will be to pass a parameter into HierarchicalForeignKey() to indicate the name of the hierarchical parent.  Then modify HierarchicalForeignKey to use the parameter instead of looking for the only ForeignKey.

This implementation has not been tested for security.


How it works
============

Every time the user makes a selection on a select field in on the webpage, the javascript submits the form in an AJAX call using a GET request instead of a POST.  In this case, the form is not fully complete.  The view handler validates the hierarchical select fields in the form, and based on the valid fields so far, generates a new HTML snippet that contains the new valid form fields.

The new snippet is sent back to the webpage, where the javascript replaces the existing select fields with fields from the new snippet.  This occurs every time the user selects a new field.  When the form is complete, it is submitted with a POST request, and the view handler validates this as a full form.

The only piece of magic not covered so far is that HierarchicalForm internally generates a second form class (and a second model) for handling AJAX requests.  The generated form and model are used to validate the select field submissions, and the new HTML snippet.

In this case, the generated model only contains the hierarchical fields, and fields are allowed to be blank, since each AJAX request may have blank fields.  The generated form and model use the underlying Django form validation functionality to lookup the hierarchical children from the database and generate new HTML.

