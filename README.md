TrailChain
--------------------------------------------
This is the POC implementation of TrailChain framework

Folder Structure
- POC :
  - Contracts: contains all the smart contracts including 
  - Actor.py: Class to define method and attricbutes for actor profile in marketplace
  - digitalNotary.py: Class to define method and attricbutes for notary profile in marketplace
  - setup.py: deploys all the smart contracts in the network
  - data.txt: contains GPS data samples to be send from seller to buyer
  - output.txt: It is the sample log for demonstrating various steps involved in selling, intra-reselling and inter-reselling

- Basline: Contains the implementation of baseline

- Network: A private ethereum network consists of 2 nodes+ 1 miner + 1 bootnode
  - Marketplace1: Deploys a set of registerSc and SubscriptionSc
  - Marketplace2: Deploys another set of registerSc and SubscriptionSc
  - TrailChain: Deploys a set of NotarySc and TrackerSc
  - Payment: Deploys PaymentSc
  
- caliper_benchmark: contains all the config files to run tests on the SUT in Layer-2 eqipped with TrackerSc and NotarySc for benchmarking purpose.