//"SPDX-License-Identifier: UNSW"
pragma experimental ABIEncoderV2;
pragma solidity ^0.5.13;

import "./TrackerSc.sol";

contract NotarySc {

    struct notaryNode {
        bytes32[] associatedMarket;
        bool exist;
    }

    struct PaymentShare{
        bytes32 ownerID;
        uint share;
    }
    
    event LogTID(bytes32);
    //event PaymentShareList(PaymentShare[]);
    event PaymentShareList(uint[]);
    event PaymentactorList(bytes32[]);
    event paymentshareLog(string);
    
    address TrackerAddress;
    
    //DN => MP mapping
    mapping(address => notaryNode) NotaryList;
    
    //marketplace => true/false mapping
    mapping(bytes32 => bool) marketplaceExist;
    
    //verifiedLineage = (TID, bool)
    mapping(bytes32 => string) public verifiedLineage;
    
    function registerDigitalNotary() public returns(bool result) {
        require(!NotaryList[msg.sender].exist, "Notary already registered");
        NotaryList[msg.sender].exist = true;
        return true;
    }
    
    function registerMarketplace(bytes32 marketID) public returns(string memory result) {
        require(NotaryList[msg.sender].exist, "Notary not registered");
        require(!marketplaceExist[marketID], "marketplace already registered");
        NotaryList[msg.sender].associatedMarket.push(marketID);
        marketplaceExist[marketID] = true;
        return "Success";
    }
    
    function setAddresTracker(address _address) public{
         TrackerAddress = _address;
     }
     
    function addNewDataTrail(bytes32 _owner, bytes32 _marketID, bytes32 _DID) public {
        require(NotaryList[msg.sender].exist, "Only registered Notary can send transaction");
        TrackerSc tracker = TrackerSc(TrackerAddress);
        bytes32 TID = tracker.createT3(_owner, _marketID, _DID);
        emit LogTID(TID);
     }
     
  function validateTrail(bytes32 _TID, bytes32 _seller, bytes32 _buyer, bytes32 _market) public view returns (string memory result){
        require(NotaryList[msg.sender].exist);
        TrackerSc tracker = TrackerSc(TrackerAddress);
        if(!tracker.TIDexist(_TID)){
            result = "Error: Invalidated data";
        }
        else if (tracker.getT3Length(_TID) == 0) {
            if(_seller !=tracker.dataProducer(_TID)) {
                result = "illegitimate selling";
            } else {
                result = "No reselling";   
            }
        }
        else {
            result = checkError(_buyer, _TID, _seller);
            if(compareStrings(result,"Success")){
                if(tracker.dataProducer(_TID) == _seller){
                    result = "No reselling";
                } else {
                    bytes32[] memory marketList;
                    (, , marketList) = tracker.retrieveTrail(_TID, _seller);
                    result = checkType(_market, marketList);
                }
            }
        }
        return result;
    }

    function checkType(bytes32 market, bytes32[] memory mList) public pure returns(string memory result){
        for(uint i=0; i<mList.length; i++){
            if(market == mList[i]){
                market = mList[i];
                result = "intra reselling";
            } 
            else {
               result = "inter reselling";
               break;
            }
        }
        return result;
    }
    
    function checkError(bytes32 _buyer, bytes32 _TID, bytes32 _seller) public view returns(string memory result){
        bool legitimate = false;
        bool doublebuy = false;
        TrackerSc tracker = TrackerSc(TrackerAddress);
        if(_buyer == tracker.dataProducer(_TID)){
            doublebuy = true;
        } 
        if (_seller == tracker.dataProducer(_TID)) {
            legitimate = true;
        }
        bytes32[] memory buyerList = tracker.getBuyerList(_TID);
        for(uint i = 0; i<buyerList.length; i++){
           if(buyerList[i] == _buyer){
              doublebuy = true;
            }
            if(buyerList[i] == _seller) {
                legitimate = true;
            }
        }
        if(!legitimate && doublebuy){
            result = "illegitimate selling and double-buy";
        }
        else if(!legitimate){
            result = "illegitimate";
        }
        else if(doublebuy) {
            result = "double-buy";
        }
        else {
            result= "Success";
        }
        return result;
    }
    
    function evaluatePaymentShare(bytes32 _TID, bytes32 _seller, bytes32 _buyer, uint _r, bytes32 _marketID, bytes32 _DID, uint P) public  returns(PaymentShare[] memory){
        TrackerSc tracker = TrackerSc(TrackerAddress);
        bytes32[] memory ownerList;
        uint[] memory ratioList;
        string memory result = validateTrail(_TID, _seller, _buyer, _marketID);
        if(compareStrings(result,"No reselling") || compareStrings(result,"inter reselling") || compareStrings(result,"intra reselling")){
            result = tracker.updateT3(_TID, _seller, _buyer, _r, _marketID, _DID);
            if(compareStrings(result,"Success")){
                result = "Trail Update passed";
    
                (ownerList, ratioList, ) = tracker.retrieveTrail(_TID, _seller);
                if(ownerList.length == 0){
                    PaymentShare[] memory PSL = new PaymentShare[](1);
                    PSL[0] =  PaymentShare(_seller, P);
                    //emit PaymentShareList(PSL);
                    bytes32[] memory actorList = new bytes32[](PSL.length);
                    uint[] memory shareList = new uint[](PSL.length);
        
                    for(uint i=0; i< PSL.length; i++){
                        actorList[i] = PSL[i].ownerID;
                        shareList[i] = PSL[i].share;
                    }
                    emit PaymentShareList(shareList);
                    emit PaymentactorList(actorList);
                } else {
                    PaymentShare[] memory PSL = new PaymentShare[](ownerList.length+1);
                    PSL = evaluate(_seller, ownerList, ratioList, P);
                    //emit PaymentShareList(PSL);
                    bytes32[] memory actorList = new bytes32[](PSL.length);
                    uint[] memory shareList = new uint[](PSL.length);
        
                    for(uint i=0; i< PSL.length; i++){
                        actorList[i] = PSL[i].ownerID;
                        shareList[i] = PSL[i].share;
                    }
                    emit PaymentShareList(shareList);
                    emit PaymentactorList(actorList);
                } 
            }
        }
        emit paymentshareLog(result);
    }
    
    function evaluate(bytes32 _owner, bytes32[] memory ownerList, uint[] memory ratioList, uint P) public pure returns(PaymentShare[] memory){
        PaymentShare[] memory PSL = new PaymentShare[](ownerList.length+1);
        for(uint i = 0; i<ownerList.length+1; i++){
            if(i==0){
                PSL[i] = PaymentShare(_owner, P);
            } else {
                    PSL[i] = PaymentShare(ownerList[i-1], ratioList[i-1]*PSL[i-1].share/100);
                    PSL[i-1].share = PSL[i-1].share - PSL[i].share;
            }
        }
        return PSL;
    }
    
    function compareStrings(string memory a, string memory b) public pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }
}
