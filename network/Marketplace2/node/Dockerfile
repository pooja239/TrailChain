FROM ubuntu:bionic

RUN apt-get update \
     && apt-get install -y wget software-properties-common \
     && rm -rf /var/lib/apt/lists/*

WORKDIR "/root"

RUN add-apt-repository -y ppa:ethereum/ethereum

ARG binary
RUN apt-get update \
     && apt-get install -y ethereum
RUN apt-get install -y solc
RUN apt-get install -y python3-pip

ARG password
ARG privatekey
RUN echo $password > ~/.accountpassword
RUN echo $privatekey > ~/.privatekey

ADD ./genesis.json ./genesis.json
ADD ./sc-start.sh ./sc-start.sh
ADD ./sp-start.sh ./sp-start.sh
ADD ./requirements.txt ./requirements.txt
RUN chmod +x ./sc-start.sh
RUN chmod +x ./sp-start.sh

RUN pip3 install -r ./requirements.txt
RUN geth init genesis.json
RUN geth account import --password ~/.accountpassword  ~/.privatekey

ENV bootnodeId=""
ENV bootnodeIp=""

CMD exec ./sc-start.sh $bootnodeId $bootnodeIp

EXPOSE 8545
EXPOSE 30303
