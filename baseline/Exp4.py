####this script is to evaluate execution time of intre Vs intra and each component

import setup
import socket
from threading import Thread
import solcx
from solcx import get_solc_version, set_solc_version
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
import random
from Actor import Actor
import time

entityList = { 
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
}

executiontime1 = []
executiontime2 = []

##A1->selling->A2

actorMapping = {}


paymentURL = 'http://127.0.0.1:7545'
marketplaceURL = 'http://127.0.0.1:7545'



for i in range(0,10):
    file_object = open('Exp4_Result.txt', 'a')
    print('\n********************************************************************')
    print('Initialization: Deploy payment and marketplace contracts')
    print('********************************************************************')

    #deploy payment contracts
    paymentAddress, paymentABI = setup.deployPaymentcontracts(paymentURL)

    #deploy Application contracts
    registerAddress, registerABI = setup.deployApplicationcontracts(marketplaceURL,'Marketplace1', paymentAddress)

  
    print('\n********************************************************************')
    print('Create data-seller and data-buyer instances for Marketplace')
    print('********************************************************************')


    _Actor1 = Actor(entityList['Actor1']['privateKey'], entityList['Actor1']['address'], entityList['Actor1']['Name'], entityList['Actor1']['host'], entityList['Actor1']['port'], registerAddress, registerABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor2 = Actor(entityList['Actor2']['privateKey'], entityList['Actor2']['address'], entityList['Actor2']['Name'], entityList['Actor2']['host'], entityList['Actor2']['port'], registerAddress, registerABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)



    print('\n********************************************************************')
    print('Registration and Setup: Register Actors, devices')
    print('********************************************************************')


    #create profile for actor1 in MP1 and payment layer and register his device
    ID, name = _Actor1.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor1}
    _Actor1.createProfileinPayment()
    #register actor1 device in MP1
    _Actor1.registerDevice("device1", 100, 100)

    #create profile for actor2 in MP1, MP2 and payment layer
    ID, name = _Actor2.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor2}

    _Actor2.createProfileinPayment()



    print('-----------------------------------------------------------------------------------------------')
    print('\n*********************************   SELLING Scenario     ***********************************')
    print('-----------------------------------------------------------------------------------------------')

    selling_starttime = int(time.time())
    

    print('\n********************************************************************')
    print('Step 1: Deploy SubscriptionSc')
    print('********************************************************************')


    step11_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor1.deploySubscriptionSc(entityList['Actor2']['address'])
    _Actor2.subscriptionAddress = subscriptionAddress
    _Actor2.subscriptionABI = subscriptionABI
    step11_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step12_starttime = int(time.time())
    print('Step 2.1: Agreement registered by Seller')
    AID1 = _Actor1.registerAgreement(subscriptionAddress, subscriptionABI)

    print('Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor2.registerAgreement(subscriptionAddress, subscriptionABI)


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
    print('Step 4: Data-Buyer starts the subscription')
    print('********************************************************************')

    step15_starttime = int(time.time())
    _Actor1.startSubscription(_AID, _SID)
	_Actor2.startSubscription(_AID, _SID)
    step15_endtime = int(time.time())

    print('\n********************************************************************')
    print('Step 6: Seller transfer data to Buyer')
    print('********************************************************************')

    step16_starttime = int(time.time())
    t1 = Thread(target=_Actor2.receiveDatafromSeller, args=(_AID, _SID, 'receiveDatafromActor1.txt',))
    t2 = Thread(target=_Actor1.sendDatatoBuyer, args=(entityList['Actor2']['host'], entityList['Actor2']['port'], _AID, _SID, 'data.txt'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    step16_endtime = int(time.time())


    print('\n********************************************************************')
    print('Step 8: Payment-Settlement')
    print('********************************************************************')

    step18_starttime = int(time.time())
    _Actor2.confirmDelivery(_AID, _SID)
    step18_endtime = int(time.time())
    selling_endtime = int(time.time())

    print('\n********************************************************************')
    print('RESULT of SELLING')
    print('********************************************************************')


    buyerbalance = _Actor2.checkBalance()
	sellerbalance = _Actor1.checkBalance()
    print('->Buyer Account Balance: ' + str(buyerbalance))
	print('->Seller Account Balance: ' + str(sellerbalance))

    
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
    
