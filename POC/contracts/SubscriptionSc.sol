//"SPDX-License-Identifier: UNSW"
pragma solidity ^0.5.13;
pragma experimental ABIEncoderV2;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 */
 
 contract interfaceSubscription{
    function updateS(bytes32 _SID, string memory field, bytes32 _value) public;
    function SignOutside(address) public;
    function reset() public;
 } 
 
 contract SubscriptionSc {
     
    struct Subscription{
         bytes32 deviceID;
         string dataType;
         string validationStatus;
         bytes32 validationValue;
         string temporalContext;
         uint price;
         bytes32 verificationValue;
         string status;
         uint resellRatio;
         bool exist;
    }

    bytes32[] subcriptionIDs;
    address public Seller;
    address public Buyer;
    mapping(bytes32 => Subscription) public subscriptions;
    mapping(address => bool) public signed;
    
    //{ 0: AWAITING_PAYMENT, 1: AWAITING_DELIVERY, 2: AWAITING_SETTLEMENT, 3: COMPLETE }
    mapping(bytes32 => uint8) public PaymentCurrState;
    
    
    event subscriptionID(bytes32);
    event subscriptionStatus(string);
    
    constructor(address _seller, address _buyer) public{
        Seller = _seller;
        Buyer = _buyer;
    }
    
    modifier onlyBuyer() {
        require(msg.sender == Buyer, "Only buyer can call this method");
        _;
    }
 
    function addS(string memory _deviceIDs, string memory _dataType, string memory _temporal, uint _price, uint _r) public{
        require (msg.sender == Seller);
        bytes32 SID = keccak256(abi.encode(subcriptionIDs.length, Seller, Buyer));
        subcriptionIDs.push(SID);
        subscriptions[SID].deviceID = keccak256(abi.encode(_deviceIDs));
        subscriptions[SID].dataType = _dataType;
        subscriptions[SID].temporalContext = _temporal;
        subscriptions[SID].price = _price;
        subscriptions[SID].validationStatus = "invalidated";
        subscriptions[SID].resellRatio = _r;
        subscriptions[SID].status = "INITIATE";
        subscriptions[SID].exist = true;
        emit subscriptionID(SID);
        emit subscriptionStatus("Subcription initiated");
    }
    
    //require the signature from both seller and buyer
    function startSubscription(bytes32 _SID) public{
        Sign();
        //require (signed[Buyer] == true && signed[Seller] == true, "Require sign by both the actors");
        if(signed[Buyer] == true && signed[Seller] == true){
            subscriptions[_SID].status = "ACTIVE";
            deposit(_SID);
            reset();
            emit subscriptionStatus("Subcription Started");
        }
        emit subscriptionStatus("Require sign by both the actors");
    }
    
    function deposit(bytes32 _SID) onlyBuyer internal {
        //require(PaymentCurrState[_SID] == PaymentState.AWAITING_PAYMENT, "Already paid");
        require(PaymentCurrState[_SID] == 0, "Already paid");
        PaymentCurrState[_SID] = 1;
        //PaymentCurrState[_SID] = PaymentState.AWAITING_PAYMENT;
    }
    
    function confirmDelivery(bytes32 _SID) external {
        require(PaymentCurrState[_SID] == 1, "Cannot confirm delivery");
        //seller.transfer(address(this).balance);
        PaymentCurrState[_SID]  = 2;
    }
    
    function updateS(bytes32 _SID, string memory field, bytes32 _value) public{
        if(compareStrings(field, "validationValue")){
            subscriptions[_SID].validationValue = _value;
        }
        if(compareStrings(field, "verificationValue")){
            subscriptions[_SID].verificationValue = _value;
        }
        if(compareStrings(field, "statusP")){
            subscriptions[_SID].status = "SETTLEMENT";
            
        }
        if(compareStrings(field, "statusF")){
            subscriptions[_SID].status = "FINISH";
            PaymentCurrState[_SID]  = 3;
        }
        emit subscriptionStatus("Subcription Updated");
    }
    
    //require the signature from buyer
    function payment(bytes32 _SID) public{
        require (msg.sender == Buyer);
        if(subscriptions[_SID].verificationValue != 0){
            subscriptions[_SID].status = "SETTLEMENT";
        }
        emit subscriptionStatus("Subcription Settlement");
    }
    
    function reset() public {
        signed[Buyer] = false;
        signed[Seller] = false;
    }
    
    
    //require the signature from seller
    function dataValidate(bytes32 _SID, uint _validationvalue) public{
        require (msg.sender == Seller);
        bytes32 nonceHash = keccak256(abi.encodePacked(_validationvalue));
        if(subscriptions[_SID].validationValue == nonceHash){
            subscriptions[_SID].validationStatus = "validated";
            //subscriptions[_SID].status = "ACTIVE";
            Sign();
            emit subscriptionStatus("Data Registration passed");
        } else {
            emit subscriptionStatus("Data Registration failed");
        }
    }
    
    function Sign() public {
        require (msg.sender == Seller || msg.sender == Buyer);
        require (signed[msg.sender] == false);
        signed[msg.sender] = true;
    }
    
    function SignOutside(address _sender) public {
        require (_sender == Seller || _sender == Buyer);
        require (signed[_sender] == false);
        signed[_sender] = true;
    }
    
    function compareStrings(string memory a, string memory b) public pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }
    
    function getSubscriptionList() public view returns (Subscription[] memory) {
        uint count = subcriptionIDs.length;
        Subscription[] memory SL = new Subscription[](count);
        for(uint i=0; i<count; i++){
            bytes32 _SID = subcriptionIDs[i];
            SL[i] = subscriptions[_SID];
        }
        return SL;
    }

    function getSubscriptionbyID(bytes32 SID) public view returns (Subscription memory) {
        return subscriptions[SID];
    }

    function getdevicebySID(bytes32 SID) public view returns (bytes32) {
        return subscriptions[SID].deviceID;
    }
    
    function paymentStatus(bytes32 _SID) public view returns (string memory result) {
        require (msg.sender == Seller || msg.sender == Buyer);
        if(PaymentCurrState[_SID] == 0) {
            result = "AWAITING_PAYMENT";
        } else if(PaymentCurrState[_SID] == 1) {
            result = "AWAITING_DELIVERY";
        } else if(PaymentCurrState[_SID] == 2) {
            result = "AWAITING_SETTLEMENT";
        } else {
            result = "COMPLETE";
        }
        return result;
    }
 
 }