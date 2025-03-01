from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('',views.loginView,name='login'),
    path('doctor-dashboard/<int:id>',views.doctorDashboard,name='doctor-dashboard'),
    path('hospital-dashboard/<int:id>',views.hospitalDashboard,name='hospital-dashboard'),
]