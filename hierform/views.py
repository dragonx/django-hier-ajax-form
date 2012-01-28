from django.http import HttpResponse
from django.shortcuts import render_to_response
from forms import DemoForm

def demoform(request):
    '''
    This view handles the form submission.
    '''
    if request.POST:
        '''
        This part handles the real form submission.
        In real life, you would save the data from the form, or something like that.
        '''
        form = DemoForm(request.POST)
        if form.is_valid():
            return HttpResponse("DemoForm submit succeeded!")
        else:
            return HttpResponse("DemoForm validation failed.  Make sure you fill out all fields.")
    else:
        '''
        This part handles generating a form for the user
        '''
        params = { 'formid' : 'createform',
                   'submiturl' : "demoform",
                   'btntxt' : "Submit form",
                   'jsurl'  : 'djhform.js' }
    
        params["form"] = DemoForm().ajaxRequest(request.GET) # Magic!
        if request.GET:
            '''
            This is an AJAX request with form parameters set.
            Generate a form snippet here, so don't use the entire template
            '''
            return HttpResponse(params["form"].as_table(), content_type="application/xhtml")        
        else:
            '''
            Generate a brand new form
            '''
            return render_to_response('hierform/formtest.html', params)

def javascript(request):
    '''
    This view generates the javascript for the form.  The javascript can be served as
    a static file, but this view injects the form url for the script to call back to the server.
    This could be hardcoded into the javscript if you'd like.
    
    The javascript handles hierarchical field selection actions.  On each selection it calls back
    to the form url, which returns html snippets of the new form fields.
    The javascript then replaces the existing form fields with the new ones.
    '''
    params = { 'formid' : 'createform',
               'ajaxurl': 'demoform'
             }
    return render_to_response('hierform/djhform.js', params)