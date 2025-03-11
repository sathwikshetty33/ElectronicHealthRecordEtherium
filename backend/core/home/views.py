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

address = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"  
checksum_address = Web3.to_checksum_address(address) 

print(checksum_address)  

with open(r'/home/sathwik/EHR/backend/core/home/abi.json', "r") as abi_file:
    contract_abi = json.load(abi_file)


LOCAL_NODE_URL = "http://127.0.0.1:8545"  
web3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))


CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3"  
contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)

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
            print(add)
            us = authenticate(username=username,password=password)
            if us is None:
                return  Response({
                    "error" : "Invalid username and password"
                },status=status.HTTP_401_UNAUTHORIZED)
            try:
                d = hospital.objects.get(user=us)
                print(d.address)
            except hospital.DoesNotExist:
                return  Response({
                    "error" : "You are not Hospital register as one"
                },status=status.HTTP_401_UNAUTHORIZED)
            try:
                d = hospital.objects.get(user=us,address=add)
            except hospital.DoesNotExist:
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
            hospd = hospitalLedger.objects.filter(patient=pat)
        except hospitalLedger.DoesNotExist:
            return Response({"error": "No hospital document found for this patient."}, status=status.HTTP_404_NOT_FOUND)
        hosp_d = hospitalDocument.objects.filter(hospitalLedger__in = hospd)
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
    
