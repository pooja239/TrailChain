//"SPDX-License-Identifier: UNSW"
pragma solidity ^0.5.13;
pragma experimental ABIEncoderV2;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 */
 
contract TrackerInterface {
    function createT3(bytes32 _owner, bytes32 _marketID, bytes32 _DID) public returns(bytes32);
    function updateT3(bytes32 _TID, bytes32 _owner, bytes32 _buyer, uint _r, bytes32 _marketID, bytes32 _DID) public returns(bool);
    function retrieveTrail(bytes32 _TID, bytes32 _owner) public view returns(bytes32[] memory, uint[] memory, bytes32[] memory);
    function getBuyerList(bytes32 _TID) public view returns(bytes32[] memory);
    function getT3Length(bytes32 _TID) public view returns(uint);
}
 
contract TrackerSc {
 
    struct Trail {
        bytes32 ownerID;
        bytes32 buyerID;
        bytes32 marketplaceID;
        bytes32 SID;
        uint ratio;
    }
 
    struct Tradetrail{
        bytes32 ownerID;
        uint ratio;
        bytes32 mID;
    }
 
    event newTrail(bytes32 TID);
    event Log(string);
 
 
    //T3 = (TID, Trail)
    mapping(bytes32 => Trail[]) T3;
 
    //dataProducer = (TID, actorID)
    mapping(bytes32 => bytes32) public dataProducer;
 
 
    //TIDexist = (TID, exist)
    mapping(bytes32 => bool) public TIDexist;
 
 
    //function to create T3 for any new dataset
    function createT3(bytes32 _owner, bytes32 _marketID, bytes32 _DID) public returns(bytes32 _TID) {
        _TID = keccak256(abi.encode(_DID, _marketID, _owner));
        require(!TIDexist[_TID], "Data already registered");
        dataProducer[_TID] = _owner;
        TIDexist[_TID] = true;
        return _TID;
    }


    //function to update the entry in entry
    function updateT3(bytes32 _TID, bytes32 _owner, bytes32 _buyer, uint _r, bytes32 _marketID, bytes32 _DID) public returns(string memory result) {
        require (TIDexist[_TID], "TID does not exist");
        if (T3[_TID].length == 0 && dataProducer[_TID] == _owner){
            T3[_TID].push(Trail(_owner, _buyer, _marketID, _DID, _r));
            result = "Success";
        } else if (T3[_TID].length != 0) {
            T3[_TID].push(Trail(_owner, _buyer, _marketID, _DID, _r));
            result = "Success";
        } else {
            result = "Error: Only Prodcuer can sell-first time";
        }
        return result;
    }
    
    //function to retrieve the trade trail of any actor
    function retrieveTrail(bytes32 _TID, bytes32 _owner) public view returns(bytes32[] memory, uint[] memory, bytes32[] memory){
        //Tradetrail[] memory TTL = constructTrail(_TID, _ownerS);
        Tradetrail[] memory TTL = constructTrail(_TID, _owner);
        bytes32[] memory ownerList = new bytes32[](TTL.length);
        uint[] memory ratioList = new uint[](TTL.length);
        bytes32[] memory marketList = new bytes32[](TTL.length);
        for(uint i=0; i<TTL.length; i++){
            ownerList[i] = TTL[i].ownerID;
            ratioList[i] = TTL[i].ratio;
            marketList[i] = TTL[i].mID;
        }
        return (ownerList, ratioList, marketList);
    }

    //function to construct the trail for any actor
    function constructTrail(bytes32 _TID, bytes32 _owner) public view returns(Tradetrail[] memory){
        //bytes32 owner = keccak256(abi.encode(_ownerS));
        uint count = 0;
        uint i;
        Tradetrail[] memory temp = new Tradetrail[](1000);
        for(i=T3[_TID].length; i>0; i--){
            if(T3[_TID][i-1].buyerID == _owner){
                temp[count] = Tradetrail(T3[_TID][i-1].ownerID, T3[_TID][i-1].ratio, T3[_TID][i-1].marketplaceID);
                _owner = T3[_TID][i-1].ownerID;
                count=count+1;
            }
        }
        Tradetrail[] memory TTL = new Tradetrail[](count);
        for(i=0; i<count; i++){
            TTL[i] = temp[i];
        }
        return TTL;
    }
    
    function getBuyerList(bytes32 _TID) public view returns(bytes32[] memory){
        bytes32[] memory buyerList = new bytes32[](getT3Length(_TID));
        for(uint i=0; i< T3[_TID].length; i++){
            buyerList[i] = T3[_TID][i].buyerID; 
        }
        return buyerList;
    }
    
    function getT3Length(bytes32 _TID) public view returns(uint){
        return T3[_TID].length;
    }
    

    function compareStrings(string memory a, string memory b) public pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }

    function retrieveT3(bytes32 _TID) public view returns(Trail[] memory) {
        require (TIDexist[_TID]);
        return T3[_TID]; 
    }
}


