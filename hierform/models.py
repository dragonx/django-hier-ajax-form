from django.db import models
from fields import HierarchicalForeignKey
import location.models

class DemoModel(models.Model):
    '''
    This is a demo model for a hierarchical AJAX form.
    The name and address fields are dummy fields for demo purposes.
    The HierarchicalForeignKey allows the form to check the relationship between them.

    You can have other normal ForeignKeys to non-hierarchical data, and the form generation will ignore them.
    
    The order of the fields is important.  The top of the hierarchy needs to be at the top.
    If the order is inverted, modifying a higher field will not properly reset the lower fields in the form.
    '''
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    country = HierarchicalForeignKey(location.models.Country)
    state = HierarchicalForeignKey(location.models.State)
    city = HierarchicalForeignKey(location.models.City)
    neighborhood = HierarchicalForeignKey(location.models.Neighborhood, null=True, blank=True)
