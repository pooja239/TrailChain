####this script is to evaluate execution time of intre Vs intra and each component

import setup
import socket
from threading import Thread
import solcx
from solcx import get_solc_version, set_solc_version
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
import random
from digitalNotary import digitalNotary
from Actor import Actor
import time

entityList = {
    "digitalNotary1": {
        "privateKey": "63155c9fb9f75435273eb74227462c5dcbff4fdabc1bcf45c904adecc02ee18f", 
        "address": "0xDd50aeD42FDAB231bAC5e63829e50F52451b4B89", 
        "Name": "digitalNotary1", 
        "host": "127.0.0.1", 
        "port": 12000
    }, 
    "Actor1": {
        "privateKey": "3f88f6416e31a8ef981ca6eebbf3c210258cb30d47c58e5ecf7022b8fbc12bf2", 
        "address": "0xcC05E9588f22d29aDD2800E55d67C45C44F025E2", 
        "Name": "Actor1", 
        "host": "127.0.0.1", 
        "port": 12001
    }, 
    "Actor2": {
        "privateKey": "a111204b047cbb07d211ac0e6f7ba5d9d3b6a0bf6859728a52591841b4bcb8f0", 
        "address": "0x5991fF7EC7bf0f19B9a787BF6564DB54ee5c3693", 
        "Name": "Actor2", 
        "host": "127.0.0.1", 
        "port": 12002
    },
    "Actor3": {
        "privateKey": "b8ec9e1f9ab1675307830d20c6cf59d5a03f05b6dc4ea7cf3031ed11ff1f1df2", 
        "address": "0x19092a1c3b7419d4ecd37753Ff8d1B1596646267", 
        "Name": "Actor3", 
        "host": "127.0.0.1", 
        "port": 12003
    },
     "Actor4": {
        "privateKey": "8465788a2d95dd184d6da346b50d9becbb863f4640b0584385e52de5f52115fe", 
        "address": "0x5A1935A055533CdE754d7d0B9b209E39e8e1642d", 
        "Name": "Actor4", 
        "host": "127.0.0.1", 
        "port": 12004
    },
    "digitalNotary2": {
        "privateKey": "9be098e06f8754f46b5a59339fb4a44c83f406c56b838982a2f7228b394fe44a", 
        "address": "0x44c752e3199BE811a7D0413988A795a96116DED6", 
        "Name": "digitalNotary2", 
        "host": "127.0.0.1", 
        "port": 12005
    },
}

executiontime1 = []
executiontime2 = []
executiontime3 = []
##A1->selling->A2->reselling->A3-M1, A3-M2->reselling->A4

actorMapping = {}


paymentURL = 'http://127.0.0.1:5545'
trailchainURL = 'http://127.0.0.1:8545'
marketplace1URL = 'http://127.0.0.1:7545'
marketplace2URL = 'http://127.0.0.1:9545'
#marketplace2URL = 'http://127.0.0.1:8548'



