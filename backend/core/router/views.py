from django.shortcuts import render

# Create your views here.
def loginView(request):
    return render(request, 'router/login.html')
def doctorDashboard(request, id):
    return render(request, 'router/doctorDashboard.html',{'id' : id})
def hospitalDashboard(request, id):
    return render(request, 'router/hospitalDashboard.html',{'id' : id})
def patientDashboard(request, id):
    return render(request, 'router/patientDashboard.html',{'id' : id})