'''
This simply contains some models representing hierarchical location names. 

Use the init_db() function from the django shell to initialize some test data into the database.
'''

from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.name;
    
class State(models.Model):
    name = models.CharField(max_length=128)
    country = models.ForeignKey(Country)
    def __unicode__(self):
        return self.name;
    
class City(models.Model):
    name = models.CharField(max_length=128)
    state = models.ForeignKey(State)
    statename_dn = models.CharField(max_length=128) #:_dn indicates this is a denormalized field
    def __unicode__(self):
        return self.name;  
    def save(self):
        self.statename_dn = self.state.name
        super(City, self).save()
    
class Neighborhood(models.Model):
    name = models.CharField(max_length=128)
    city = models.ForeignKey(City)
    cityname_dn = models.CharField(max_length=128) #:_dn indicates this is a denormalized field
    statename_dn = models.CharField(max_length=128) #:_dn indicates this is a denormalized field
    def __unicode__(self):
        return self.name;
    def save(self):
        self.cityname_dn = self.city.name
        self.statename_dn = self.city.statename_dn
        super(Neighborhood, self).save()
    

def init_db():
    '''
    This method creates some test data in the DB for locations.
    So far I've only run it from the django shell::
    
        python manage.py shell
        >>> import djangoappengine.main
        >>> import location.models
        >>> location.models.init_db()
    '''
    data = { 'Canada' :  { 'Ontario' : { 'Toronto'   : ['North York', 'Scarborough', 'Mississauga'],
                                         'Waterloo'  : [],
                                         'Kitchener' : [] },
                           'British Columbia' : { 'Vancouver' : ['Downtown Vancouver', 'West Vancouver', 'Richmond']}
                         },
             'United States' : { 'California' : { 'San Francisco' : ['Mission', 'SoMa', 'Dogpatch', 'Inner Richmond', 'Outer Richmond', 'Inner Sunset', 'Outer Sunset'],
                                                  'San Mateo'     : [],
                                                  'Santa Clara'   : [],
                                                  'San Jose'      : [],
                                                  'Burlingame'    : [],
                                                  'Palo Alto'     : [],
                                                  'Mountain View' : [] },
                                 'New York'    : { 'New York'     : [] }
                                },
             'Hong Kong'     : { 'Hong Kong'  : { 'Hong Kong'     : ['Central', 'Admiralty', 'Causeway Bay', 'Tsim Sha Tsui', 'Hung Hom']}}
           }
    
    for country in data:
        newcountry = Country(name=country)
        newcountry.save()
        for state in data[country]:
            newstate = State(name=state, country=newcountry)
            newstate.save()
            for city in data[country][state]:
                newcity = City(name=city, state=newstate)
                newcity.save()
                for neighborhood in data[country][state][city]:
                    newneighborhood = Neighborhood(name=neighborhood, city=newcity)
                    newneighborhood.save()
                    
    print "Done."