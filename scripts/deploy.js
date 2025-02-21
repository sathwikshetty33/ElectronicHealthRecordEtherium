const hre = require("hardhat");

async function main() {
    const Contract = await hre.ethers.getContractFactory("HealthRecordSystem"); // Replace with your contract name
    const contract = await Contract.deploy(); // Deploying the contract

    await contract.waitForDeployment(); // Wait until deployment is completed

    console.log("Contract deployed to:", await contract.getAddress());
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
