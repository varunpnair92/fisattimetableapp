from django.urls import path
from django.urls import re_path as url#from django.urls import re_path as url 


from . import views

urlpatterns = [
    
    
    path('labdata', views.lab_allotment_view, name='labdata'),   
    path('laballot', views.allot_lab_slot, name='allot_lab_slot'),
    path('laballot_continue', views.allot_lab_slot_continue, name='allot_lab_slot_continue'),
    path('labexternal', views.labdetailsexternal, name='labexternal'),
    path('labdata_range', views.lab_allotment_range_view, name='labdata_range'),
    
   


                ]
