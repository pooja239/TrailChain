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
    "Actor5": {
        "privateKey": "9be098e06f8754f46b5a59339fb4a44c83f406c56b838982a2f7228b394fe44a", 
        "address": "0x44c752e3199BE811a7D0413988A795a96116DED6",
        "Name": "Actor5", 
        "host": "127.0.0.1", 
        "port": 12005
    },
    "Actor6": {
        "privateKey": "1fe406082a24987d4c63cc9609ad31ac14cc691ec64c9bfb9643ef06c811687b", 
        "address": "0x4c5fcE13458cc5f6b31E31D0F91fa826e955ccfc",
        "Name": "Actor6", 
        "host": "127.0.0.1", 
        "port": 12006
    },
    "Actor7": {
        "privateKey": "f1a95f7f56c1969fcefdd86e53bab47111c7426548d51e93d6018a2f22d6c431", 
        "address": "0x4dcFc37c19bC8005B7Bb8198ce4d2583C4AFFFc4",
        "Name": "Actor7", 
        "host": "127.0.0.1", 
        "port": 12007
    },
    "Actor8": {
        "privateKey": "638342ea0b55633c801f6b298c0f108eaf2cff5e062ed8cf50576fc84a687f27", 
        "address": "0xEB6A44ffC10b9Fd571fA4F84DA9699003be2D1D2",
        "Name": "Actor8", 
        "host": "127.0.0.1", 
        "port": 12008
    },
    "Actor9": {
        "privateKey": "548ecab60ef6cac6d9faef295660807020767cf9de8876263a8f1f8751df0aa8", 
        "address": "0x6939668C71407FE2184326F8016930e42E1fA067",
        "Name": "Actor9", 
        "host": "127.0.0.1", 
        "port": 12009
    }
}


##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

actorMapping = {}


#paymentURL = 'http://127.0.0.1:8545'
#trailchainURL = 'http://127.0.0.1:8545'
#marketplace1URL = 'http://127.0.0.1:8545'

paymentURL = 'http://127.0.0.1:5545'
trailchainURL = 'http://127.0.0.1:8545'
marketplace1URL = 'http://127.0.0.1:7545'

