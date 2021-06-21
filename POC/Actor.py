import solcx
from solcx import get_solc_version, set_solc_version
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
import random
import socket
import threading
import watermarking_module
import re


ENCODING = 'utf-8'

set_solc_version('v0.5.13')

class Actor:
    

    def __init__(self, _privateKey, _address, _UserName, _host, _port, _registerAddress, _registerABI, _paymentAddress, _paymentABI, _marketplaceURL, _paymentURL):
        self.profile = {}
        self.profile['private_key'] = _privateKey
        self.profile['address'] = _address
        self.profile['UserName'] = _UserName
        self.profile['host'] = _host
        self.profile['port'] = _port
        self.profile['UserID'] = ''
        
        self.marketplaceURL = _marketplaceURL
        self.paymentURL = _paymentURL


        _web3P = Web3(Web3.HTTPProvider(self.paymentURL))
        _web3M = Web3(Web3.HTTPProvider(self.marketplaceURL))
        
        _RegisterSc = _web3M.eth.contract(address=_registerAddress, abi=_registerABI)
        _PaymentSc = _web3P.eth.contract(address=_paymentAddress, abi=_paymentABI)
        
        self.contracts = {}
        self.contracts['application'] = {'Address': _registerAddress, 'ABI': _registerABI, 'web3': _web3M, 'contract': _RegisterSc}
        self.contracts['payment'] = {'Address': _paymentAddress, 'ABI': _paymentABI, 'web3': _web3P, 'contract': _PaymentSc}

        self.AgreementList = {}

        self.sellerSendFile = {}

        self.buyerReceivedFile = {}


    def createProfileinPayment(self):
        
        PaymentSc = self.contracts['payment']['contract']
        web3 = self.contracts['payment']['web3']

        username = self.profile['UserName']
        createAccount_tx = PaymentSc.functions.createAccount(self.profile['UserName'], 100000000).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(createAccount_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        print(f'{username} is registered in Payment system')
        

    def createProfileinMarketplace(self):
        
        RegisterSc = self.contracts['application']['contract']
        web3 = self.contracts['application']['web3']

        username = self.profile['UserName']
        registerActor_tx = RegisterSc.functions.registerActor(self.profile['UserName']).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(registerActor_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        logs = RegisterSc.events.LogID().processReceipt(tx_receipt, errors=DISCARD)
        self.profile['UserID'] = Web3.toHex(logs[0]['args'][''])
        #ID = _Producer
        print(f'{username} is registered in Marketplace')

        return self.profile['UserID'], self.profile['UserName']

        

    
    def registerDevice(self, _device, _C, _R):
        
        RegisterSc = self.contracts['application']['contract']
        web3 = self.contracts['application']['web3']

        username = self.profile['UserName']
        registerDevice_tx = RegisterSc.functions.registerDevice(_device, _C, _R).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(registerDevice_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        print(f'{username} device is registered in Marketplace')



    def deploySubscriptionSc(self, _buyer):

        #RegisterSc = self.contracts['application']['contract']
        web3 = self.contracts['application']['web3']
        
        username = self.profile['UserName']
        subscription_file = solcx.compile_files('SubscriptionSc.sol')
        abiSubscription = subscription_file['SubscriptionSc.sol:SubscriptionSc']['abi']
        bytecodeSubscription = subscription_file['SubscriptionSc.sol:SubscriptionSc']['bin']
        subscription = web3.eth.contract(abi=abiSubscription, bytecode=bytecodeSubscription)


        seller = self.profile["address"]
        buyer = _buyer

        # Build Constructor Tx
        construct_txn = subscription.constructor(seller, buyer).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )

        tx_create = web3.eth.account.signTransaction(construct_txn, self.profile['private_key'])

        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        gasUsed = tx_receipt

        print(f'-> [{username}]: Data-Seller deploys SubscriptionSc address: { tx_receipt.contractAddress }')
        return tx_receipt.contractAddress, abiSubscription, tx_receipt.gasUsed


    def registerAgreement(self, _subscriptionAddress, _subscriptionABI):
    
        RegisterSc = self.contracts['application']['contract']
        web3 = self.contracts['application']['web3']

        username = self.profile['UserName']
        registerAgreement_tx = RegisterSc.functions.registerAgreement(_subscriptionAddress).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(registerAgreement_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        logs = RegisterSc.events.LogID().processReceipt(tx_receipt, errors=DISCARD)
        self.AID = Web3.toHex(logs[0]['args'][''])
        print(f'-> [{username}]: registers contract in the marketplace')
        
        subscriptionSc = web3.eth.contract(address=_subscriptionAddress, abi=_subscriptionABI)
        self.AgreementList = {self.AID: {'subscriptionSc': subscriptionSc, 'address': _subscriptionAddress, 'ABI': _subscriptionABI,'subscriptionList': []}}
        
        return self.AID, tx_receipt.gasUsed



    def addSubscription(self, _AID, _device, _dataType, _temporal, _price, _resellRatio):
    
        web3 = self.contracts['application']['web3']

        username = self.profile['UserName']

        SubscriptionSc = self.AgreementList[_AID]['subscriptionSc']
        addS_tx = SubscriptionSc.functions.addS(_device, _dataType, _temporal, _price, _resellRatio).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(addS_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)


        logs = SubscriptionSc.events.subscriptionID().processReceipt(tx_receipt, errors=DISCARD)
        SID = Web3.toHex(logs[0]['args'][''])
        print(f'[{username}]: Data-Seller add subscription with ID: {SID}')

        self.AgreementList[_AID]['subscriptionList'].append(SID)        

        self.checkSubscriptionStatus(_AID, SID)
        return SID, tx_receipt.gasUsed


    def registerData(self, _AID, _SID):

        RegisterSc = self.contracts['application']['contract']
        web3 = self.contracts['application']['web3']        

        username = self.profile['UserName']

        registerData_tx = RegisterSc.functions.registerData(_SID, _AID).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(registerData_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        logs = RegisterSc.events.LogID().processReceipt(tx_receipt, errors=DISCARD)
        DID = Web3.toHex(logs[0]['args'][''])
        print(f'(4.1) [{username}]: Data-Producer executes  data registeration with DID: {DID}')
        return tx_receipt.gasUsed

    
    def receiveRegistrationfromNotary(self,_filename):
        
        web3 = self.contracts['application']['web3']  

        username = self.profile['UserName']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.bind((self.profile['host'], self.profile['port']))
        sock.listen(10)
        mssg = []
        connection, client_address = sock.accept()
        print('accept')
        while True:
            data = connection.recv(2048)
            if not data:
                break  # no more data coming in, so break out of the while loop
            mssg.append(data)  # add chunk to your already collected data
        message = mssg[0].decode(ENCODING)
    
    ##message Format = [_Owner, _TID, _SID, _AID, Challenge, nonce]
    
        challenge_received = message.split(' ')[1] 
        nonce_received = int(message.split(' ')[2]) 
        TID_received = message[66:132]
        SID_received = message[132:198]
        AID_received = message[198:264]

        SubscriptionSc = self.AgreementList[AID_received]['subscriptionSc']
        #SubscriptionSc = web3.eth.contract(address=Subscription_address, abi=abiSubscription)
        dataValidate_tx = SubscriptionSc.functions.dataValidate(SID_received, nonce_received).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(dataValidate_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        logs = SubscriptionSc.events.subscriptionStatus().processReceipt(tx_receipt, errors=DISCARD)
        status = logs[0]['args']['']
        print(f'(4.5) [{username}]: Data-Producer validates the ownership of dataset using received nonce')
        print(f'-> {status}')

        if(status == 'Data Registration passed'):
        
            print(f'(4.6) [{username}]: Data-Producer watermarks the data with the received key')
            watermarkedDataFile = watermarking_module.addWatermark(TID_received, _filename)
            self.sellerSendFile[SID_received] = {'datasetFile': _filename, 'waterMarkedFile': watermarkedDataFile}

        return tx_receipt.gasUsed

        
    #file can either be 'waterMarkedFile' or 'datasetFile' depending on whether its a producer or reseller 
    def sendDatatoBuyer(self, _buyerHost, _buyerPort, _AID, _SID, _fileType):
        
        username = self.profile['UserName']
        SubscriptionSc = self.AgreementList[_AID]['subscriptionSc']
        status = SubscriptionSc.functions.subscriptions(_SID).call()[7]
        _filename = self.sellerSendFile[_SID][_fileType]
        #print(f"Producer: {status}")
        if (status =="ACTIVE"):
            print(f"(6.1) [{username}]: Data-seller transfers the dataset to data-buyer")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((_buyerHost, _buyerPort))  

            f = open(_filename, "r") 
            message = f.read(1024)
            while (message):
                s.sendall(message.encode(ENCODING))
                message = f.read(1024)
            f.close()
            s.shutdown(2)
            s.close()


    def startSubscription(self, _AID, _SID):
        
        web3 = self.contracts['application']['web3']  

        username = self.profile['UserName']
        SubscriptionSc = self.AgreementList[_AID]['subscriptionSc']
        #SubscriptionSc = web3.eth.contract(address=Subscription_address, abi=abiSubscription)
        startSubscription_tx = SubscriptionSc.functions.startSubscription(_SID).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3.eth.getTransactionCount(self.profile['address']),
            'chainId': web3.eth.chain_id,
        }
        )
        tx_create = web3.eth.account.signTransaction(startSubscription_tx, self.profile['private_key'])
        tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        logs = SubscriptionSc.events.subscriptionStatus().processReceipt(tx_receipt, errors=DISCARD)
        status = logs[0]['args']['']

        print(f'[{username}]: Starts the subscription')
        
        self.checkSubscriptionStatus(_AID, _SID)
        return tx_receipt.gasUsed


    def receiveDatafromSeller(self, _AID, _SID, _filename):
        
        username = self.profile['UserName']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.profile['host'], self.profile['port']))
        sock.listen(10)
        message = []
        connection, client_address = sock.accept()
        textfile = open(_filename, "w")
        while True:
            data = connection.recv(1024)
            if not data:
                break  # no more data coming in, so break out of the while loop
            d1 = data.decode(ENCODING)
            textfile.write(d1)
        textfile.close()
        print(">>>>>>>>>>>>>>Actor " + _SID)
        self.buyerReceivedFile[_SID] = _filename

        print(f"(6.2) [{username}]: Data-buyer receives the dataset from data-seller")


    def sendDataVerificationRequest(self, _notaryHost, _notaryPort, _SID, _AID):
    
        username = self.profile['UserName']
        print(f'(7.1) Data-Buyer: Send (SID, AID, verification packets) to the Notary for executing data verification process')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((_notaryHost, _notaryPort))     
        message = _SID + _AID
        s.sendall(message.encode(ENCODING))
        s.shutdown(2)
        s.close()
        print(">>>>>>>>>>>>>>Actor " + _SID)
        _filename = self.buyerReceivedFile[_SID]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((_notaryHost, _notaryPort))  
        f = open(_filename, "r") 
        message = f.read(1024)
        while (message):
            s.sendall(message.encode(ENCODING))
            message = f.read(1024)
        f.close()
        s.shutdown(2)
        s.close()

    def checkSubscriptionStatus(self, _AID, _SID):

        SubscriptionSc = self.AgreementList[_AID]['subscriptionSc']
        #SubscriptionSc = web3.eth.contract(address=Subscription_address, abi=abiSubscription)
        subscriptionsStatus = SubscriptionSc.functions.getSubscriptionbyID(_SID).call()
        print(f'-> Subscription status : {subscriptionsStatus[7]}')
        paymentStatus = SubscriptionSc.functions.paymentStatus(_SID).call({'from': self.profile['address']})
        print(f'-> Payment status : {paymentStatus}')

    def checkBalance(self):

        PaymentSc = self.contracts['payment']['contract']
        return PaymentSc.functions.balanceOf().call({'from': self.profile['address']})

