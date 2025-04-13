const provider = new ethers.providers.JsonRpcProvider("http://127.0.0.1:8545"); // Connect to Hardhat Local Network
let signer;
let contractInstance;
const contractABI = [ 
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_buyer",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_price",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_quantity",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_contractYears",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "farmer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "buyer",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "price",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "quantity",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "contractYears",
        "type": "uint256"
      }
    ],
    "name": "ContractCreated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "buyer",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "paymentsMade",
        "type": "uint256"
      }
    ],
    "name": "PaymentMade",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "farmer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "buyer",
        "type": "address"
      }
    ],
    "name": "ProductDelivered",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "buyer",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "confirmDelivery",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "contractYears",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "farmer",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getPaymentsMade",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isContractComplete",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isPaid",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "makePayment",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "paymentsMade",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "price",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "quantity",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
    ];
const contractBytecode = "0x608060405234801561001057600080fd5b506040516104b63803806104b683398101604081905261002f916100be565b600080546001600160a01b031990811633908117909255600180546001600160a01b038716921682179055600284905560038390556004805460ff191690556040805192835260208301919091528101839052606081018290527ffab0e42748281d7ded0b8035c108061734a19fc87373b21ab917a4550826cbaf9060800160405180910390a1505050610101565b6000806000606084860312156100d357600080fd5b83516001600160a01b03811681146100ea57600080fd5b602085015160409095015190969495509392505050565b6103a6806101106000396000f3fe6080604052600436106100705760003560e01c80637150d8ae1161004e5780637150d8ae146100df578063a035b1fe14610117578063d811fcf01461012d578063d8d797001461014d57600080fd5b806317fc45e214610075578063209ebc081461009e5780635e10177b146100c8575b600080fd5b34801561008157600080fd5b5061008b60035481565b6040519081526020015b60405180910390f35b3480156100aa57600080fd5b506004546100b89060ff1681565b6040519015158152602001610095565b3480156100d457600080fd5b506100dd610155565b005b3480156100eb57600080fd5b506001546100ff906001600160a01b031681565b6040516001600160a01b039091168152602001610095565b34801561012357600080fd5b5061008b60025481565b34801561013957600080fd5b506000546100ff906001600160a01b031681565b6100dd610290565b6000546001600160a01b031633146101b45760405162461bcd60e51b815260206004820152601960248201527f4f6e6c79206661726d65722063616e2063616c6c20746869730000000000000060448201526064015b60405180910390fd5b60045460ff166102065760405162461bcd60e51b815260206004820152601860248201527f5061796d656e74206e6f7420726563656976656420796574000000000000000060448201526064016101ab565b600080546002546040516001600160a01b039092169281156108fc029290818181858888f19350505050158015610241573d6000803e3d6000fd5b50600054600154604080516001600160a01b0393841681529290911660208301527f7b2375ea59e583d947bfdaa1092d9c1f3b3a3bc8218ce55fb7976286ea48b32191015b60405180910390a1565b6001546001600160a01b031633146102ea5760405162461bcd60e51b815260206004820152601860248201527f4f6e6c792062757965722063616e2063616c6c2074686973000000000000000060448201526064016101ab565b600254341461032e5760405162461bcd60e51b815260206004820152601060248201526f125b98dbdc9c9958dd08185b5bdd5b9d60821b60448201526064016101ab565b6004805460ff19166001179055604080513381523460208201527f3a2d0e41c506b136330c6e5e0295ccbf0966daece99bfe7c89020cc01dbfb8d6910161028656fea264697066735822122065c7c2e329b39ebb0ffd231aaeaf2e19b00700cf34ffa9371a3e814b2799206c64736f6c634300081c0033"; // Add your compiled contract bytecode
const contractAddressInput = document.getElementById("contractAddress");

// Hardcoded contract address (optional, can be removed if deploying dynamically)

// ✅ Ensure the element exists before setting the value
if (contractAddressInput) {
    contractAddressInput.value = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
}

// Connect MetaMask

