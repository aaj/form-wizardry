from django.conf.urls import patterns, include, url
from django.contrib import admin

from myapp.views import *
from myapp.forms import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wizardry.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', 'myapp.views.login_view', name='login'),
    url(r'^test/', 'myapp.views.test_view', name='test'),
    url(r'^contacts/', ContactWizard.as_view(FORMS), name='contacts'),
    url(r'^car/', 'myapp.views.car_view', name='car'),
)