class getHospitalDocStatus(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request, id):
        try:
            patd = hospitalDocument.objects.get(id=id)
        except hospitalDocument.DoesNotExist:
            return Response({"error": "Hospital document does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if patd.isPrivate == False:
            return Response(status=status.HTTP_200_OK)
        if patd.hospitalLedger.hospital.user == request.user:
            return Response(status=status.HTTP_200_OK)
        if patd.hospitalLedger.patient.user == request.user:
            return Response(status=status.HTTP_200_OK)
        return Response({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
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
        if pat.hospital != user_hospital:
            return Response({
                'detail': 'Unauthorized access'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = HospitalDocumentSerializer(documents, many=True)
        
        return Response({
            'documents': serializer.data
        })

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

class UploadToIPFS(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            pat = patient.objects.get(user=request.user)
        except patient.DoesNotExist:
            return Response({
                'detail': 'Only patients can upload documents'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if 'file' not in request.FILES or 'name' not in request.data:
            return Response({"error": "File and name are required"}, status=400)

        file = request.FILES["file"]
        name = request.data["name"]

        # Upload to IPFS
        try:
            pinata_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {
                "pinata_api_key": settings.PINATA_API_KEY,
                "pinata_secret_api_key": settings.PINATA_SECRET_KEY,
            }
            files = {"file": (name, file.read())}

            response = requests.post(pinata_url, headers=headers, files=files)

            if response.status_code != 200:
                return Response({"error": f"Failed to upload to IPFS: {response.text}"}, status=500)
                
            ipfs_data = response.json()
            cid = ipfs_data["IpfsHash"]
        except Exception as e:
            return Response({"error": f"IPFS upload error: {str(e)}"}, status=500)

        # Store in Blockchain
        try:
            web3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))
            
            # Verify connection to blockchain
            if not web3.is_connected():
                return Response({"error": "Cannot connect to Ethereum node"}, status=500)
            
            # Verify contract address format
            try:
                contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
            except ValueError:
                return Response({"error": f"Invalid contract address format: {address}"}, status=400)
                
            # Create contract instance
            contract = web3.eth.contract(address=contract_address, abi=contract_abi)
            
            # Verify checksum_address exists and is valid
            try:
                sender_address = Web3.to_checksum_address(checksum_address)
                if web3.eth.get_balance(sender_address) == 0:
                    return Response({"error": "Sender account has no balance"}, status=400)
            except ValueError:
                return Response({"error": f"Invalid sender address format: {checksum_address}"}, status=400)
            owner = contract.functions.own().call()  # Assuming there's an owner() function
            if owner.lower() != sender_address.lower():
                return Response({"error": "Sender is not the contract owner"}, status=403)
            # Get current timestamp from blockchain
            current_timestamp = int(web3.eth.get_block('latest')['timestamp'])
            patd = patientDocument.objects.create(
                name=name,
                patient=pat,
                hash=cid,
            )
            patd.save()
            #     function addPatientDocument(uint _patid,uint _docid, string memory _hash,uint256 _timestamp,bool _isPrivate) onlyOwner external {
        # patientDocuments[_docid] = PatientDocument(_hash,_docid,_timestamp,_patid,_isPrivate);
        # emit DocumentAdded(_docid, _hash, false);
            tx_hash = contract.functions.addPatientDocument(
                pat.id,patd.id, cid, current_timestamp, False
            ).transact({'from': sender_address})
            print(pat.id,patd.id)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            event_signature = web3.keccak(text="DocumentAdded(uint256,string,bool)").hex()
            for log in receipt.logs:
                if log['topics'][0].hex() == event_signature:
                    print("DocumentAdded event found:", log)
            if not receipt.status:
                return Response({"error": "Transaction failed"}, status=500)
                
            # Save to database only after blockchain confirmation
           
            
            return Response({
                "message": "File uploaded to IPFS and stored on Blockchain",
                "cid": cid,
                "url": f"https://gateway.pinata.cloud/ipfs/{cid}",
                "transaction": receipt.transactionHash.hex()
            })
            
        except Exception as e:
            return Response({"error": f"Blockchain error: {str(e)}"}, status=500)

class UploadToIPFSHospital(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            # Verify that the user is a hospital
            hosp = hospital.objects.get(user=request.user)
        except hospital.DoesNotExist:
            return Response({
                'detail': 'Only hospitals can upload documents'
            }, status=403)

        # Validate required fields
        if 'file' not in request.FILES or 'name' not in request.data or 'hospitalLedger' not in request.data:
            return Response({"error": "File, name, and ledgerId are required"}, status=400)

        file = request.FILES["file"]
        name = request.data["name"]
        ledger_id = request.data["hospitalLedger"]

        # Validate ledger existence
        try:
            ledger = hospitalLedger.objects.get(id=ledger_id)
        except hospitalLedger.DoesNotExist:
            return Response({'detail': 'Ledger does not exist'}, status=404)

        # Validate hospital's blockchain address
        hospital_address = hosp.address
        if not hospital_address:
            return Response({"error": "Hospital has no blockchain address configured"}, status=400)

        # Upload file to IPFS via Pinata
        try:
            pinata_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {
                "pinata_api_key": settings.PINATA_API_KEY,
                "pinata_secret_api_key": settings.PINATA_SECRET_KEY,
            }
            files = {"file": (name, file.read())}

            response = requests.post(pinata_url, headers=headers, files=files)

            if response.status_code != 200:
                return Response({"error": f"Failed to upload to IPFS: {response.text}"}, status=500)

            ipfs_data = response.json()
            cid = ipfs_data["IpfsHash"]

            # Save document metadata in the database
            hosp_doc = hospitalDocument.objects.create(
                name=name,
                hospitalLedger=ledger,
            )
            hosp_doc.save()
            document_id = hosp_doc.id  # Generate a unique document ID
        except Exception as e:
            return Response({"error": f"IPFS upload error: {str(e)}"}, status=500)

        # Store document details on the blockchain
        try:
            web3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))

            # Verify connection to the Ethereum node
            if not web3.is_connected():
                return Response({"error": "Cannot connect to Ethereum node"}, status=500)

            # Verify contract address format
            try:
                contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
            except ValueError:
                return Response({"error": f"Invalid contract address format: {CONTRACT_ADDRESS}"}, status=400)

            # Create contract instance
            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            # Verify hospital address is valid
            # try:
            #     sender_address = Web3.to_checksum_address(hospital_address)
            #     if web3.eth.get_balance(sender_address) == 0:
            #         return Response({"error": "Hospital account has no balance for transaction"}, status=400)
            # except ValueError:
            #     return Response({"error": f"Invalid hospital address format: {hospital_address}"}, status=400)

            # Get the latest block timestamp
            current_timestamp = int(web3.eth.get_block('latest')['timestamp'])

            # Call the addHospitalDocument function
            tx_hash = contract.functions.addHospitalDocument(
                ledger.patient.id, cid, document_id, current_timestamp, False
            ).transact({'from': checksum_address})

            # Wait for the transaction receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            # Check if the transaction was successful
            if not receipt.status:
                return Response({"error": "Transaction failed"}, status=500)



            # Return success response
            document_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
            return Response(
                status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Blockchain error: {str(e)}"}, status=500)
class PatientDocumentVisibiltyStatus(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self,request,id):
        try:
            pat = patientDocument.objects.get(id=id)
        except patientDocument.DoesNotExist:
            return Response(status=404)
        if request.user == pat.patient.user:
            return Response({
                'visible': True
            }, status=200)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
class PatientDocumentView(APIView):
    """
    API view to get patient document from blockchain and redirect to IPFS
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, patient_id, doc_id):
        print(f"User: {request.user.username}, Patient ID: {patient_id}, Doc ID: {doc_id}")
        
        try:
            # Get the document object from your database
            doc = patientDocument.objects.get(id=doc_id)
            print(f"Document found: {doc.id}, Patient: {doc.patient.id}")
            
            # Verify the document belongs to the requested patient
            if doc.patient.id != patient_id:
                print(f"Document patient mismatch: {doc.patient.id} != {patient_id}")
                return Response({
                    'detail': 'Document does not belong to this patient'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Connect to blockchain
            w3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))
            if not w3.is_connected():
                print("Failed to connect to Ethereum node")
                return Response({"error": "Blockchain connection failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)
            print(f"Connected to contract at {address}")
        #         function getPatientDocument(uint _patid,uint _docid) view onlyOwner external returns(string memory){
        # if (patientDocuments[_docid].isPrivate){
        #     require(patientDocumentAuthorizations[_docid][msg.sender] ||  _patid == patientDocuments[_docid].patientId, "Access denied");
        # }
        # return patientDocuments[_docid].add;
            try:
                document_cid = contract.functions.getPatientDocument(
                    int(doc.patient.id),
                    int(doc_id)
                ).call({'from': checksum_address})
                print(f"Contract returned CID: {document_cid}")
            except Exception as contract_error:
                print(f"Contract call failed: {str(contract_error)}")
                return Response({"error": f"Blockchain contract error: {str(contract_error)}"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not document_cid:
                print("Empty CID returned from contract")
                return Response({
                    "error": "Document not found or access denied"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Construct complete IPFS URL with Pinata gateway
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{document_cid}"
            print(f"Returning IPFS URL: {ipfs_url}")
            
            # Return the URL in the response
            return Response({"url": ipfs_url}, status=status.HTTP_200_OK)
                
        except patientDocument.DoesNotExist:
            print(f"Document with ID {doc_id} not found in database")
            return Response({
                'detail': 'Document does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print("Exception in view:")
            traceback.print_exc()
            return Response({
                "error": f"Failed to retrieve document: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HospitalDocumentView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request,  doc_id):
        
        try:
            # Get the document object from your database
            doc = hospitalDocument.objects.get(id=doc_id)
            if doc.isPrivate:
                if doc.hospitalLedger.patient.user != request.user:
                    if doc.hospitalLedger.hospital.user != request.user: 
                        print(f"Document patient mismatch: {doc.id} ")
                        return Response({
                            'detail': 'Document does not belong to this patient'
                        }, status=status.HTTP_403_FORBIDDEN)
                
            if request.user == doc.hospitalLedger.patient.user:
                add = checksum_address
            else:
                add = doc.hospitalLedger.hospital.address
            w3 = Web3(Web3.HTTPProvider(LOCAL_NODE_URL))
            if not w3.is_connected():
                print("Failed to connect to Ethereum node")
                return Response({"error": "Blockchain connection failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)
            print(f"Connected to contract at {address}")
            try:
                document_cid = contract.functions.getHospitalDocument(
                    int(doc_id)
                ).call({'from': checksum_address})
                print(f"Contract returned CID: {document_cid}")
            except Exception as contract_error:
                print(f"Contract call failed: {str(contract_error)}")
                return Response({"error": f"Blockchain contract error: {str(contract_error)}"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not document_cid:
                print("Empty CID returned from contract")
                return Response({
                    "error": "Document not found or access denied"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Construct complete IPFS URL with Pinata gateway
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{document_cid}"
            print(f"Returning IPFS URL: {ipfs_url}")
            
            # Return the URL in the response
            return Response({"url": ipfs_url}, status=status.HTTP_200_OK)
                
        except patientDocument.DoesNotExist:
            print(f"Document with ID {doc_id} not found in database")
            return Response({
                'detail': 'Document does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print("Exception in view:")
            traceback.print_exc()
            return Response({
                "error": f"Failed to retrieve document: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)















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