async function connectWallet() {
    if (!window.ethereum) {
        alert("MetaMask is required.");
        return;
    }
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
    signer = provider.getSigner(accounts[0]);
    console.log(`✔ Connected MetaMask account: ${accounts[0]}`);
}

// 🚀 Deploy Smart Contract (Farmer)
async function deployContract() {
  try {
      await connectWallet(); // Ensure MetaMask is connected

      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      const farmerAddress = accounts[0]; // ✅ Use the connected MetaMask account

      const ContractFactory = new ethers.ContractFactory(contractABI, contractBytecode, signer);

      const buyerAddress = document.getElementById("buyerWallet").value.trim();
      if (!buyerAddress || !ethers.utils.isAddress(buyerAddress)) {
          alert("Enter a valid buyer wallet address.");
          return;
      }
      const buyerEmail = document.getElementById("buyerEmail").value.trim();  // ✅ New Field for Buyer's Email
        if (!buyerEmail) {
            alert("Enter a valid buyer email.");
            return;
        }

      const priceInput = document.getElementById("price").value.trim();
      if (!priceInput || isNaN(priceInput) || Number(priceInput) <= 0) {
          alert("Enter a valid price.");
          return;
      }
      const price = ethers.utils.parseEther(priceInput);

      const quantityInput = document.getElementById("quantity").value.trim();
      if (!quantityInput || isNaN(quantityInput) || Number(quantityInput) <= 0) {
          alert("Enter a valid quantity.");
          return;
      }
      const quantity = Number(quantityInput);

      const contractYearsInput = document.getElementById("contractYears").value.trim();
      if (!contractYearsInput || isNaN(contractYearsInput) || Number(contractYearsInput) <= 0) {
          alert("Enter a valid contract duration in years.");
          return;
      }
      const contractYears = Number(contractYearsInput);

      const productType = document.getElementById("productType").value.trim();
      if (!productType) {
          alert("Enter a valid product type.");
          return;
      }

      console.log(`🚀 Deploying contract with Farmer: ${farmerAddress}, Buyer: ${buyerAddress}, Price: ${price.toString()}, Quantity: ${quantity}, Product Type: ${productType}, Years: ${contractYears}`);

      // ✅ Deploy Smart Contract with MetaMask Farmer Address
      contractInstance = await ContractFactory.deploy(buyerAddress, price, quantity, contractYears);
      await contractInstance.deployed();

      const contractAddress = contractInstance.address; 
      alert(`✅ Contract Deployed at: ${contractAddress}`);

      localStorage.setItem("contractAddress", contractAddress);
      localStorage.setItem("contractYears", contractYears); 

      const contractDisplayElement = document.getElementById("contractAddressDisplay");
      if (contractDisplayElement) {
          contractDisplayElement.innerText = `Contract Deployed at: ${contractAddress}`;
      }

      // ✅ Send contract details to Flask API for MySQL storage
      const response = await fetch("/deploy_contract", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              farmer_address: farmerAddress,  // ✅ Store dynamic farmer address
              buyer_address: buyerAddress,
              price: priceInput,
              quantity: quantity,
              contract_years: contractYears,
              product_type: productType,
              contract_address: contractAddress,
              buyer_email: buyerEmail
          })
      });

      const data = await response.json();
      if (data.error) {
          alert(`❌ Failed to store contract in database: ${data.error}`);
      } else {
          alert("✅ Contract stored in MySQL successfully!");
      }

  } catch (error) {
      console.error("❌ Error deploying contract:", error);
      alert("Failed to deploy contract. Check console for more details.");
  }
}



