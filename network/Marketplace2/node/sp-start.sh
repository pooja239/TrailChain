#!/bin/sh
# geth account new --password ~/.accountpassword

geth --bootnodes "enode://$bootnodeId@$bootnodeIp:30301" \
     --networkid 3404061304910 \
     --nousb \
     --rpc \
     --rpcaddr "0.0.0.0" \
     --rpcapi "eth,web3,net,admin,debug,db,personal" \
     --rpccorsdomain "*" \
     --syncmode="fast" \
     --unlock 0 \
     --password ~/.accountpassword \
     --allow-insecure-unlock
