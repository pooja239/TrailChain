//"SPDX-License-Identifier: UNSW"
pragma solidity ^0.5.13;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 */
 
 contract PaymentSc {
    
    //(Actor public key => balances)
    mapping (bytes32 => uint256) private _balances;
    
    struct account{
        bytes32 ID;
        uint balance;
        
    }

    uint256 private totalSupply;

    string private name;
    string private symbol;
    
    event  Transfer(address, address, uint);
    
    mapping(address => account) actorAccount;
    mapping(bytes32 => address) AccountID;
     
    constructor (string memory name_, string memory symbol_, uint totalSupply_) public {
        name = name_;
        symbol = symbol_;
        totalSupply = totalSupply_;
    }

    /**
     * @dev Returns the name of the token.
     */
    function Name() public view returns (string memory) {
        return name;
    }

    function TotalSupply() public view returns (uint256) {
        return totalSupply;
    }
    
    function balanceOf() public view returns (uint256) {
        return actorAccount[msg.sender].balance;
    }

    function balanceOfActors(bytes32 actorID) public view returns (uint256) {
        address actorAdd = AccountID[actorID];
        return actorAccount[actorAdd].balance;
    }    

    function createAccount(string memory _name, uint _balance) public {
        bytes32 ID = keccak256(abi.encode(_name));
        actorAccount[msg.sender] = account(ID, _balance);
        AccountID[ID] = msg.sender;
    }

    function transfer(bytes32 _recipient, uint256 amount) public returns (bool) {
        uint256 senderBalance = actorAccount[msg.sender].balance;
        require(senderBalance >= amount, "ERC20: transfer amount exceeds balance");
        actorAccount[msg.sender].balance = senderBalance - amount;
        address Recipient = AccountID[_recipient];
        actorAccount[Recipient].balance += amount;
        emit Transfer(msg.sender, Recipient, amount);
    }
    
    function transferFrom(address _sender, address _recipient, uint256 _amount) public returns (bool) {
        //transfer(sender, recipient, amount);
        uint256 senderBalance = actorAccount[_sender].balance;
        require(senderBalance >= _amount, "ERC20: transfer amount exceeds balance");
        actorAccount[_sender].balance = senderBalance - _amount;
        actorAccount[_recipient].balance += _amount;
        emit Transfer(_sender, _recipient, _amount);
        return true;
    }

 }