// 📌 Fetch Contract Details (Buyer)
async function fetchContractDetails() {
  try {
      const contractAddress = document.getElementById("contractAddress").value.trim();
      if (!contractAddress) {
          alert("Enter a valid contract address.");
          return;
      }

      // ✅ Fetch contract details from Flask API instead of blockchain
      const response = await fetch(`/fetch_contract_details?contract_address=${contractAddress}`);
      const data = await response.json();

      if (data.error) {
          alert(`❌ Failed to fetch contract details: ${data.error}`);
          return;
      }

      document.getElementById("contractDetails").innerHTML = `
          <p>👨‍🌾 Farmer Address: ${data.farmer}</p>
          <p>🛒 Buyer Address: ${data.buyer}</p>
          <p>💰 Price: ${data.price} ETH</p>
          <p>📦 Quantity: ${data.quantity} kg</p>
          <p>🌱 Product Type: ${data.product_type}</p>
          <p>📅 Contract Duration: ${data.contract_years} years</p>
          <p>💰 Payment Made: ${data.payment_made ? "✅ Yes" : "❌ No"}</p>
          <p>📆 Payment Completed Years: ${data.payment_completed_years} / ${data.contract_years} years</p>
          <p>📜 Order Accepted: ${data.order_accepted ? "✅ Yes" : "❌ No"}</p>
          <p>📦 Delivery Confirmed: ${data.delivery_confirmed ? "✅ Yes" : "❌ No"}</p>
      `;

  } catch (error) {
      console.error("❌ Failed to fetch contract details:", error);
      alert("❌ An error occurred while fetching contract details.");
  }
}



async function makePayment() {
  try {
      await connectWallet();

      const contractAddress = document.getElementById("contractAddress").value.trim();
      if (!contractAddress) {
          alert("Enter a valid contract address.");
          return;
      }

      let connectedAccount = await signer.getAddress();

      // ✅ Step 1: Ask Flask if payment is still allowed
      const checkResponse = await fetch("/check_payment_validity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              buyer_address: connectedAccount,
              contract_address: contractAddress
          })
      });

      const checkData = await checkResponse.json();
      if (checkData.error) {
          alert(`❌ Payment Failed: ${checkData.error}`);
          return;
      }

      // ✅ Step 2: Proceed with Blockchain Payment (Only if Flask allows)
      contractInstance = new ethers.Contract(contractAddress, contractABI, signer);
      const price = await contractInstance.price();
      console.log(`🚀 Making payment of: ${ethers.utils.formatEther(price)} ETH`);

      const tx = await contractInstance.makePayment({ value: price });
      await tx.wait();

      alert("✅ Payment successful!");

      // ✅ Step 3: Call Flask API to update MySQL
      const updateResponse = await fetch("/make_payment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              buyer_address: connectedAccount,
              contract_address: contractAddress
          })
      });

      const updateData = await updateResponse.json();
      if (updateData.error) {
          alert(`❌ Failed to update database: ${updateData.error}`);
      } else {
          alert(`✅ Payment Recorded! Total completed years: ${updateData.updated_completed_years}`);
      }

      await fetchContractDetails(); // Refresh UI

  } catch (error) {
      console.error("❌ Error making payment:", error);
      alert("❌ Failed to make payment.Only Buyer can do this !");
  }
}


async function confirmDelivery() {
  try {
      await connectWallet();

      let contractAddress = document.getElementById("contractAddress").value.trim();
      if (!contractAddress) {
          alert("❌ Enter a valid contract address before confirming delivery.");
          return;
      }

      contractInstance = new ethers.Contract(contractAddress, contractABI, signer);

      let connectedAccount = await signer.getAddress(); // ✅ Get the connected MetaMask account

      const farmer = await contractInstance.farmer(); // ✅ Fetch the registered farmer from the smart contract

      console.log(`🔍 Connected Account: ${connectedAccount}`);
      console.log(`🔍 Registered Farmer in Contract: ${farmer}`);

      // ✅ Ensure only the registered farmer can confirm delivery
      if (connectedAccount.toLowerCase() !== farmer.toLowerCase()) {
          alert("❌ Only the farmer who deployed the contract can confirm delivery. Please switch to the correct account.");
          return;
      }

      console.log(`🚀 Checking if payment is made before confirming delivery...`);

      // ✅ Step 1: Ask Flask if payment has been completed
      const checkResponse = await fetch("/check_payment_validity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              buyer_address: connectedAccount,  // The farmer is checking if the buyer has paid
              contract_address: contractAddress
          })
      });

      const checkData = await checkResponse.json();
      if (checkData.error) {
          alert(`❌ Delivery Confirmation Failed: ${checkData.error}`);
          return;
      }

      console.log(`🚀 Confirming delivery from farmer: ${connectedAccount}`);

      // ✅ Step 2: Call Flask API to update database
      const response = await fetch("/confirm_delivery", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              farmer_address: connectedAccount,
              contract_address: contractAddress
          })
      });

      const data = await response.json();
      if (data.error) {
          alert(`❌ Failed to update database: ${data.error}`);
      } else {
          alert("✅ Delivery Confirmed!");
      }

  } catch (error) {
      console.error("⚠️ Error confirming delivery:", error);
      alert("❌ Failed to confirm delivery. Check console for details.");
  }
}



