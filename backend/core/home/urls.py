from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('hospital-login/',HospitalLogin.as_view(),name='hoslog'),
    path('patient-login/',PatientLogin.as_view(),name='patlog'),
    path('doctor-login/',DoctorLogin.as_view(),name='doclog'),
    path('hospital-dashboard/<int:id>',HospitalDashboard.as_view(),name='doc-dash'),
    path('patient-dashboard/<int:id>',PatientDashboard.as_view(),name='doc-dash'),
    path('doctor-dashboard/<int:id>',DoctorDashboard.as_view(),name='doc-dash'),
    path('doctors/<int:id>', GetDoctors.as_view(), name='doctor-list'),
    path('doctors/create/', doctor_create, name='doctor-create'),
    path('doctors/<int:pk>/', doctor_detail, name='doctor-detail'),
    path('hospital-documents/create/', hospital_document_create, name='hospital-document-create'),
    path('hospital-documents/<int:doc_id>/grant-access/', grant_hospital_access, name='grant-hospital-access'),
    path('patient-documents/create/', patient_document_create, name='patient-document-create'),
    path('patient-documents/<int:doc_id>/visibility/', change_document_visibility, name='change-document-visibility'),
    path('patient-documents/<int:id>/',PatientDoc.as_view(),name='patient-documents'),
    path('patient-document-access/<int:id>/',getPatientDocStatus.as_view(),name='patient-doc-status'),
]