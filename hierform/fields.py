from django import forms
from django.db import models
from django.forms import ModelChoiceField
from django.utils.datastructures import SortedDict
import logging

class HierarchicalModelChoiceField(ModelChoiceField):
    def __init__(self, **kwargs):
        '''
        Just save the parent field and current field for easy reference during updateQueryset, and then call the super constructor
        '''
        self._hierarchical_parent_field = kwargs.pop("_hierarchical_parent_field", None)
        self.field = kwargs.pop("field", None)
        kwargs["widget"] = forms.Select(attrs={'class':"djhselect"})
        return super(HierarchicalModelChoiceField, self).__init__(**kwargs)
        
    def updateQueryset(self, filter_objs):
        '''
        All the magic happens in the next few lines.
        We filter the available results queryset to only those allowed by the parent in the hierarchy.
        '''
        if self._hierarchical_parent_field:
            '''
            Filter the queryset by the parent field
            '''
            if self._hierarchical_parent_field.name in filter_objs:
                f = { self._hierarchical_parent_field.name : filter_objs[self._hierarchical_parent_field.name] } # Create a filter based on the parent in the hierarchy
                self.queryset  = self.field.rel.to.objects.filter(**f).order_by('name') # Filter the queryset based on the filter.
            else:
                self.queryset = self.field.rel.to.objects.none() # Initally blank until parent field updated
        if self.field.name in filter_objs and filter_objs[self.field.name]:
            '''
            Look for invalid objects in filter_objs that don't match the hierarchical parent filter.
            Note this only works if we operate in order and we manage to clear filter_objs before our
            hierarchical child reads it.
            '''
            obj = filter_objs[self.field.name]
            if isinstance(obj,models.Model) and not self.queryset.filter(pk=obj.pk):
                logging.debug("updateQueryset " + str(self.field.name) + " found invalid object " + str(filter_objs[self.field.name]))                     
                filter_objs[self.field.name] = None
                     
class HierarchicalForeignKey(models.ForeignKey):
    '''
    This form field shows items limited to those that reflect the given foreign key
    
    This class is pretty much the same as ForeignKey, except:
        1. It looks for a parent foreignkey field (ie if this is a State, then the parent is a foreignkey to a Country)
        2. It returns a HierarchicalModelChoiceField instead of a ModelChoiceField for a form.
        
    Possible additions:
        a. Pass in kwarg to specify hierarchical_parent_field instead of searching for it.
        b. Pass in kwarg to indicate top of the hierarchy (or pass in a hierarchical_parent_field of None)
    '''
    _hierarchical_parent_field = None
    def __init__(self, to, **kwargs):
        '''
        This function finds and sets the parent field.
        Ideally we can pass the parent field down to the formfield creation, but the formfield creation method
        doesn't take parameters from the field creation method.  So we save it in the local object now and
        pass it in when the formfield() creation method is called.
        '''
        super(HierarchicalForeignKey, self).__init__(to, **kwargs)
                
        for field in to._meta.fields:
            if isinstance(field, models.ForeignKey):
                self._hierarchical_parent_field = field
                
    def formfield(self, **kwargs):
        '''
        Create a formfield.  This calls the super formfield() method, but we tell it to create
        a HierarchicalModelChoiceField instead of just a ModelChoiceField.  We also pass in the parent field
        to initialize the HierarchicalModelChoiceField.
        '''
        defaults = {
            'form_class': HierarchicalModelChoiceField,
            '_hierarchical_parent_field' : self._hierarchical_parent_field,
            'field' : self
        }
        defaults.update(kwargs)
        return super(HierarchicalForeignKey, self).formfield(**defaults)

class HierarchicalForm(forms.ModelForm):
    
    class CannotSave(Exception):
        pass
        
    _ajaxFormClass = None #: cached AJAX form class

    def __init__(self, *args, **kwargs):
        '''
        Same as creating a ModelForm, except that we look for the HierarchicalModelChoiceFields and update their querysets
        
        It's important that fields higher up in the hierarchy are listed first in the model, otherwise
        some dependency checks may not run and this form may not work properly.
        '''
        super(forms.ModelForm, self).__init__(*args, **kwargs)        
        if args and args[0]:
            data = args[0]
        else:
            data = self.initial
        for i in self.fields:
            if isinstance(self.fields[i], HierarchicalModelChoiceField):
                self.fields[i].updateQueryset(data)

    def ajaxFormClass(self):
        '''
        This function creates an ajax form class (note a class, so you need to instantiate it after) for processing AJAX calls.
        '''
        if not self._ajaxFormClass:        
            def init(self, *args, **kwargs):
                '''
                Function used to replace the __init__() function in generated forms.
                Same as creating a ModelForm, except that we look for the HierarchicalModelChoiceFields and update their querysets
                
                It's important that fields higher up in the hierarchy are listed first in the model, otherwise
                some dependency checks may not run and this form may not work properly.
                '''
                super(HierarchicalForm, self).__init__(*args, **kwargs)
                if self.initial:
                    for i in self.fields:
                        if isinstance(self.fields[i], HierarchicalModelChoiceField):
                            self.fields[i].updateQueryset(self.initial)                    

            def nullsave(self):
                '''Function used to replace the save() function in generated fields'''
                raise HierarchicalForm.CannotSave("This model class is created for ajax form verification, and cannot save to the database.")

            '''
            The ajax form class must contain an ajax model class for processing the ajax form.
            This ajax model class is based off of the original model class, but it only contains hierarchical foreign key fields.
            '''
            
            modelFields = SortedDict() # Use a SortedDict so the form fields stay in order.
            
            for key in self.fields:
                ''' self.fields is sorted in the correct order, so we iterate through that. '''
                formfield = self.fields[key]
                if isinstance(formfield, HierarchicalModelChoiceField):
                    f = formfield.field
                    '''
                    We use the form validation to update the fields each time.  Since the form will be updated piecemeal via AJAX,
                    we need to allow blank data for the fields, so set blank=True and null=True,
                    '''
                    kwargs = { 'blank' : True, 'null' : True }
                    modelFields[key] = f.__class__(f.rel.to, **kwargs)
    
            modelFields["__module__"] = self.Meta.model.__module__
            ''' Disable the save() method to avoid accidentally polluting the database.'''        
            modelFields["save"] = nullsave
    
            '''Create new Form class that contains a new Meta that contains a new Model'''
            newModel = self.Meta.model.__metaclass__(self.Meta.model.__name__ + "_ajax", self.Meta.model.__bases__, modelFields)
            newMeta = self.Meta()
            newMeta.fields = None
            newMeta.model = newModel       
            self._ajaxFormClass = self.__class__.__metaclass__(self.__class__.__name__ + "_ajax", self.__class__.__bases__, { 'Meta' : newMeta } )
            self._ajaxFormClass.__init__ = init
        
        return self._ajaxFormClass


    def ajaxRequest(self,request):
        '''
        Helper function to process form submission data and generate a new form.
        '''
        try:
            if request.is_ajax() and request.GET:
                in_form = self.ajaxFormClass()(request.GET)
                if in_form.is_valid():
                    return self.ajaxFormClass()(initial=in_form.cleaned_data)
        except Exception, e:
            logging.error("Error processing AJAX data " + str(e))
        return self
