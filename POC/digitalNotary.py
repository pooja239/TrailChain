import socket
import threading
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
import random
import watermarking_module
 
ENCODING = 'utf-8'
 
class digitalNotary:
    
    

    def __init__(self, _privateKey, _address, _userName, _host, _port, _registerAddress, _registerABI, _paymentAddress, _paymentABI, _notaryAddress, _notaryABI, _paymentURL, _trailchainURL, _applicationURL):
        
        self.profile = {}
        self.profile['private_key'] = _privateKey
        self.profile['address'] = _address
        self.profile['host'] = _host
        self.profile['port'] = _port
        self.profile['userName'] = _userName
        
        #self.registerAddress = _registerAddress
        #self.registerABI = _registerABI
        #self.paymentAddress = _paymentAddress
        #self.paymentABI = _paymentABI
        #self.notaryAddress = _notaryAddress
        #self.notaryABI = _notaryABI

        self.applicationURL = _applicationURL
        self.paymentURL = _paymentURL
        self.trailchainURL = _trailchainURL


        _web3P = Web3(Web3.HTTPProvider(self.paymentURL))
        _web3M = Web3(Web3.HTTPProvider(self.applicationURL))
        _web3T = Web3(Web3.HTTPProvider(self.trailchainURL))
        
        _NotarySc = _web3T.eth.contract(address=_notaryAddress, abi=_notaryABI)
        _PaymentSc = _web3P.eth.contract(address=_paymentAddress, abi=_paymentABI)
        _RegisterSc = _web3M.eth.contract(address=_registerAddress, abi=_registerABI)
        
        self.contracts = {}
        self.contracts['application'] = {'Address': _registerAddress, 'ABI': _registerABI, 'web3': _web3M, 'contract': _RegisterSc}
        self.contracts['payment'] = {'Address': _paymentAddress, 'ABI': _paymentABI, 'web3': _web3P, 'contract': _PaymentSc}
        self.contracts['system'] = {'Address': _notaryAddress, 'ABI': _notaryABI, 'web3': _web3T, 'contract': _NotarySc}
        

        self.unregisteredPendingList = {}
        self.unpaidPendingList = {}

    def registerinTrailChain(self):

        NotarySc = self.contracts['system']['contract']
        web3T = self.contracts['system']['web3']

        RegisterSc = self.contracts['application']['contract']
        web3M = self.contracts['application']['web3']

        username = self.profile['userName']

        registerDigitalNotary_tx = NotarySc.functions.registerDigitalNotary().buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3T.eth.getTransactionCount(self.profile['address']),
            'gas': 3000000,
            'chainId': web3T.eth.chain_id,
        }
        )
        tx_create = web3T.eth.account.signTransaction(registerDigitalNotary_tx, self.profile['private_key'])
        tx_hash = web3T.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3T.eth.waitForTransactionReceipt(tx_hash)

        print('Digital notary is registered')

        MID = RegisterSc.functions.getMarketplaceID().call({'from': self.profile['address']})

        registerMarketplace_tx = NotarySc.functions.registerMarketplace(MID).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3T.eth.getTransactionCount(self.profile['address']),
            'chainId': web3T.eth.chain_id,
        }
        )
        tx_create = web3T.eth.account.signTransaction(registerMarketplace_tx, self.profile['private_key'])
        tx_hash = web3T.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3T.eth.waitForTransactionReceipt(tx_hash)

        print(f'[{username}]: Digital notary register marketplace in TrailChain')

    def pendingUnregisteredDataRequest(self):

        RegisterSc = self.contracts['application']['contract']
        
        dataList = RegisterSc.functions.retrieveunregisteredDataList().call({'from': self.profile['address']})
        validationList = []
        for data in dataList:
            _AID = Web3.toHex(data[2])
            _SellerAddress = RegisterSc.functions.getSellerInfo(_AID).call({'from': self.profile['address']})
            _Owner = Web3.toHex(RegisterSc.functions.actorList(_SellerAddress).call()[0])
            _MID = RegisterSc.functions.getMarketplaceID().call({'from': self.profile['address']})
            _DID = Web3.toHex(data[0])
            _SID = Web3.toHex(data[1])
            self.unregisteredPendingList[_SID] = {'AID': _AID,'Owner': _Owner, 'MarketplaceID': _MID}
            

    def dataOwnershipRegistrationProcess(self, _SID, _AID):

        NotarySc = self.contracts['system']['contract']
        web3T = self.contracts['system']['web3']

        RegisterSc = self.contracts['application']['contract']
        web3M = self.contracts['application']['web3']
        
        validationList = []
        username = self.profile['userName']
        _Owner = self.unregisteredPendingList[_SID]['Owner']
        _DID = _SID
        _MID = self.unregisteredPendingList[_SID]['MarketplaceID']
        _SellerAddress = RegisterSc.functions.getSellerInfo(_AID).call({'from': self.profile['address']})

        addNewDataTrail_tx = NotarySc.functions.addNewDataTrail(_Owner, _MID, _DID).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3T.eth.getTransactionCount(self.profile['address']),
            'gas': 3000000,
            'chainId': web3T.eth.chain_id,
        }
        )
        tx_create = web3T.eth.account.signTransaction(addNewDataTrail_tx, self.profile['private_key'])
        tx_hash = web3T.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3T.eth.waitForTransactionReceipt(tx_hash)
        gasUsed1 = tx_receipt.gasUsed

        logs = NotarySc.events.LogTID().processReceipt(tx_receipt, errors=DISCARD)
        _TID = Web3.toHex(logs[0]['args'][''])
        print(f'(4.2) [{username}]: Digital-Notary created a New Trade trail with ID: {_TID}')
        
        ##Generate Nonce, encrypt and send to the producer 
        nonce = int(''.join([str(random.randint(0, 9)) for i in range(8)]))
        result = Web3.toHex(Web3.soliditySha3(['uint256'], [nonce]))
        #subscriptionDetail = AIDContract.functions.subscriptions(_SID).call()
        
        _deviceID = RegisterSc.functions.getDevicefromSID(_AID, _SID).call({'from': self.profile['address']})
        Challenge, Response = RegisterSc.functions.getDeviceInfo(_deviceID, _SellerAddress).call()
        ##Send (Ency(Nonce),Response), Challenge, _TID

        ownershipRegistered_tx = RegisterSc.functions.ownershipRegistered(_DID, "validationStatus", result).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3M.eth.getTransactionCount(self.profile['address']),
            'chainId': web3M.eth.chain_id,
        }
        )
        tx_create = web3M.eth.account.signTransaction(ownershipRegistered_tx, self.profile['private_key'])
        tx_hash = web3M.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3M.eth.waitForTransactionReceipt(tx_hash)
        print(f'(4.3) [{username}]: created Nonce and updated in the RegisterSc')
        validationList.append([Challenge, nonce, _Owner, _TID, _SID, _AID])
        return validationList, gasUsed1, tx_receipt.gasUsed

    def sendRegistrationtoProducer(self, message, _producerHost, _producerPort):

        username = self.profile['userName']
        print(f'(4.4) [{username}]: encrypts (TID, Nonce, Challenge) and send to the data-producer')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((_producerHost, _producerPort))  
        s.sendall(message.encode(ENCODING))
        s.shutdown(2)
        s.close()

    def dataVerificationProcess(self, _filename):

        NotarySc = self.contracts['system']['contract']
        web3T = self.contracts['system']['web3']

        RegisterSc = self.contracts['application']['contract']
        web3M = self.contracts['application']['web3']
        
        username = self.profile['userName']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.profile['host'], self.profile['port']))
        sock.listen(10)
        mssg = []
        connection, client_address = sock.accept()
        while True:
            data = connection.recv(2048)
            if not data:
                break  # no more data coming in, so break out of the while loop
            mssg.append(data)  # add chunk to your already collected data
        message = mssg[0].decode(ENCODING)
        connection, client_address = sock.accept()
        textfile = open(_filename, "w")
        while True:
            data = connection.recv(1024)
            if not data:
                break  # no more data coming in, so break out of the while loop
            d1 = data.decode(ENCODING)
            textfile.write(d1)
        textfile.close()

    
        print(f"(7.2) [{username}]: Receives the verification requests from data-buyer")
    
        _extractedTID = watermarking_module.DetectExtractWatermark(_filename)

        print(f"(7.3) [{username}]: Extracts the watermarking from the verification packets")
        print(f">> Extracted watermarking: {_extractedTID}")
    
        _receivedSID = message[0:66]
        _receivedAID = message[66:132]

        #NotarySc = web3.eth.contract(address=notaryAddress, abi=notaryABI)
        #RegisterSc = web3.eth.contract(address=registerAddress, abi=registerABI)

        _MID =  RegisterSc.functions.getMarketplaceID().call({'from': self.profile['address']})
        _sellerAddress = RegisterSc.functions.getSellerInfo(_receivedAID).call({'from': self.profile['address']})
        _buyerAddress = RegisterSc.functions.getBuyerInfo(_receivedAID).call({'from': self.profile['address']})
        _seller = RegisterSc.functions.actorList(_sellerAddress).call()[0]
        _buyer = RegisterSc.functions.actorList(_buyerAddress).call()[0]


        print(f'(7.3) [{username}]: Validating the trail')
        validationResult = NotarySc.functions.validateTrail(_extractedTID, _seller, _buyer, _MID).call({'from': self.profile['address']})
        print(f'-> Validation result: {validationResult}')

        ##encrypt TID with notary's public key
        _value = _extractedTID
        authencityRegistered_tx = RegisterSc.functions.authencityRegistered(_receivedSID, _receivedAID, "verificationValue", _value).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3M.eth.getTransactionCount(self.profile['address']),
            'chainId': web3M.eth.chain_id,
        }
        )
        tx_create = web3M.eth.account.signTransaction(authencityRegistered_tx, self.profile['private_key'])
        tx_hash = web3M.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3M.eth.waitForTransactionReceipt(tx_hash)

        print(f'(7.5) [{username}]: Updates the proof of authencity for data-buyer')
        print(f">> authencityRegisteredNotarygasUsed: {tx_receipt.gasUsed}")


    def pendingPaymentList(self):

        RegisterSc = self.contracts['application']['contract']

        paymentList = RegisterSc.functions.retrieveunpaidList().call({'from': self.profile['address']})
        #self.unpaidPendingList = {'SID' : {'AID': '', 'TID': '', 'Buyer': '', 'Seller': '', 'Amount': 0, 'resellRatio': 0}}
        for _payment in paymentList:
            SID = Web3.toHex(_payment[0])
            self.unpaidPendingList[SID] = {
            'AID': Web3.toHex(_payment[1]),
            'TID': Web3.toHex(_payment[2]),
            'Buyer': Web3.toHex(_payment[3]),
            'Seller': Web3.toHex(_payment[4]),
            'Amount': _payment[5],
            'resellRatio': _payment[6]
            }
            

    def paymentSettlment(self, _SID):

        NotarySc = self.contracts['system']['contract']
        web3T = self.contracts['system']['web3']

        RegisterSc = self.contracts['application']['contract']
        web3M = self.contracts['application']['web3']

        PaymentSc = self.contracts['payment']['contract']
        web3P = self.contracts['payment']['web3']
        
        username = self.profile['userName']
        _AID = self.unpaidPendingList[_SID]['AID']
        _TID = self.unpaidPendingList[_SID]['TID']
        _buyer = self.unpaidPendingList[_SID]['Buyer']
        _seller = self.unpaidPendingList[_SID]['Seller']
        _amount = self.unpaidPendingList[_SID]['Amount']
        _resellratio = self.unpaidPendingList[_SID]['resellRatio']
        _MID = RegisterSc.functions.getMarketplaceID().call({'from': self.profile['address']})

        print(f'(8.2) {username}: Executes evaluatePaymentShare using NotarySc')
        evaluatePaymentShare_tx = NotarySc.functions.evaluatePaymentShare(_TID, _seller, _buyer, _resellratio, _MID, _SID, _amount).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3T.eth.getTransactionCount(self.profile['address']),
            'gas': 3000000,
            'chainId': web3T.eth.chain_id,
        }
        )
        tx_create = web3T.eth.account.signTransaction(evaluatePaymentShare_tx, self.profile['private_key'])
        tx_hash = web3T.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3T.eth.waitForTransactionReceipt(tx_hash)
        gasUsed1 = tx_receipt.gasUsed
        actorsList = []
        logs = NotarySc.events.PaymentactorList().processReceipt(tx_receipt, errors=DISCARD)
        list = logs[0]['args']['']
        
        for ele in list:
            actorsList.append(Web3.toHex(ele))

        logs = NotarySc.events.PaymentShareList().processReceipt(tx_receipt, errors=DISCARD)
        shareList = logs[0]['args']['']
    
        print(f'-> Payment share list : {actorsList, shareList}')

        print(f'(8.3) {username}: Executes paymentShare using PaymentSc')
        paymentShare_tx = PaymentSc.functions.paymentShare(actorsList, shareList, _buyer).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3P.eth.getTransactionCount(self.profile['address']),
            'chainId': web3P.eth.chain_id,
        }
        )
        tx_create = web3P.eth.account.signTransaction(paymentShare_tx, self.profile['private_key'])
        tx_hash = web3P.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3P.eth.waitForTransactionReceipt(tx_hash)
        gasUsed2 = tx_receipt.gasUsed

        registerPayment_tx = RegisterSc.functions.registerPayment(_SID).buildTransaction(
        {
            'from': self.profile['address'],
            'nonce': web3M.eth.getTransactionCount(self.profile['address']),
            'chainId': web3M.eth.chain_id,
        }
        )
        tx_create = web3M.eth.account.signTransaction(registerPayment_tx, self.profile['private_key'])
        tx_hash = web3M.eth.sendRawTransaction(tx_create.rawTransaction)
        tx_receipt = web3M.eth.waitForTransactionReceipt(tx_hash)
        print(f'(8.4) {username}: Executes registerPayment that marks the completion of payment settlement and subscription')
        gasUsed3 = tx_receipt.gasUsed

        return actorsList, _buyer, gasUsed1, gasUsed2, gasUsed3 


    