for i in range(0,1):

    file_object = open('Exp2_Result.txt', 'a')

    if i!=0:
        os.remove("watermarkedData.txt")
        os.remove("Actor2receiveDatafromActor1.txt")
        os.remove("Actor3receiveDatafromActor2.txt")
        os.remove("Actor4receiveDatafromActor3.txt")
        os.remove("Actor5receiveDatafromActor4.txt")
        os.remove("Actor6receiveDatafromActor5.txt")
        os.remove("Actor7receiveDatafromActor6.txt")
        os.remove("Actor8receiveDatafromActor7.txt")
        os.remove("Actor9receiveDatafromActor8.txt")
        os.remove("receivedDVPfromActor2.txt")
        os.remove("receivedDVPfromActor3.txt")
        os.remove("receivedDVPfromActor4.txt")
        os.remove("receivedDVPfromActor5.txt")
        os.remove("receivedDVPfromActor6.txt")
        os.remove("receivedDVPfromActor7.txt")
        os.remove("receivedDVPfromActor8.txt")
        os.remove("receivedDVPfromActor9.txt")
        del _Notary1
        del _Actor1
        del _Actor2
        del _Actor3
        del _Actor4
        del _Actor5
        del _Actor6
        del _Actor7
        del _Actor8
        del _Actor9

    print('\n********************************************************************')
    print('Initialization: Deploy System, payment and marketplace contracts')
    print('********************************************************************')

    #deploy system contracts
    notaryAddress, notaryABI, trackerAddress, trackerABI= setup.deploySystemcontracts(trailchainURL)

    #deploy payment contracts
    paymentAddress, paymentABI = setup.deployPaymentcontracts(paymentURL)

    #deploy Application contracts
    register1Address, register1ABI = setup.deployApplication1contracts(marketplace1URL,entityList['digitalNotary1']['address'], 'Marketplace1')

    print('\n********************************************************************')
    print(f'Create digital notary, data-producer and data-buyer instances for Marketplace1')
    print('********************************************************************')
                  
    _Notary1 = digitalNotary(entityList['digitalNotary1']['privateKey'], entityList['digitalNotary1']['address'], entityList['digitalNotary1']['Name'], entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, notaryAddress, notaryABI, paymentURL, trailchainURL, marketplace1URL)

    _Actor1 = Actor(entityList['Actor1']['privateKey'], entityList['Actor1']['address'], entityList['Actor1']['Name'], entityList['Actor1']['host'], entityList['Actor1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor2 = Actor(entityList['Actor2']['privateKey'], entityList['Actor2']['address'], entityList['Actor2']['Name'], entityList['Actor2']['host'], entityList['Actor2']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor3 = Actor(entityList['Actor3']['privateKey'], entityList['Actor3']['address'], entityList['Actor3']['Name'], entityList['Actor3']['host'], entityList['Actor3']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor4 = Actor(entityList['Actor4']['privateKey'], entityList['Actor4']['address'], entityList['Actor4']['Name'], entityList['Actor4']['host'], entityList['Actor4']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor5 = Actor(entityList['Actor5']['privateKey'], entityList['Actor5']['address'], entityList['Actor5']['Name'], entityList['Actor5']['host'], entityList['Actor5']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor6 = Actor(entityList['Actor6']['privateKey'], entityList['Actor6']['address'], entityList['Actor6']['Name'], entityList['Actor6']['host'], entityList['Actor6']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor7 = Actor(entityList['Actor7']['privateKey'], entityList['Actor7']['address'], entityList['Actor7']['Name'], entityList['Actor7']['host'], entityList['Actor7']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor8 = Actor(entityList['Actor8']['privateKey'], entityList['Actor8']['address'], entityList['Actor8']['Name'], entityList['Actor8']['host'], entityList['Actor8']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor9 = Actor(entityList['Actor9']['privateKey'], entityList['Actor9']['address'], entityList['Actor9']['Name'], entityList['Actor9']['host'], entityList['Actor9']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)


    print('\n********************************************************************')
    print(f'Registration and Setup: Register Actors, devices')
    print('********************************************************************')

    #register MP1 in TrailChain
    _Notary1.registerinTrailChain()

    #create profile for actor1 in MP1 and payment layer
    ID, name = _Actor1.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor1}
    _Actor1.createProfileinPayment()
    #register actor1 device in MP1
    _Actor1.registerDevice("device1", 100, 100)

    ID, name = _Actor2.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor2}
    _Actor2.createProfileinPayment()

    ID, name = _Actor3.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor3}
    _Actor3.createProfileinPayment()

    ID, name = _Actor4.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor4}
    _Actor4.createProfileinPayment()

    ID, name = _Actor5.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor5}
    _Actor5.createProfileinPayment()

    ID, name = _Actor6.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor6}
    _Actor6.createProfileinPayment()

    ID, name = _Actor7.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor7}
    _Actor7.createProfileinPayment()

    ID, name = _Actor8.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor8}
    _Actor8.createProfileinPayment()

    ID, name = _Actor9.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor9}
    _Actor9.createProfileinPayment()


    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   SELLING Scenario     ***********************************')

    selling_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step11_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor1.deploySubscriptionSc(entityList['Actor2']['address'])
    _Actor2.subscriptionAddress = subscriptionAddress
    _Actor2.subscriptionABI = subscriptionABI
    step11_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step12_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor1.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor2.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step12_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step13_starttime = int(time.time())
    _SID = _Actor1.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step13_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Register new generated Dataset')
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
    print(f'Step 5: Data-Buyer starts the subscription')
    print('********************************************************************')

    step15_starttime = int(time.time())
    _Actor2.startSubscription(_AID, _SID)
    step15_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Seller transfer data to Buyer')
    print('********************************************************************')

    step16_starttime = int(time.time())
    t1 = Thread(target=_Actor2.receiveDatafromSeller, args=(_AID, _SID, 'Actor2receiveDatafromActor1.txt',))
    t2 = Thread(target=_Actor1.sendDatatoBuyer, args=(entityList['Actor2']['host'], entityList['Actor2']['port'], _AID, _SID, 'waterMarkedFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step16_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Buyer executes data verification process')
    print('********************************************************************')


    step17_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor2.txt",))
    t2 = Thread(target=_Actor2.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor2.checkSubscriptionStatus(_AID, _SID)
    step17_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 8: Payment-Settlement')
    print('********************************************************************')

    step18_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor2.checkSubscriptionStatus(_AID, _SID)
    step18_endtime = int(time.time())

    selling_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT of SELLING')
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

    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-1 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor2.deploySubscriptionSc(entityList['Actor3']['address'])
    _Actor3.subscriptionAddress = subscriptionAddress
    _Actor3.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor2.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor3.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor2.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor2.startSubscription(_AID, _SID)
    _Actor2.sellerSendFile[_SID] = {'datasetFile': 'Actor2receiveDatafromActor1.txt', 'waterMarkedFile': ''}

    _Actor3.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor3.receiveDatafromSeller, args=(_AID, _SID, 'Actor3receiveDatafromActor2.txt',))
    t2 = Thread(target=_Actor2.sendDatatoBuyer, args=(entityList['Actor3']['host'], entityList['Actor3']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
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
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor3.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling1" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time)  + '\n'
    file_object.write(result_time)


    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-2 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor3.deploySubscriptionSc(entityList['Actor4']['address'])
    _Actor4.subscriptionAddress = subscriptionAddress
    _Actor4.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor3.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor4.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor3.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor3.startSubscription(_AID, _SID)
    _Actor3.sellerSendFile[_SID] = {'datasetFile': 'Actor3receiveDatafromActor2.txt', 'waterMarkedFile': ''}

    _Actor4.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor4.receiveDatafromSeller, args=(_AID, _SID, 'Actor4receiveDatafromActor3.txt',))
    t2 = Thread(target=_Actor3.sendDatatoBuyer, args=(entityList['Actor4']['host'], entityList['Actor4']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor4.txt",))
    t2 = Thread(target=_Actor4.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor4.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor4.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling2" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time) + '\n'
    file_object.write(result_time)
    
    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-3 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor4.deploySubscriptionSc(entityList['Actor5']['address'])
    _Actor5.subscriptionAddress = subscriptionAddress
    _Actor5.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor4.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor5.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor4.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor4.startSubscription(_AID, _SID)
    _Actor4.sellerSendFile[_SID] = {'datasetFile': 'Actor4receiveDatafromActor3.txt', 'waterMarkedFile': ''}

    _Actor5.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor5.receiveDatafromSeller, args=(_AID, _SID, 'Actor5receiveDatafromActor4.txt',))
    t2 = Thread(target=_Actor4.sendDatatoBuyer, args=(entityList['Actor5']['host'], entityList['Actor5']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor5.txt",))
    t2 = Thread(target=_Actor5.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor5.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor5.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling3" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time) + '\n'
    
    file_object.write(result_time)

    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-4 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor5.deploySubscriptionSc(entityList['Actor6']['address'])
    _Actor6.subscriptionAddress = subscriptionAddress
    _Actor6.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor5.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor6.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor5.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor5.startSubscription(_AID, _SID)
    _Actor5.sellerSendFile[_SID] = {'datasetFile': 'Actor5receiveDatafromActor4.txt', 'waterMarkedFile': ''}

    _Actor6.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor6.receiveDatafromSeller, args=(_AID, _SID, 'Actor6receiveDatafromActor5.txt',))
    t2 = Thread(target=_Actor5.sendDatatoBuyer, args=(entityList['Actor6']['host'], entityList['Actor6']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor6.txt",))
    t2 = Thread(target=_Actor6.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor6.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor6.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling4" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time)  + '\n'
    
    file_object.write(result_time)


    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-5 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor6.deploySubscriptionSc(entityList['Actor7']['address'])
    _Actor7.subscriptionAddress = subscriptionAddress
    _Actor7.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor6.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor7.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor6.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor6.startSubscription(_AID, _SID)
    _Actor6.sellerSendFile[_SID] = {'datasetFile': 'Actor6receiveDatafromActor5.txt', 'waterMarkedFile': ''}

    _Actor7.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor7.receiveDatafromSeller, args=(_AID, _SID, 'Actor7receiveDatafromActor6.txt',))
    t2 = Thread(target=_Actor6.sendDatatoBuyer, args=(entityList['Actor7']['host'], entityList['Actor7']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor7.txt",))
    t2 = Thread(target=_Actor7.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor7.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor7.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling5" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time)  + '\n'
    
    file_object.write(result_time)


    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-6 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor7.deploySubscriptionSc(entityList['Actor8']['address'])
    _Actor8.subscriptionAddress = subscriptionAddress
    _Actor8.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor7.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor8.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor7.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor7.startSubscription(_AID, _SID)
    _Actor7.sellerSendFile[_SID] = {'datasetFile': 'Actor7receiveDatafromActor6.txt', 'waterMarkedFile': ''}

    _Actor8.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor8.receiveDatafromSeller, args=(_AID, _SID, 'Actor8receiveDatafromActor7.txt',))
    t2 = Thread(target=_Actor7.sendDatatoBuyer, args=(entityList['Actor8']['host'], entityList['Actor8']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor8.txt",))
    t2 = Thread(target=_Actor8.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor8.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor8.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling6" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time)  + '\n'
    
    file_object.write(result_time)

    ##A1->selling->A2->reselling1->A3->reselling2->A4->reselling3->A5->reselling4->A6->reselling5->A7->reselling6->A8->reselling7->A9

    print('\n*********************************   RESELLING-7 Scenario     ***********************************')

    reselling1_starttime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 1: Deploy SubscriptionSc')
    print('********************************************************************')

    step21_starttime = int(time.time())
    subscriptionAddress, subscriptionABI = _Actor8.deploySubscriptionSc(entityList['Actor9']['address'])
    _Actor9.subscriptionAddress = subscriptionAddress
    _Actor9.subscriptionABI = subscriptionABI
    step21_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 2: Register SubscriptionSc')
    print('********************************************************************')

    step22_starttime = int(time.time())
    print(f'Step 2.1: Agreement registered by Seller')
    AID1 = _Actor8.registerAgreement(subscriptionAddress, subscriptionABI)

    print(f'Step 2.2: Agreement registered by Buyer')
    AID2 = _Actor9.registerAgreement(subscriptionAddress, subscriptionABI)


    if (AID1 == AID2):
        _AID = AID1
        print(f'>> Agreement ID is: {_AID}')
    step22_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 3: Add subscription by producer: device1, GPS, realtime, 1000, 10')
    print('********************************************************************')

    step23_starttime = int(time.time())
    _SID = _Actor8.addSubscription(_AID, 'device1', 'GPS', 'realtime', 10000000, 10)
    step23_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 4: Data-Buyer and data-seller starts the subscription')
    print('********************************************************************')

    step24_starttime = int(time.time())
    _Actor8.startSubscription(_AID, _SID)
    _Actor8.sellerSendFile[_SID] = {'datasetFile': 'Actor8receiveDatafromActor7.txt', 'waterMarkedFile': ''}

    _Actor9.startSubscription(_AID, _SID)
    step24_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 5: Seller transfer data to Buyer')
    print('********************************************************************')

    step25_starttime = int(time.time())
    t1 = Thread(target=_Actor9.receiveDatafromSeller, args=(_AID, _SID, 'Actor9receiveDatafromActor8.txt',))
    t2 = Thread(target=_Actor8.sendDatatoBuyer, args=(entityList['Actor9']['host'], entityList['Actor9']['port'], _AID, _SID, 'datasetFile'))

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    step25_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 6: Buyer executes data verification process')
    print('********************************************************************')

    step26_starttime = int(time.time())
    t1 = Thread(target=_Notary1.dataVerificationProcess, args=("receivedDVPfromActor9.txt",))
    t2 = Thread(target=_Actor9.sendDataVerificationRequest, args=(entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], _SID, _AID))


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    _Actor9.checkSubscriptionStatus(_AID, _SID)
    step26_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'Step 7: Payment-Settlement')
    print('********************************************************************')

    step27_starttime = int(time.time())
    _Notary1.pendingPaymentList()
    actorList, _buyer = _Notary1.paymentSettlment(_SID)
    _Actor9.checkSubscriptionStatus(_AID, _SID)
    step27_endtime = int(time.time())
    reselling1_endtime = int(time.time())

    print('\n********************************************************************')
    print(f'RESULT')
    print('********************************************************************')

    actorbalance = actorMapping[_buyer]['Object'].checkBalance()
    print('->Buyer: ' + actorMapping[_buyer]['Name'] + ' Account Balance: ' + str(actorbalance))
    for ele in  actorList:
        actorbalance = actorMapping[ele]['Object'].checkBalance()
        print('->Owner: ' + actorMapping[ele]['Name'] + ' Account Balance: ' + str(actorbalance))


    reselling1_time = reselling1_endtime - reselling1_starttime 
    step21_time = step21_endtime - step21_starttime
    step22_time = step22_endtime - step22_starttime
    step23_time = step23_endtime - step23_starttime
    step24_time = step24_endtime - step24_starttime
    step25_time = step25_endtime - step25_starttime
    step26_time = step26_endtime - step26_starttime
    step27_time = step27_endtime - step27_starttime
    
    delimiter = ","
    
    result_time = "ReSelling7" + delimiter + str(reselling1_time) + delimiter + str(step21_time) + delimiter + str(step22_time) + delimiter + str(step23_time) + delimiter + "NA" + delimiter + str(step24_time) + delimiter + str(step25_time) + delimiter + str(step26_time) + delimiter + str(step27_time) + '\n'
    
    file_object.write(result_time)
    file_object.close()
