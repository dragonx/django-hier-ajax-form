from django.test import TestCase
from django.test.client import RequestFactory
from forms import DemoForm
from location.models import init_db, Country, State, City, Neighborhood

class formTest(TestCase):

    def test_main(self):
        init_db() # set up the locations in the DB.  Could use a fixture for this.

        def is_ajax():
            # Make our own fake ajax request
            return True
    
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        # Create an instance of a GET request.
        canada = Country.objects.get(name="Canada")
        ontario = State.objects.get(name="Ontario")
        toronto = City.objects.get(name="Toronto")
        northyork = Neighborhood.objects.get(name="North York")
        sanfran = City.objects.get(name="San Francisco")
        
        request = self.factory.get('/demoform', { "country" : canada.id})
        request.is_ajax = is_ajax
        def view1(request):
            form = DemoForm()
            self.assertEqual(len(form.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form.fields["state"].choices.queryset), 0)
            self.assertEqual(len(form.fields["city"].choices.queryset), 0)
            self.assertEqual(len(form.fields["neighborhood"].choices.queryset), 0)
            self.assertFalse(form.is_valid())
            # country = Canada
            form2 = form.ajaxRequest(request)
            self.assertEqual(len(form2.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form2.fields["city"].choices.queryset), 0)
            self.assertEqual(len(form2.fields["neighborhood"].choices.queryset), 0)            
            self.assertFalse(form2.is_valid())
            with self.assertRaises(Exception):
                form2.save() # ajax forms are not meant to be saved
        view1(request)

        request = self.factory.get('/demoform', { "country" : canada.id, "state" : ontario.id})
        request.is_ajax = is_ajax
        def view2(request):
            # country = Canada, state = Ontario
            form = DemoForm(request.GET)
            self.assertEqual(len(form.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form.fields["neighborhood"].choices.queryset), 0)
            self.assertFalse(form.is_valid())
            form2 = form.ajaxRequest(request)
            self.assertEqual(len(form2.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form2.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["neighborhood"].choices.queryset), 0)            
            self.assertFalse(form2.is_valid())
            with self.assertRaises(Exception):
                form2.save() # ajax forms are not meant to be saved
        view2(request)

        request = self.factory.get('/demoform', { "country" : canada.id, "state" : ontario.id, "city" : toronto.id, "neighborhood" : northyork.id })
        request.is_ajax = is_ajax
        def view3(request):
            # country = Canada, state = Ontario, city=Toronto, neighborhood=North York
            # This is the one fully valid case
            form = DemoForm(request.GET)
            self.assertEqual(len(form.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form.fields["neighborhood"].choices.queryset), 3)
            self.assertTrue(form.is_valid())
            form2 = form.ajaxRequest(request)
            self.assertEqual(len(form2.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form2.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["neighborhood"].choices.queryset), 3)            
            self.assertFalse(form2.is_valid())
            with self.assertRaises(Exception):
                form2.save() # ajax forms are not meant to be saved
        view3(request)

        request = self.factory.get('/demoform', { "country" : canada.id, "state" : ontario.id, "city" : sanfran.id})
        request.is_ajax = is_ajax
        def view4(request):
            # country = Canada, state = Ontario, city=San Francisco
            # Should ignore San Francisco and show valid choices for Ontario
            form = DemoForm(request.GET)
            self.assertEqual(len(form.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form.fields["neighborhood"].choices.queryset), 7) #should be 0, this is invalid
            self.assertFalse(form.is_valid())
            form2 = form.ajaxRequest(request)
            self.assertEqual(len(form2.fields["country"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["state"].choices.queryset), 2)
            self.assertEqual(len(form2.fields["city"].choices.queryset), 3)
            self.assertEqual(len(form2.fields["neighborhood"].choices.queryset), 0)            
            self.assertFalse(form2.is_valid())
            with self.assertRaises(Exception):
                form2.save() # ajax forms are not meant to be saved
        view4(request)
