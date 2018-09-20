from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r'^my_index/$', my_index, name='my_index'),
    url(r'^register/$', register, name='register'),
    url(r'^my_login_v1/$', my_login_v1, name='my_login_v1'),
    url(r'^new_logout/$', new_logout, name='new_logout'),
    url(r'^active/(.+)', active, name='active'),
    url(r'^get_verify_img', get_verify_img, name='get_verify_img'),
    url(r'^my_person/$', my_person, name='my_person'),
    url(r'^my_modify/$',my_modify,name='my_modify'),

]