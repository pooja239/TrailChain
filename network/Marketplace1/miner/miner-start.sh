#!/bin/sh
# geth account new  --password ~/.accountpassword

geth --bootnodes "enode://$bootnodeId@$bootnodeIp:30301" \
     --networkid 34040613049100 \
     --nousb \
     --syncmode=full \
     --mine \
     --miner.threads 1 \
     --miner.gasprice "0" \
     --rpc \
     --rpcaddr "0.0.0.0" \
     --rpcapi "eth,web3,net,admin,debug,db,personal" \
     --rpccorsdomain "*" \
     --unlock 0 \
     --password ~/.accountpassword \
     --allow-insecure-unlock \
     --nat "any"
     