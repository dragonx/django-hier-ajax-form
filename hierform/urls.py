from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
                       ('^demoform$', 'hierform.views.demoform'),
                       ('^djhform.js$', 'hierform.views.javascript')
)