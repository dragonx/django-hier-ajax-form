from fields import HierarchicalForm
from models import DemoModel

class DemoForm(HierarchicalForm):
    '''
    Demo form based on the demo model.
    All you have to do is inherit from HierarchicalForm
    '''        
    class Meta:
        model = DemoModel