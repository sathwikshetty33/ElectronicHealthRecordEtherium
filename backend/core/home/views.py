from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from web3 import Web3
import json
import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from web3 import Web3
from django.conf import settings
import hashlib
import time
from .serialzers import *
from web3 import Web3

address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"  
checksum_address = Web3.to_checksum_address(address) 

print(checksum_address)  

with open(r'/Volumes/T7/untitled folder 12/ElectronicHealthRecordEtherium/backend/core/home/abi.json', "r") as abi_file:
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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_list(request):
    doctors = doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

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

# Hospital Document APIs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hospital_document_create(request):
    try:
        # Handle file upload to cloud storage
        file = request.FILES.get('document')
        cloud_url = upload_to_cloud(file)  # Implement this method
        
        # Generate document hash
        doc_hash = Web3.keccak(text=cloud_url)
        
        # Create Django record
        serializer = HospitalDocumentSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(document_hash=doc_hash.hex())
            
            # Add to blockchain
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