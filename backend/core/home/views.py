from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from web3 import Web3
import json
import os
from .models import *
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from web3 import Web3
from django.conf import settings
from django.db.models import Q
import hashlib
import time
from .serialzers import *
from web3 import Web3
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"  
checksum_address = Web3.to_checksum_address(address) 

print(checksum_address)  

with open(r'/home/sathwik/EHR/backend/core/home/abi.json', "r") as abi_file:
    contract_abi = json.load(abi_file)


LOCAL_NODE_URL = "http://127.0.0.1:8545"  
web3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))


CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3"  
contract = web3.eth.contract(address=Web3.to_checksum_address(address), abi=contract_abi)

class ContractOwnerView(APIView):
    def get(self, request):
        try:
            owner_address = contract.functions.own().call()
            return Response({"owner": owner_address})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
class HospitalLogin(APIView):
        authentication_classes = [] # No authentication for login endpoint
        permission_classes = [AllowAny]
        def post(self, request):
            data = request.data
            serializer=HospitalLoginSerializer(data=data)
            if not serializer.is_valid():
                return Response({"some error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            username = serializer.data['username']
            password = serializer.data['password']
            add = serializer.data['address']
            us = authenticate(username=username,password=password)
            if us is None:
                return  Response({
                    "error" : "Invalid username and password"
                },status=status.HTTP_401_UNAUTHORIZED)
            d = hospital.objects.filter(user=us).first()
            if d is None:
                return  Response({
                    "error" : "You are not Hospital register as one"
                },status=status.HTTP_401_UNAUTHORIZED)
            d = hospital.objects.filter(user=us,address=add).first()
            if d is None:
                return  Response({
                    "error" : "Incorrect metamask address"
                },status=status.HTTP_401_UNAUTHORIZED)
            token,_ = Token.objects.get_or_create(user=us)
            return Response({
                "token" : token.key,
                "hospId" : d.id,
            },status=status.HTTP_200_OK)
        
@method_decorator(csrf_exempt, name='dispatch')
class DoctorLogin(APIView):
        authentication_classes = [] # No authentication for login endpoint
        permission_classes = [AllowAny]
        def post(self, request):
            
            data = request.data
            serializer=HospitalLoginSerializer(data=data)
            if not serializer.is_valid():
                return Response({"some error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            username = serializer.data['username']
            password = serializer.data['password']
            add = serializer.data['address']
            us = authenticate(username=username,password=password)
            if us is None:
                return  Response({
                    "error" : "Invalid username and password"
                },status=status.HTTP_401_UNAUTHORIZED)
            d = doctor.objects.filter(user=us).first()
            if d is None:
                return  Response({
                    "error" : "You are not Doctor register as one"
                },status=status.HTTP_401_UNAUTHORIZED)
            d = doctor.objects.filter(user=us,address=add).first()
            if d is None:
                return  Response({
                    "error" : "Incorrect metamask address"
                },status=status.HTTP_401_UNAUTHORIZED)
            token,_ = Token.objects.get_or_create(user=us)
            return Response({
                "token" : token.key,
                "docId" : d.id
            },status=status.HTTP_200_OK)
class PatientLogin(APIView):
        authentication_classes = [] # No authentication for login endpoint
        permission_classes = [AllowAny]
        def post(self, request):
            data = request.data
            serializer=PatientLoginSerializer(data=data)
            if not serializer.is_valid():
                return Response({"some error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            username = serializer.data['username']
            password = serializer.data['password']
            us = authenticate(username=username,password=password)
            if us is None:
                return  Response({
                    "error" : "Invalid username and password"
                },status=status.HTTP_401_UNAUTHORIZED)
            d = patient.objects.filter(user=us).first()
            if d is None:
                return  Response({
                    "error" : "You are not a user register as one"
                },status=status.HTTP_401_UNAUTHORIZED)
            token,_ = Token.objects.get_or_create(user=us)
            return Response({
                "token" : token.key,
                "patId" : d.id,
            },status=status.HTTP_200_OK)    
class GetDoctors(APIView):
    def get(self, request,id):
        try:
            user_hospital = hospital.objects.get(id=id)
        except hospital.DoesNotExist:
            return Response({"error": "Hospital does not exsist"}, status=status.HTTP_404_NOT_FOUND)
        hospital_doctors = HospitalDoctors.objects.filter(hospital=user_hospital)
        doctor_ids = hospital_doctors.values_list('doctor_id', flat=True)
        doctors = doctor.objects.filter(id__in=doctor_ids)
        doctor_serializer = DoctorSerializer(doctors, many=True)
        return Response({"doctors": doctor_serializer.data}, status=status.HTTP_200_OK)
class HospitalDashboard(APIView):
    def get(self, request, id):
        try:
            user_hospital = hospital.objects.get(id=id)
        except hospital.DoesNotExist:
            return Response({"error": "Hospital does not exsist"}, status=status.HTTP_404_NOT_FOUND)
        hosp_serializer = HospitalSerializer(user_hospital)
        print(hosp_serializer.data)
        return Response({"hospital": hosp_serializer.data}, status=status.HTTP_200_OK)
class PatientDashboard(APIView):
    def get(self, request,id):
        try:
            pat = patient.objects.get(id=id)
        except patient.DoesNotExist:
            return Response({"error": "patient does nott exist."}, status=status.HTTP_404_NOT_FOUND)
        pat_serializer = PatientSerializer(pat)
        return Response({"patient": pat_serializer.data}, status=status.HTTP_200_OK)
class DoctorDashboard(APIView):
    def get(self, request,id):
        try:
            doc = doctor.objects.get(id=id)
        except doctor.DoesNotExist:
            return Response({"error": "Doctor does not exist."}, status=status.HTTP_404_NOT_FOUND)
        doc_serializer = DoctorSerializer(doc)
        return Response({"doctor": doc_serializer.data}, status=status.HTTP_200_OK)
class PatientDoc(APIView):
    def get(self,request,id):
        try: 
            pat = patient.objects.get(id=id)
        except patient.DoesNotExist:
            return Response({"error": "Patient does not exist."}, status=status.HTTP_404_NOT_FOUND)
        patd = patientDocument.objects.filter(patient=pat)
        patd_serializer = PatientPersonalDocumentSerializer(patd,many=True)
        try: 
            hospd = hospitalLedger.objects.get(patient=pat)
        except hospitalLedger.DoesNotExist:
            return Response({"error": "No hospital document found for this patient."}, status=status.HTTP_404_NOT_FOUND)
        hosp_d = hospitalDocument.objects.filter(hospitalLedger = hospd)
        hosp_d_serializer = PatientHospitalDocumentSerializer(hosp_d, many=True)
        context = {
            "patient": patd_serializer.data,
            "hospital": hosp_d_serializer.data,
            
        }
        return Response(context, status=status.HTTP_200_OK)
class getPatientDocStatus(APIView):
    def get(self, request, id):
        try:
            patd = patientDocument.objects.get(id=id)
        except patientDocument.DoesNotExist:
            return Response({"error": "Patient document does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if patd.isPrivate == False:
            return Response(status=status.HTTP_200_OK)
        try:
            tok = request.COOKIES.get('authToken')
        except KeyError:
            return Response({"error": "Authentication token not found"}, status=status.HTTP_403_FORBIDDEN)
        try:
            token = Token.objects.get(key=tok)
        except Token.DoesNotExist:
            return Response({"error": "Invalid authentication token"}, status=status.HTTP_403_FORBIDDEN)
        if token.user!= patd.patient.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)
class checkPatient(APIView):
    def get(self, request, id):
        try:
            tok = request.COOKIES.get('authToken')
        except KeyError:
            return Response({"error": "Authentication token not found"}, status=status.HTTP_403_FORBIDDEN)
        try:
            token = Token.objects.get(key=tok)
        except Token.DoesNotExist:
            return Response({"error": "Invalid authentication token"}, status=status.HTTP_403_FORBIDDEN)
        try:
            patd = patient.objects.get(id=id)
        except patient.DoesNotExist:
            return Response({"error": "Patient does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if token.user!= patd.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)
class checkHospital(APIView):
    def get(self, request, id):
        try:
            tok = request.COOKIES.get('authToken')
        except KeyError:
            return Response({"error": "Authentication token not found"}, status=status.HTTP_403_FORBIDDEN)
        try:
            token = Token.objects.get(key=tok)
        except Token.DoesNotExist:
            return Response({"error": "Invalid authentication token"}, status=status.HTTP_403_FORBIDDEN)
        try:
            patd = hospital.objects.get(id=id)
        except hospital.DoesNotExist:
            return Response({"error": "hospital does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if token.user!= patd.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)

class HospitalRoleCheckAPIView(APIView):
    """
    API endpoint to check if the authenticated user is associated with a hospital
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def get(self, request):
        try:
            user_hospital = hospital.objects.get(user=request.user)
            return Response({'hospital' : user_hospital.name},status=status.HTTP_200_OK)
        except hospital.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class HospitalLedgerAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if user is a hospital
        try:
            user_hospital = hospital.objects.get(user=request.user)
        except hospital.DoesNotExist:
            return Response({
                'detail': 'Only hospitals can register patients'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prepare data for serializer
        data = request.data.copy()
        data['hospital'] = user_hospital.id
        
        # Validate that the patient and doctor exist
        try:
            patient_obj = patient.objects.get(id=data.get('patient'))
            doctor_obj = doctor.objects.get(id=data.get('doctor'))
        except (patient.DoesNotExist, doctor.DoesNotExist):
            return Response({
                'detail': 'Invalid patient or doctor'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the ledger entry
        serializer = HospitalLedgerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class PatientSearchAPIView(APIView):
    """
    API endpoint for searching patients
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) < 2:
            return Response([])
        
        patients = patient.objects.filter(
            Q(name__icontains=query) | 
            Q(bloodGroup__icontains=query) |
            Q(contact__icontains=query)
        )[:10]  # Limit to 10 results
        
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)


class DoctorSearchAPIView(APIView):
    """
    API endpoint for searching doctors
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) < 2:
            return Response([])
        
        doctors = doctor.objects.filter(
            Q(name__icontains=query) |
            Q(license__icontains=query) |
            Q(location__icontains=query)
        )[:10]  
        
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

class hospitalPatients(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user_hospital = hospital.objects.get(user=request.user)
        except hospital.DoesNotExist:
            return Response({
                'detail': 'Only hospitals can view patients'
            }, status=status.HTTP_403_FORBIDDEN)
            
        patients = hospitalLedger.objects.filter(hospital=user_hospital)
        serializer = HospitalLedgerWithNestedSerializer(patients, many=True)
        
        return Response({
            'patients': serializer.data
        })

class hospitalDocumetsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        try:
            user_hospital = hospital.objects.get(user=request.user)
        except hospital.DoesNotExist:
            return Response({
                'detail': 'Only hospitals can view documents'
            }, status=status.HTTP_403_FORBIDDEN)
        try:
            pat = hospitalLedger.objects.get(id=id)
        except hospitalLedger.DoesNotExist:
            return Response({
                'detail': 'Ledger  does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            documents = hospitalDocument.objects.filter(hospitalLedger=pat)
        except hospitalDocument.DoesNotExist:
            return Response({
                'detail': 'No documents found'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = HospitalDocumentSerializer(documents, many=True)
        
        return Response({
            'documents': serializer.data
        })


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def doctor_create(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, pk):
    doc = get_object_or_404(doctor, pk=pk)
    
    if request.method == 'GET':
        serializer = DoctorSerializer(doc)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DoctorSerializer(doc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hospital_document_create(request):
    try:
        # Handle file upload to cloud storage
        file = request.FILES.get('document')
        cloud_url = upload_to_cloud(file)  # Implement this method
        doc_hash = Web3.keccak(text=cloud_url)
        
        serializer = HospitalDocumentSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(document_hash=doc_hash.hex())
            
            contract = get_contract()
            tx = contract.functions.addHospitalDocument(
                request.data['hospital_id'],
                request.data['patient_id'],
                doc_hash,
                instance.id,
                int(time.time()),
                not request.data.get('isPublic', False)
            ).transact({'from': settings.DEFAULT_ACCOUNT})
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_hospital_access(request, doc_id):
    document = get_object_or_404(hospitalDocument, pk=doc_id)
    hospital_id = request.data.get('hospital_id')
    
    try:
        contract = get_contract()
        tx = contract.functions.giveHospitalDocumentAccess(
            document.hospitalLedger.hospital.id,
            document.id,
            hospital_id
        ).transact({'from': settings.DEFAULT_ACCOUNT})
        
        documentAcess.objects.create(
            doc=document,
            to_id=hospital_id,
            sanctioned=True
        )
        
        return Response({'status': 'access granted'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Patient Document APIs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def patient_document_create(request):
    try:
        # Handle file upload to cloud storage
        file = request.FILES.get('document')
        cloud_url = upload_to_cloud(file)  # Implement this method
        
        # Generate document hash
        doc_hash = Web3.keccak(text=cloud_url)
        
        # Create Django record
        serializer = PatientDocumentSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(document_hash=doc_hash.hex())
            
            # Add to blockchain
            contract = get_contract()
            tx = contract.functions.addPatientDocument(
                request.data['patient_id'],
                instance.id,
                doc_hash,
                int(time.time()),
                not request.data.get('isPublic', False)
            ).transact({'from': settings.DEFAULT_ACCOUNT})
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_document_visibility(request, doc_id):
    document = get_object_or_404(patientDocument, pk=doc_id)
    is_private = request.data.get('is_private', True)
    
    try:
        contract = get_contract()
        tx = contract.functions.changePatientDocumentsVisibility(
            document.id,
            is_private,
            document.patient.id
        ).transact({'from': settings.DEFAULT_ACCOUNT})
        
        document.isPublic = not is_private
        document.save()
        
        return Response({'status': 'visibility updated'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)