async function acceptOrder() {
  try {
      await connectWallet();

      let contractAddress = document.getElementById("contractAddress").value.trim();
      if (!contractAddress) {
          alert("❌ Enter a valid contract address before accepting the order.");
          return;
      }

      try {
          contractAddress = ethers.utils.getAddress(contractAddress); // ✅ Convert to checksum format
      } catch (error) {
          alert("❌ Invalid contract address format. Please enter a valid Ethereum address.");
          return;
      }

      let connectedAccount = await signer.getAddress(); // ✅ Get the connected MetaMask account

      try {
          connectedAccount = ethers.utils.getAddress(connectedAccount); // ✅ Convert to checksum format
      } catch (error) {
          alert("❌ Invalid buyer address format. Please ensure MetaMask is connected.");
          return;
      }

      console.log(`🔍 Connected Account: ${connectedAccount}`);

      // ✅ Call Flask API to fetch stored buyer address & delivery status
      console.log(`🔍 Fetching stored buyer and delivery status for contract: ${contractAddress}`);
      const contractResponse = await fetch(`/fetch_contract_details?contract_address=${contractAddress}`);
      const contractData = await contractResponse.json();

      if (contractData.error) {
          alert(`❌ Failed to fetch contract details: ${contractData.error}`);
          return;
      }

      const storedBuyer = ethers.utils.getAddress(contractData.buyer); // ✅ Ensure stored address is formatted correctly
      const deliveryConfirmed = contractData.delivery_confirmed; // ✅ Check if delivery is confirmed

      console.log(`🔍 Stored Buyer Address: ${storedBuyer}, Delivery Confirmed: ${deliveryConfirmed}`);

      // ✅ Ensure only the registered buyer can accept the order
      if (connectedAccount !== storedBuyer) {
          alert("❌ Only the assigned buyer can accept the order. Please switch to the correct MetaMask account.");
          return;
      }

      // ✅ Ensure delivery is confirmed before accepting the order
      if (!deliveryConfirmed) {
          alert("❌ Delivery has not been confirmed yet. Please confirm delivery before accepting the order.");
          return;
      }

      console.log(`🚀 Accepting order from buyer: ${connectedAccount}`);

      // ✅ Call Flask API to update database
      console.log(`🔍 Sending buyer address to Flask: ${connectedAccount}`);
      const response = await fetch("/accept_order", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              buyer_address: connectedAccount,
              contract_address: contractAddress
          })
      });

      const data = await response.json();
      if (data.error) {
          alert(`❌ Failed to accept order: ${data.error}`);
      } else {
          alert("✅ Order Accepted!");
      }

  } catch (error) {
      console.error("⚠️ Error accepting order:", error);
      alert("❌ Failed to accept order. Check console for details.");
  }
}




// ✅ Ensure script runs after the page is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  const contractAddressInput = document.getElementById("contractAddress");
  const savedContractAddress = localStorage.getItem("contractAddress");

  // ✅ Only update if the element exists and we have a saved contract address
  if (contractAddressInput && savedContractAddress) {
      contractAddressInput.value = savedContractAddress;
  }
});


// ✅ Clear previous values when the page loads
document.addEventListener("DOMContentLoaded", function () {
  localStorage.removeItem("contractAddress");  // Remove stored contract address
  localStorage.removeItem("paymentStatus");    // Remove payment status
  localStorage.removeItem("updateTime");       // Remove update timestamp
});
