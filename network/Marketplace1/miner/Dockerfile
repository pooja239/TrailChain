FROM ubuntu:bionic

RUN apt-get update \
     && apt-get install -y wget software-properties-common \
     && rm -rf /var/lib/apt/lists/*

WORKDIR "/root"

RUN add-apt-repository -y ppa:ethereum/ethereum

ARG binary
RUN apt-get update \
     && apt-get install -y ethereum

ARG password
ARG privatekey
RUN echo $password > ~/.accountpassword
RUN echo $privatekey > ~/.privatekey

ADD ./genesis.json ./genesis.json
ADD ./miner-start.sh ./miner-start.sh
RUN chmod +x ./miner-start.sh
RUN geth init genesis.json
RUN geth account import --password ~/.accountpassword  ~/.privatekey

ADD ./full-R23-0000000000000000 /root/.ethash/full-R23-0000000000000000
ADD ./full-R23-290decd9548b62a8 /root/.ethash/full-R23-290decd9548b62a8

ENV bootnodeId=""
ENV bootnodeIp=""

CMD exec ./miner-start.sh $bootnodeId $bootnodeIp

EXPOSE 8545
EXPOSE 30303
