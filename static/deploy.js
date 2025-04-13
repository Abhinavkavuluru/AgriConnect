const hre = require("hardhat");

async function main() {
  // Get the first two accounts from Hardhat's local node
  const [deployer, buyer] = await hre.ethers.getSigners();
  console.log("Deploying contract with account:", deployer.address);

  // Define contract parameters
  const Price = hre.ethers.parseEther("0.1"); // ✅ Correct for Ethers v6
  const Quantity = 100; // Example: 100 kg of wheat
  const ContractYears = 3; // ✅ New: Contract duration in years

  // Deploy contract
  const Contract = await hre.ethers.getContractFactory("FarmerBuyerContract");
  const contract = await Contract.deploy(buyer.address, Price, Quantity, ContractYears);

  await contract.waitForDeployment(); // ✅ Wait for contract to be deployed

  console.log("Contract deployed at:", await contract.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
