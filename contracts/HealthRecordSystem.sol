// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract HealthRecordSystem {

    address public defaultAddress;

    struct HospitalDocument {
        bytes32 add;
        address hospital;
        uint256 documentId;
        uint256 patientId;
        uint256 time;    
        bool isPrivate;      
    }

    struct PatientDocument {
        bytes32 add;
        uint256 documentId;
        uint256 timestamp;
        uint256 patientId;
        bool isPrivate;
    }

    mapping(uint256 => mapping(address => bool)) hospitalDocumentAuthorizations;
    mapping(uint256 => mapping(address => bool)) patientDocumentAuthorizations;
    mapping(uint256 => address) hospitals;
    mapping(uint256 => HospitalDocument) hospitalDocuments;
    mapping(uint256 => PatientDocument) patientDocuments;
    event ChangedVisibility(uint256 documentId, bool isPrivate);
    event DocumentAdded(uint256 indexed documentId, bytes32 hash, bool isHospital);
    event AccessGranted(uint256 indexed documentId, address indexed user);
    event AccessRevoked(uint256 indexed documentId, address indexed user);
    event AddedHospital(uint indexed hospitalId, address indexed hospitalAddress);
    constructor() {
        defaultAddress = msg.sender;

    }

    modifier onlyOwner() {
        require(msg.sender == defaultAddress, "Not authorized");
        _;
    }
    modifier checkHospitalAddress(uint _id){
        require(hospitals[_id] == msg.sender, "Not authorized");
        _;
    }

    function own() public view returns (address) {
        return defaultAddress;
    }
    function giveHospitalDocumentAccess(uint hospId, uint _id, address _user) public checkHospitalAddress(hospId) {
        hospitalDocumentAuthorizations[_id][_user] = true;
        emit AccessGranted(_id, _user);
    }
    function givePatientDocumentAccess( uint _id, address _user) public onlyOwner {
        patientDocumentAuthorizations[_id][_user] = true;
        emit AccessGranted(_id, _user);
    }
    function revokePatientDocumentAccess( uint _id, address _user) public onlyOwner {
        patientDocumentAuthorizations[_id][_user] = false;
        emit AccessRevoked(_id, _user);
    }
    function addHospital (uint _id, address _address) onlyOwner external {
        require(hospitals[_id] == address(0), "Hospital already exists");
        hospitals[_id] = _address;
        emit AddedHospital( _id ,_address);
    }
    function revokeHospitalDocumentAccess(uint hospId, uint _id, address _user) public checkHospitalAddress(hospId) {
        hospitalDocumentAuthorizations[_id][_user] = false;
        emit AccessRevoked(_id, _user);
    }
    function addHospitalDocument(uint hospId,uint _patid, bytes32 _hash,uint256 _documentId,uint256 _timestamp,bool vis) external checkHospitalAddress(hospId) {
        hospitalDocuments[_documentId] = HospitalDocument(_hash,msg.sender,_documentId,_patid,_timestamp,vis);
        emit DocumentAdded(_documentId, _hash, true);
    }
    function addPatientDocument(uint _patid,uint _docid, bytes32 _hash,uint256 _timestamp,bool _isPrivate) onlyOwner external {
        patientDocuments[_docid] = PatientDocument(_hash,_docid,_timestamp,_patid,_isPrivate);
        emit DocumentAdded(_docid, _hash, false);
}
    function getPatientDocument(uint _patid,uint _docid) view onlyOwner external returns(bytes32){
        if (patientDocuments[_docid].isPrivate){
            require(patientDocumentAuthorizations[_docid][msg.sender] ||  _patid == patientDocuments[_docid].patientId, "Access denied");
        }
        return patientDocuments[_docid].add;
    }
    function getHospitalDocument(uint _docid) view external returns(bytes32){
        if (hospitalDocuments[_docid].isPrivate){
            require(hospitalDocumentAuthorizations[_docid][msg.sender] ||  hospitalDocuments[_docid].hospital == msg.sender, "Access denied");
        }
        return hospitalDocuments[_docid].add;
    }
    function changeHospitalDocumentsVisibility(uint _docid,bool vis,uint _patid)  external{
        require(_patid == hospitalDocuments[_docid].patientId, "Access denied");
        hospitalDocuments[_docid].isPrivate = vis;
        emit ChangedVisibility(_docid, vis);
    }
    function changePatientDocumentsVisibility(uint _docid,bool vis,uint _patid)  external{
        require(_patid == patientDocuments[_docid].patientId, "Access denied");
        patientDocuments[_docid].isPrivate = vis;
        emit ChangedVisibility(_docid, vis);
    }
}