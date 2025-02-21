// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract HealthRecordSystem {
    uint256 private hospitalDocumentsCount;
    uint256 private patientDocumentsCount;
    address public defaultAddress;

    struct HospitalDocument {
        bytes32 hash;
        address owner;
        uint256 documentId;
        string storageLocation;
        bool isPublic;
        uint256 timestamp;
        string documentType;   
        bool isActive;         
    }

    struct PatientDocument {
        bytes32 hash;
        uint256 documentId;
        bool isPublic;
        uint256 timestamp;
        string documentType;
        bool isActive;
    }

    mapping(uint256 => mapping(address => bool)) public hospitalDocumentAuthorizations;
    mapping(uint256 => mapping(address => bool)) public patientDocumentAuthorizations;
    
    mapping(uint256 => HospitalDocument) public hospitalDocuments;
    mapping(uint256 => PatientDocument) public patientDocuments;

    event DocumentAdded(uint256 indexed documentId, bytes32 hash, bool isHospital);
    event AccessGranted(uint256 indexed documentId, address indexed user);
    event AccessRevoked(uint256 indexed documentId, address indexed user);

    constructor() {
        defaultAddress = msg.sender;
        hospitalDocumentsCount = 0;
        patientDocumentsCount = 0;
    }

    modifier onlyOwner() {
        require(msg.sender == defaultAddress, "Not authorized");
        _;
    }

    modifier documentExists(uint256 documentId, bool isHospital) {
        if (isHospital) {
            require(documentId < hospitalDocumentsCount, "Hospital document does not exist");
        } else {
            require(documentId < patientDocumentsCount, "Patient document does not exist");
        }
        _;
    }
    function own() public view returns (address) {
        return defaultAddress;
    }
}
