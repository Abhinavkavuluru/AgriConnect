# 🌾 AgriConnect – A Blockchain-Based Framework for Secure Agricultural Transactions

AgriConnect is an end-to-end blockchain-based contract farming platform designed to streamline and secure agricultural transactions between farmers and buyers. The system provides secure smart contracts (via Ethereum), verified payments (via PayPal), and communication (via Twilio), all wrapped in a user-friendly Flask web application.

---

## 🚀 Project Overview

This project has two core components:

1. **Smart Contracts & Blockchain Setup**
   - GitHub Repo: [`Smart_contract`](https://github.com/yourusername/Smart_contract)
   - Tech: Solidity + Hardhat + MetaMask
   - Runs an Ethereum test blockchain with smart contracts for contract farming.

2. **Flask-Based Web Platform**
   - GitHub Repo: [`AgriConnect`](https://github.com/yourusername/AgriConnect)
   - Tech: Flask + MySQL + Twilio + PayPal
   - Handles registration, login, crop listing, contract communication, and payments.

---

## 🧱 Folder Structure

- `Smart_contract/` – Contains Hardhat project for deploying Ethereum smart contracts
- `AgriConnect/` – Contains the Flask-based front-end + backend system with all integrations

---

## 🔧 Prerequisites

### Common:
- Python 3.10+
- Node.js (LTS)
- MySQL Server (8.x)
- MetaMask extension installed
- Twilio account
- PayPal Developer account

---

## 🧩 How to Run – Step-by-Step

### ✅ 1. Set up Smart Contract Backend (Smart_contract repo)


git clone https://github.com/yourusername/Smart_contract.git
cd Smart_contract
npm install
npx hardhat node

✅ 2. Set up the Flask Web Platform (AgriConnect repo)
git clone https://github.com/yourusername/AgriConnect.git
cd AgriConnect
Install Python packages
pip install -r requirements.txt
Create .env file for credentials
FLASK_SECRET_KEY=your_flask_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth
TWILIO_PHONE_NUMBER=your_twilio_phone


✅ 3. MySQL Setup
Start your MySQL server

✅ 4. Run the Flask App
python app.py
App runs at: http://localhost:5000

✅ Make sure the Hardhat node is running before launching the Flask app!

🧪 Features & Modules
•	👨‍🌾 Farmer Features
   •	Register/Login
   •	List crops
   •	Chat with buyers
   •	Create blockchain contracts
•	🛒 Buyer Features
   •	Browse available crops
   •	Accept orders
   •	Make payments (via PayPal)
   •	Confirm deliveries
•	🔐 Security
   •	OTP-based password reset (via Twilio)
   •	Smart contract-backed secure payments
   •	Blockchain ledger-based agreement tracking


🧠 Technologies Used
Layer	                    Tech
Smart Contract	          Solidity, Hardhat, MetaMask
Web Backend	             Python, Flask
Frontend	                HTML, CSS, JS
DB	                      MySQL
Messaging	             Twilio API
Payments	                PayPal SDK

🤝 Team & Acknowledgements
Developed by:
   •	K. Abhinav 
   •	E. Uday Sai 
   •	P. Sai Kumar 
Guided by: Mrs. K. Ramya Madhavi
Department of Information Technology
Maturi Venkata Subba Rao Engineering College (MVSR)


📈 Future Enhancements
   •	AI-based crop price prediction
   •	Multilingual support
   •	Real-time blockchain visualization
   •	UPI & Crypto wallet integrations
   •	Mobile App with push notifications

📃 License
This project is for academic and research purposes. For production use, please ensure proper key encryption and API security.

