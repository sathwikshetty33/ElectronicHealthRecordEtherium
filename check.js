const hre = require("hardhat");

async function main() {
  const Contract = await hre.ethers.getContractFactory("HealthRecordSystem");
  const contract = await Contract.attach("0x0165878a594ca255338adfa4d48449f69242eb8f");
  
  // Check document 7
  const document = await contract.patientDocuments(7);
  console.log("Document 7:", document);
  
  // Check authorization
  const auth = await contract.patientDocumentAuthorizations(7, "CALLER_ADDRESS");
  console.log("Authorization for caller:", auth);
}

main()
// Get the storage at the specific slot where patientDocuments[7] is stored
// You'll need to calculate the correct storage slot based on your contract's storage layout
const storageSlot = ethers.utils.keccak256(
  ethers.utils.defaultAbiCoder.encode(
    ['uint256', 'uint256'],
    [7, /* slot of patientDocuments mapping */]
  )
);

const data = await ethers.provider.getStorageAt(contract.address, storageSlot);
console.log("Storage data:", data);
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
    
  });