from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('hospital-login/',HospitalLogin.as_view(),name='hoslog'),
    path('patient-login/',PatientLogin.as_view(),name='patlog'),
    path('doctor-login/',DoctorLogin.as_view(),name='doclog'),

    path('doctors/', GetDoctors.as_view(), name='doctor-list'),
    path('doctors/create/', doctor_create, name='doctor-create'),
    path('doctors/<int:pk>/', doctor_detail, name='doctor-detail'),
    
    # Hospital Document URLs
    path('hospital-documents/create/', hospital_document_create, name='hospital-document-create'),
    path('hospital-documents/<int:doc_id>/grant-access/', grant_hospital_access, name='grant-hospital-access'),
    
    # Patient Document URLs
    path('patient-documents/create/', patient_document_create, name='patient-document-create'),
    path('patient-documents/<int:doc_id>/visibility/', change_document_visibility, name='change-document-visibility'),
]