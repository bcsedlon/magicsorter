from django.conf.urls import url, include

from .views import CardDelete

from . import views

#from .models import InstrumentList
#from .views import InstrumentCreate, InstrumentUpdate, 
#from .views import InstrumentDelete, RuleDelete, PeriodDelete

urlpatterns = [
    url(r'^$', views.cards, name='cards'),
    url(r'^(?P<sort>-*[a-z]+)/$', views.cards, name='cards'),
    url(r'^card/(?P<pk>[0-9]+)/$', views.card, name='card'),
    url(r'^card_delete/(?P<pk>[0-9]+)/$', CardDelete.as_view(), name='card_delete'),
    
    url(r'^scan_delete/(?P<pk>[0-9]+)/$', views.scan_delete, name='scan_delete'),
    
]