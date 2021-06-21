//"SPDX-License-Identifier: UNSW"
pragma solidity ^0.5.13;
pragma experimental ABIEncoderV2;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 */
 
 import "./SubscriptionSc.sol";
 import "./PaymentSc.sol";
 
 contract RegisterSc {

    
    struct device {
        bytes32 deviceID;
        uint challenge;
        uint response;
    }
    
    struct Actor {
        bytes32 ID;
        device[] deviceList;
        bool exist;
    }
    
     struct data{
         bytes32 dataID;
         bytes32 subscriptionID;
         bytes32 agreementID;
         bool validation;
     }

    
    //actorList = (actorAddress, Struct Actor)
    mapping(address => Actor) public actorList;
    
    //contractList = (AID, contractAddress)
    mapping(bytes32 => address) public contractList;

    address paymentaddress;
    
    event LogID(bytes32);
    event log(string);
    
    //constructor(string memory _marketIDS, address _DN) public{
    constructor(string memory _marketIDS, address _paymentaddress) public{
        bytes32 _marketID = keccak256(abi.encode(_marketIDS));
        marketplaceID = _marketID;
        paymentaddres = _paymentaddress;
        //digitalNotary = _DN;
    }
    
    function registerActor(string memory actorS) public returns(bool){
        require(!actorList[msg.sender].exist, "Actor is already registered");
        bytes32 _actorPUK = keccak256(abi.encode(actorS));
        actorList[msg.sender].ID = _actorPUK;
        actorList[msg.sender].exist = true;
        emit LogID(_actorPUK);
        return true;
    }
    
    function registerDevice(string memory _deviceIDs, uint _C, uint _R) public returns(bool){
        require(actorList[msg.sender].exist, "Actor is not registered");
        bytes32 _deviceID = keccak256(abi.encode(_deviceIDs));
        device memory D = device(_deviceID, _C, _R);
        actorList[msg.sender].deviceList.push(D);
        return true;
    }
    
    //multi-sig function
    function registerAgreement(address _contractAddress) public returns(bool){
        SubscriptionSc subsriptionContract =  SubscriptionSc(_contractAddress);
        address buyer = subsriptionContract.Buyer();
        address seller = subsriptionContract.Seller();
        bytes32 _agreementID = keccak256(abi.encode(seller,buyer));
        contractList[_agreementID] = _contractAddress;
        emit LogID(_agreementID);
        return true;
    }

    function registerDelivery(bytes32 _AID, bytes32 _SID) public {
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        address buyer = subsriptionContract.Buyer();
        require(msg.sender == buyer, "Accessible by only buyer");
        require(subsriptionContract.PaymentCurrState(_SID) == 1, "Cannot confirm delivery");
        uint amount;
        (,,,amount,,) = subsriptionContract.subscriptions(_SID);
        bytes32 seller = actorList[subsriptionContract.Seller()].ID;
        subsriptionContract.confirmDelivery(_SID); //mark the payment status to AWAITING_SETTLEMENT"
        subsriptionContract.payment(_SID); //mark the subscription status to SETTLEMENT
        PaymentSc paymentContract =  PaymentSc(paymentaddress);
        paymentContract.transfer(seller, amount); //send payment using paymentSc
        subsriptionContract.updateS(_SID, "statusF");  //updateS
    }
    
    
    function getSellerInfo(bytes32 _AID) public view returns(address seller) {
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        seller = subsriptionContract.Seller();
        return seller;
    }

    function getBuyerInfo(bytes32 _AID) public view returns(address buyer) {
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        buyer = subsriptionContract.Buyer();
        return buyer;
    }

    
    function getMarketplaceID() public view returns(bytes32) {
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        return marketplaceID;  
    } 
    
}