for i in range(0,10):
    file_object = open('Exp1_Result.txt', 'a')
    print('\n********************************************************************')
    print('Initialization: Deploy System, payment and marketplace contracts')
    print('********************************************************************')

    #deploy system contracts
    notaryAddress, notaryABI, trackerAddress, trackerABI= setup.deploySystemcontracts(trailchainURL)

    #deploy payment contracts
    paymentAddress, paymentABI = setup.deployPaymentcontracts(paymentURL)

    #deploy Application contracts
    register1Address, register1ABI = setup.deployApplication1contracts(marketplace1URL,entityList['digitalNotary1']['address'], 'Marketplace1')

    #deploy Application contracts
    register2Address, register2ABI = setup.deployApplication1contracts(marketplace2URL,entityList['digitalNotary2']['address'], 'Marketplace2')

    print('\n********************************************************************')
    print('Create digital notary, data-producer and data-buyer instances for Marketplace1')
    print('********************************************************************')


                   
    _Notary1 = digitalNotary(entityList['digitalNotary1']['privateKey'], entityList['digitalNotary1']['address'], entityList['digitalNotary1']['Name'], entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, notaryAddress, notaryABI, paymentURL, trailchainURL, marketplace1URL)

    _Notary2 = digitalNotary(entityList['digitalNotary2']['privateKey'], entityList['digitalNotary2']['address'], entityList['digitalNotary2']['Name'], entityList['digitalNotary2']['host'], entityList['digitalNotary2']['port'], register2Address, register2ABI, paymentAddress, paymentABI, notaryAddress, notaryABI, paymentURL, trailchainURL, marketplace2URL)

    _Actor1 = Actor(entityList['Actor1']['privateKey'], entityList['Actor1']['address'], entityList['Actor1']['Name'], entityList['Actor1']['host'], entityList['Actor1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor2_M1 = Actor(entityList['Actor2']['privateKey'], entityList['Actor2']['address'], entityList['Actor2']['Name'], entityList['Actor2']['host'], entityList['Actor2']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor2_M2 = Actor(entityList['Actor2']['privateKey'], entityList['Actor2']['address'], entityList['Actor2']['Name'], entityList['Actor2']['host'], entityList['Actor2']['port'], register2Address, register2ABI, paymentAddress, paymentABI, marketplace2URL, paymentURL)

    _Actor3 = Actor(entityList['Actor3']['privateKey'], entityList['Actor3']['address'], entityList['Actor3']['Name'], entityList['Actor3']['host'], entityList['Actor3']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)


    _Actor4 = Actor(entityList['Actor4']['privateKey'], entityList['Actor4']['address'], entityList['Actor4']['Name'], entityList['Actor4']['host'], entityList['Actor4']['port'], register2Address, register2ABI, paymentAddress, paymentABI, marketplace2URL, paymentURL)


    print('\n********************************************************************')
    print('Registration and Setup: Register Actors, devices')
    print('********************************************************************')

    #register MP1 in TrailChain
    _Notary1.registerinTrailChain()
    _Notary2.registerinTrailChain()


    #create profile for actor1 in MP1 and payment layer and register his device
    ID, name = _Actor1.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor1}
    _Actor1.createProfileinPayment()
    #register actor1 device in MP1
    _Actor1.registerDevice("device1", 100, 100)

    #create profile for actor2 in MP1, MP2 and payment layer
    ID, name = _Actor2_M1.createProfileinMarketplace()
    _Actor2_M2.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor2_M1}

    _Actor2_M1.createProfileinPayment()

    #create profile for actor3 in MP1 and payment layer
    ID, name = _Actor3.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor3}
    _Actor3.createProfileinPayment()

    #create profile for actor4 in MP2 and payment layer and register his device
    ID, name = _Actor4.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor4}
    _Actor4.createProfileinPayment()

    print('-----------------------------------------------------------------------------------------------')
    print('\n*********************************   SELLING Scenario     ***********************************')
    print('-----------------------------------------------------------------------------------------------')

    selling_starttime = int(time.time())
    

    print('\n********************************************************************')
    print('Step 1: Deploy SubscriptionSc')
    print('********************************************************************')


    step11_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor1.deploySubscriptionSc(entityList['Actor2']['address'])
    _Actor2_M1.subscriptionAddress = subscriptionAddress
    _Actor2_M1.subscriptionABI = subscriptionABI
    step11_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step12_starttime = int(time.time())
    print('Step 2.1: Agreement registered by Seller')
    AID1 = _Actor1.registerAgreement(subscriptionAddress, subscriptionABI)

    print('Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor2_M1.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
       _AID = AID1
       print(f'>> Agreement ID is: {_AID}')
    step12_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step13_starttime = int(time.time())
    _SID = _Actor1.addSubscription(_AID, 'device1', 'GPS', 'realtime', 1000, 10)
    step13_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 4: Register new generated Dataset')
    print('********************************************************************')


    step14_starttime = int(time.time())
    _Actor1.registerData(_AID, _SID)

    _Notary1.pendingUnregisteredDataRequest()
    #validationList = [Challenge, nonce, _Owner, _TID, _SID, _AID]
    validationList = _Notary1.dataOwnershipRegistrationProcess(_SID, _AID)
    message = ''.join(validationList[0][2:])+' '+str(validationList[0][0])+' '+str(validationList[0][1])
    
    t1 = Thread(target=_Actor1.receiveRegistrationfromNotary, args=('data.txt',))
    t2 = Thread(target=_Notary1.sendRegistrationtoProducer, args=(message, entityList['Actor1']['host'], entityList['Actor1']['port']))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step14_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 5: Data-Buyer starts the subscription')
    print('********************************************************************')

    step15_starttime = int(time.time())
    _Actor2_M1.startSubscription(_AID, _SID)
    step15_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 6: Seller transfer data to Buyer')
    print('********************************************************************')

    step16_starttime = int(time.time())
    t1 = Thread(target=_Actor2_M1.receiveDatafromSeller, args=(_AID, _SID, 'receiveDatafromActor1.txt',))
    t2 = Thread(target=_Actor1.sendDatatoBuyer, args=(entityList['Actor2']['host'], entityList['Actor2']['port'], _AID, _SID, 'waterMarkedFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    step16_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 7: Buyer executes data verification process')
    print('********************************************************************')

    step17_starttime = int(time.time())
    _message = _SID + _AID
    _filename = "receiveDatafromActor1.txt"

    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor2M1.txt",))
    t2 = Thread(target=_Actor2_M1.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor2_M1.checkSubscriptionStatus(_AID, _SID)

    step17_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 8: Payment-Settlement')
    print('********************************************************************')

    step18_starttime = int(time.time())

    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor2_M1.checkSubscriptionStatus(_AID, _SID)

    step18_endtime = int(time.time())
    selling_endtime = int(time.time())

    print('\n********************************************************************')
    print('RESULT of SELLING')
    print('********************************************************************')


    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))

    
    selling_time = selling_endtime - selling_starttime 
    step11_time = step11_endtime - step11_starttime
    step12_time = step12_endtime - step12_starttime
    step13_time = step13_endtime - step13_starttime
    step14_time = step14_endtime - step14_starttime
    step15_time = step15_endtime - step15_starttime
    step16_time = step16_endtime - step16_starttime
    step17_time = step17_endtime - step17_starttime
    step18_time = step18_endtime - step18_starttime

    delimiter = ","
    
    result_time = "Selling" + delimiter + str(selling_time) + delimiter + str(step11_time) + delimiter + str(step12_time) + delimiter + str(step13_time) + delimiter + str(step14_time) + delimiter + str(step15_time) + delimiter + str(step16_time) + delimiter + str(step17_time)  + delimiter + str(step18_time) + '\n'
    file_object.write(result_time)
    
    print('-----------------------------------------------------------------------------------------------')
    print('\n*********************************   INTRA-RESELLING Scenario     ***********************************')
    print('-----------------------------------------------------------------------------------------------')

    intraselling_starttime = int(time.time())

    print('\n********************************************************************')
    print('Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor2_M1.deploySubscriptionSc(entityList['Actor3']['address'])
    _Actor3.subscriptionAddress = subscriptionAddress
    _Actor3.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print('Step 2.1: Agreement registered by Seller')
    AID1 = _Actor2_M1.registerAgreement(subscriptionAddress, subscriptionABI)

    print('Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor3.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())


    print('\n********************************************************************')
    print('Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor2_M1.addSubscription(_AID, 'device1', 'GPS', 'realtime', 1000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor2_M1.startSubscription(_AID, _SID)
    _Actor2_M1.sellerSendFile[_SID] = {'datasetFile': 'receiveDatafromActor1.txt', 'waterMarkedFile': ''}

    _Actor3.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor3.receiveDatafromSeller, args=(_AID, _SID, 'receiveDatafromActor2M1.txt',))
    t2 = Thread(target=_Actor2_M1.sendDatatoBuyer, args=(entityList['Actor3']['host'], entityList['Actor3']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor3.txt",))
    t2 = Thread(target=_Actor3.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor3.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())


    print('\n********************************************************************')
    print('Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor3.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    intraselling_endtime = int(time.time())

    print('\n********************************************************************')
    print('RESULT of Intra-reselling')
    print('********************************************************************')
   
    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))

    intraselling_time = intraselling_endtime - intraselling_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    
    result_time = "Intra-Selling" + delimiter + str(intraselling_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time) + '\n'
    file_object.write(result_time)

    print('-----------------------------------------------------------------------------------------------')
    print('\n*********************************   INTER-RESELLING Scenario     ***********************************')
    print('-----------------------------------------------------------------------------------------------')

    interselling_starttime = int(time.time())

    print('\n********************************************************************')
    print('Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step31_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor2_M2.deploySubscriptionSc(entityList['Actor4']['address'])
    _Actor4.subscriptionAddress = subscriptionAddress
    _Actor4.subscriptionABI = subscriptionABI
    step31_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step32_starttime = int(time.time())
    print('Step 2.1: Agreement registered by Seller')
    AID1 = _Actor2_M2.registerAgreement(subscriptionAddress, subscriptionABI)

    print('Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor4.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step32_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step33_starttime = int(time.time())
    _SID = _Actor2_M2.addSubscription(_AID, 'device1', 'GPS', 'realtime', 1000, 10)
    step33_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step34_starttime = int(time.time())
    _Actor2_M2.startSubscription(_AID, _SID)
    _Actor2_M2.sellerSendFile[_SID] = {'datasetFile': 'receiveDatafromActor1.txt', 'waterMarkedFile': ''}

    _Actor4.startSubscription(_AID, _SID)
    step34_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step35_starttime = int(time.time())
    t1 = Thread(target=_Actor4.receiveDatafromSeller, args=(_AID, _SID, 'receiveDatafromActor2M2.txt',))
    t2 = Thread(target=_Actor2_M2.sendDatatoBuyer, args=(entityList['Actor4']['host'], entityList['Actor4']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step35_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 6: Buyer executes data verification process')
    print('********************************************************************')

    
    step36_starttime = int(time.time())
    t1 = Thread(target=_Notary2.dataVerificationProcess, args=("receivedDVPfromActor4.txt",))
    t2 = Thread(target=_Actor4.sendDataVerificationRequest, args=(entityList['digitalNotary2']['host'], entityList['digitalNotary2']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor4.checkSubscriptionStatus(_AID, _SID)
    step36_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 7: Payment-Settlement')
    print('********************************************************************')


    step37_starttime = int(time.time())
    _Notary2.pendingPaymentList()
    actorList, _buyer = _Notary2.paymentSettlment(_SID)
    _Actor4.checkSubscriptionStatus(_AID, _SID)
    step37_endtime = int(time.time())
    interselling_endtime = int(time.time())

    print('\n********************************************************************')
    print('RESULT of Inter-reselling')
    print('********************************************************************')


    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))

    
    interselling_time = interselling_endtime - interselling_starttime 
    step31_time = step31_endtime - step31_starttime
    step32_time = step32_endtime - step32_starttime
    step33_time = step33_endtime - step33_starttime
    step34_time = step34_endtime - step34_starttime
    step35_time = step35_endtime - step35_starttime
    step36_time = step36_endtime - step36_starttime
    step37_time = step37_endtime - step37_starttime
    
    
    result_time = "Inter-Selling" + delimiter + str(interselling_time) + delimiter + str(step31_time) + delimiter + str(step32_time) + delimiter + str(step33_time) + delimiter + "NA" + delimiter + str(step34_time) + delimiter + str(step35_time) + delimiter + str(step36_time) + delimiter + str(step37_time) + '\n'
    file_object.write(result_time)
    file_object.close()

