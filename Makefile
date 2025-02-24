bcNode:
	npx hardhat node
bcDeploy:
	npx  hardhat run scripts/deploy.js --network localhost
phony:
	bcDeploy bcNode