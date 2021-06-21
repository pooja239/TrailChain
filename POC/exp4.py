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
        "privateKey": "8452fbc43711404d0b20bfb978cdc9082d8fd78100b51c14fa6265b798fa11a8", 
        "address": "0xEBDAF5366c785c642c4b17753D981968deAD9c94", 
        "Name": "digitalNotary1", 
        "host": "127.0.0.1", 
        "port": 12000
    }, 
    "Actor1": {
        "privateKey": "4a464e10ba1d7baa0e9f7800b9184273035044647586c6f25902960d0e0e5090", 
        "address": "0xaB0A83FeCe5E5287782ed22FDd60c26664804273", 
        "Name": "Actor1", 
        "host": "127.0.0.1", 
        "port": 12001
    }, 
    "Actor2": {
        "privateKey": "f1f6652a0bd7682b9cc35fea7b298d890883cbf09fbfe441d95ca9fb7b611cfd", 
        "address": "0xF5cFe897D5AA7330693E0C20f568503043a271B9", 
        "Name": "Actor2", 
        "host": "127.0.0.1", 
        "port": 12002
    },
    "Actor3": {
        "privateKey": "8241e39e01512155cd98524531572c1529c3674ca52685bbfc7e6492454086ec", 
        "address": "0x312BF41E058a83059B251FfC92b146cb876858B4", 
        "Name": "Actor3", 
        "host": "127.0.0.1", 
        "port": 12003
    },
}


##A1->selling->A2->reselling->A3-M1, A3-M2->reselling->A4

actorMapping = {}


paymentURL = 'http://127.0.0.1:9545'
trailchainURL = 'http://127.0.0.1:9545'
marketplace1URL = 'http://127.0.0.1:9545'




for i in range(0,10):
    

    print('\n--------------------------------------------------------------------------------------------------------------------------------------')
    print('Iteration: ' + str(i))
    print('--------------------------------------------------------------------------------------------------------------------------------------')

    print('\n********************************************************************')
    print('Initialization: Deploy System, payment and marketplace contracts')
    print('********************************************************************')

    #deploy system contracts
    notaryAddress, notaryABI, trackerAddress, trackerABI, notarygasUsed, trackergasUsed= setup.deploySystemcontracts(trailchainURL)

    #deploy payment contracts
    paymentAddress, paymentABI, paymentgasUsed = setup.deployPaymentcontracts(paymentURL)

    #deploy Application contracts
    register1Address, register1ABI, applicationgasUsed = setup.deployApplication1contracts(marketplace1URL,entityList['digitalNotary1']['address'], 'Marketplace1')

    print('\n********************************************************************')
    print('Create digital notary, data-producer and data-buyer instances for Marketplace1')
    print('********************************************************************')


                   
    _Notary1 = digitalNotary(entityList['digitalNotary1']['privateKey'], entityList['digitalNotary1']['address'], entityList['digitalNotary1']['Name'], entityList['digitalNotary1']['host'], entityList['digitalNotary1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, notaryAddress, notaryABI, paymentURL, trailchainURL, marketplace1URL)

    _Actor1 = Actor(entityList['Actor1']['privateKey'], entityList['Actor1']['address'], entityList['Actor1']['Name'], entityList['Actor1']['host'], entityList['Actor1']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor2 = Actor(entityList['Actor2']['privateKey'], entityList['Actor2']['address'], entityList['Actor2']['Name'], entityList['Actor2']['host'], entityList['Actor2']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)

    _Actor3 = Actor(entityList['Actor3']['privateKey'], entityList['Actor3']['address'], entityList['Actor3']['Name'], entityList['Actor3']['host'], entityList['Actor3']['port'], register1Address, register1ABI, paymentAddress, paymentABI, marketplace1URL, paymentURL)



    print('\n********************************************************************')
    print('Registration and Setup: Register Actors, devices')
    print('********************************************************************')

    #register MP1 in TrailChain
    _Notary1.registerinTrailChain()
    
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

    #create profile for actor3 in MP1 and payment layer
    ID, name = _Actor3.createProfileinMarketplace()
    actorMapping[ID] = {'Name': name, 'Object': _Actor3}
    _Actor3.createProfileinPayment()


    print('-----------------------------------------------------------------------------------------------')
    print('\n*********************************   SELLING Scenario     ***********************************')
    print('-----------------------------------------------------------------------------------------------')

    print('\n********************************************************************')
    print('Step 1: Deploy SubscriptionSc')
    print('********************************************************************')


    subscriptionAddress, subscriptionABI, deploySellergasUsed = _Actor1.deploySubscriptionSc(entityList['Actor2']['address'])
    _Actor2.subscriptionAddress = subscriptionAddress
    _Actor2.subscriptionABI = subscriptionABI

    
    print(">> notarygasUsed: " + str(notarygasUsed))
    print(">> trackergasUsed: " + str(trackergasUsed))
    print(">> paymentgasUsed: " + str(paymentgasUsed))
    print(">> applicationgasUsed: " + str(applicationgasUsed))
    print(">> deploySellergasUsed: " + str(deploySellergasUsed))

