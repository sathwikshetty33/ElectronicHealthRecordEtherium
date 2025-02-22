from rest_framework import serializers
from .models import *
class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = doctor
        fields = '__all__'

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = hospital
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = patient
        fields = '__all__'

class HospitalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = hospitalDocument
        fields = '__all__'

class PatientDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = patientDocument
        fields = '__all__'