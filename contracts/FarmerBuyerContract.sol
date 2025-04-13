// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract FarmerBuyerContract {
    address public farmer;
    address public buyer;
    uint256 public price;
    uint256 public quantity;
    uint256 public contractYears;
    uint256 public paymentsMade; // ✅ Track payments made
    bool public isPaid = false;

    event ContractCreated(address indexed farmer, address indexed buyer, uint256 price, uint256 quantity, uint256 contractYears);
    event PaymentMade(address indexed buyer, uint256 amount, uint256 paymentsMade);
    event ProductDelivered(address indexed farmer, address indexed buyer);

    constructor(address _buyer, uint256 _price, uint256 _quantity, uint256 _contractYears) {
        require(_contractYears > 0, "Contract years must be greater than zero");
        require(_price > 0, "Price must be greater than zero");
        require(_quantity > 0, "Quantity must be greater than zero");

        farmer = msg.sender;
        buyer = _buyer;
        price = _price;
        quantity = _quantity;
        contractYears = _contractYears;
        paymentsMade = 0; // ✅ Initialize payment tracker

        emit ContractCreated(farmer, buyer, price, quantity, contractYears);
    }

    function makePayment() public payable {
        require(msg.sender == buyer, "Only buyer can make payment");
        require(paymentsMade < contractYears, "All payments completed");
        require(msg.value == price, "Payment must match price");
        require(!isPaid, "Already paid for this cycle");

        isPaid = true;
        paymentsMade++; // ✅ Increment payments made

        emit PaymentMade(msg.sender, msg.value, paymentsMade);
    }

    function confirmDelivery() public {
        require(msg.sender == farmer, "Only farmer can confirm delivery");
        require(isPaid, "Payment not received yet");

        isPaid = false; // ✅ Reset payment status for the next cycle
        emit ProductDelivered(farmer, buyer);
    }

    function getPaymentsMade() public view returns (uint256) {
        return paymentsMade; // ✅ Allow frontend to track payments
    }

    function isContractComplete() public view returns (bool) {
        return paymentsMade >= contractYears;
    }
}
