from django.db import models
from django.contrib.auth.models import User

class doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    license = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

class hospital(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    license = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
class patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    bloodGroup = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    emergencyContact = models.CharField(max_length=100)
class hospitalLedger(models.Model):
    hospital = models.ForeignKey(hospital, on_delete=models.CASCADE)
    date = models.DateField()
    patient = models.ForeignKey(patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(doctor, on_delete=models.CASCADE)
    isDischarged = models.BooleanField(default=False)
class hospitalDocument(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    hospitalLedger = models.ForeignKey(hospitalLedger, on_delete=models.CASCADE)
    isPrivate = models.BooleanField(default=True)
class patientDocument(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    isPrivate = models.BooleanField(default=True)
class documentAcess(models.Model):
    doc = models.ForeignKey(hospitalDocument, on_delete=models.CASCADE)
    to = models.ForeignKey(hospital, on_delete=models.CASCADE)
    sanctioned = models.BooleanField(default=False)