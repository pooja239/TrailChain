//"SPDX-License-Identifier: UNSW"
pragma solidity ^0.5.13;
pragma experimental ABIEncoderV2;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 */
 
 import "./SubscriptionSc.sol";
 
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
    
    struct payment{
        bytes32 subscriptionID;
        bytes32 agreementID;
        bytes32 authenticationValue;
        bytes32 buyer;
        bytes32 seller;
        uint amount;
        uint resellratio;
        //bool paymentStatus;
    }
    
  
    bytes32 marketplaceID;
    address digitalNotary;
    
    //actorList = (actorAddress, Struct Actor)
    mapping(address => Actor) public actorList;
    
    //contractList = (AID, contractAddress)
    mapping(bytes32 => address) public contractList;
    
    //dataList = (deviceID, subscriptionID List)
    mapping(bytes32 => bytes32[]) dataList;
    
    payment[] unpaidList;
    data[] unregisteredList;
    
    event LogID(bytes32);
    event log(string);
    
    constructor(string memory _marketIDS, address _DN) public{
        bytes32 _marketID = keccak256(abi.encode(_marketIDS));
        marketplaceID = _marketID;
        digitalNotary = _DN;
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
        //require(actorList[msg.sender].exist, "Actor is not registered");
        SubscriptionSc subsriptionContract =  SubscriptionSc(_contractAddress);
        address buyer = subsriptionContract.Buyer();
        address seller = subsriptionContract.Seller();
        //address _sender = msg.sender;
        //subsriptionContract.SignOutside(_sender);
        //require (subsriptionContract.signed(buyer) == true && subsriptionContract.signed(seller) == true, "require sign by both actors");
        bytes32 _agreementID = keccak256(abi.encode(seller,buyer));
        contractList[_agreementID] = _contractAddress;

        //subsriptionContract.reset();
        emit LogID(_agreementID);
        return true;
    }

    function registerData(bytes32 _SID, bytes32 _AID) public returns(bool){
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        //bytes32 _deviceID = keccak256(abi.encode(_deviceIDS));
        //bytes32 _dataID = keccak256(abi.encode(marketplaceID,_SID,_AID));
        bytes32 _dataID = _SID;
        bytes32 _deviceID;
        //uint _r;
        (_deviceID,,,,,,,,,) = subsriptionContract.subscriptions(_SID);
        dataList[_deviceID].push(_dataID);
        data memory d = data(_dataID, _SID, _AID, false);
        unregisteredList.push(d);
        //subsriptionContract.updateS(_SID, "status", 0);
        emit LogID(_dataID);
        return true;
    }
    
    //function ownershipRegistered(bytes32 _SID, bytes32 _value) public returns(bool){
    function ownershipRegistered(bytes32 _SID, string memory _field, bytes32 _value) public returns(bool){
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        uint len = unregisteredList.length;
        uint i;
        for(i=0; i<unregisteredList.length; i++){
            if(unregisteredList[i].subscriptionID == _SID) {
                break;
            }
        }
        //unregisteredList[i].validation = true;
        bytes32 _AID = unregisteredList[i].agreementID;
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        //subsriptionContract.updateS(_SID, _field, _value);
        subsriptionContract.updateS(_SID, "validationValue", _value);
        unregisteredList[i] = unregisteredList[len-1];
        delete unregisteredList[len-1];
        return true;
    }
    
    function registerDelivery(bytes32 _AID, bytes32 _SID) public {
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        address buyer = subsriptionContract.Buyer();
        require(msg.sender == digitalNotary || msg.sender == buyer, "Accessible by only digital notary and buyer");
        require(subsriptionContract.PaymentCurrState(_SID) == 1, "Cannot confirm delivery");
        //seller.transfer(address(this).balance);
        if(msg.sender == subsriptionContract.Buyer()){
            uint amount;
            (,,,,,amount,,,,) = subsriptionContract.subscriptions(_SID);
            bytes32 seller = actorList[subsriptionContract.Seller()].ID;
            //payment memory _p = payment(_SID, _AID, 0, actorList[buyer].ID, seller, amount, 0, false);
            payment memory _p = payment(_SID, _AID, 0, actorList[buyer].ID, seller, amount, 0);
            unpaidList.push(_p);
        }
        subsriptionContract.confirmDelivery(_SID);
    }
    
    
    function authencityRegistered(bytes32 _SID, bytes32 _AID, string memory _field, bytes32 _value) public returns(bool){
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        bytes32 buyer = actorList[subsriptionContract.Buyer()].ID;
        bytes32 seller = actorList[subsriptionContract.Seller()].ID;
        uint amount;
        uint _r;
        (,,,,,amount,,,_r,) = subsriptionContract.subscriptions(_SID);
        //payment memory _p = payment(_SID, _AID, _value, buyer, seller, amount, _r, false);
        payment memory _p = payment(_SID, _AID, _value, buyer, seller, amount, _r);
        unpaidList.push(_p);
        subsriptionContract.updateS(_SID, "statusP", _value);
        registerDelivery(_AID, _SID);
        return true;
    }
    
    function registerPayment(bytes32 _SID) public {
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        uint len = unpaidList.length;
        uint i;
        for(i=0; i<unpaidList.length; i++){
            if(unpaidList[i].subscriptionID == _SID) {
                break;
            }
        }
        //unregisteredList[i].validation = true;
        bytes32 _AID = unpaidList[i].agreementID;
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        //subsriptionContract.updateS(_SID, "status", 0);
        subsriptionContract.updateS(_SID, "statusF", 0);
        unpaidList[i] = unpaidList[len-1];
        delete unpaidList[len-1];
        
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
    
    function retrieveunregisteredDataList() public view returns(data[] memory) {
        return unregisteredList;
    }

    function retrieveunpaidList() public view returns(payment[] memory) {
        return unpaidList;
    }
    
    function getDeviceInfo(bytes32 _deviceID, address _owner) public view returns(uint C, uint R){
        for(uint i=0; i<actorList[_owner].deviceList.length;i++) {
            if(actorList[_owner].deviceList[i].deviceID == _deviceID) {
                C = actorList[_owner].deviceList[i].challenge;
                R = actorList[_owner].deviceList[i].response;
                break;
            }
        }
        return(C,R);
    }

    function getDevicefromSID(bytes32 _AID, bytes32 _SID) public view returns (bytes32) {
        require(msg.sender == digitalNotary, "Accessible by only digital notary");
        SubscriptionSc subsriptionContract =  SubscriptionSc(contractList[_AID]);
        return subsriptionContract.getdevicebySID(_SID);
    }

}