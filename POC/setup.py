import solcx
from solcx import get_solc_version, set_solc_version
#from compile import abi, bytecode
from web3 import Web3
from web3.logs import STRICT, IGNORE, DISCARD, WARN
import random


# If you haven't already installed the Solidity compiler, uncomment the following line
#solcx.install_solc('v0.5.13')

set_solc_version('v0.5.13')

account_from = {
    'private_key': '5e26f39309bcb52d29fe2336e54d64d9d71407dd17a8a8ed42c78e5daf1d67a2',
    'address': '0x082dc6905D5d931Dd6F38Cdb18E396AfC06bD417',
}


# Compile contract
register_file = solcx.compile_files('RegisterSc.sol')
subscription_file = solcx.compile_files('SubscriptionSc.sol')
notary_file = solcx.compile_files('NotarySc.sol')
tracker_file = solcx.compile_files('TrackerSc.sol')
payment_file = solcx.compile_files('PaymentSc.sol')

# Export contract data
abiRegister = register_file['RegisterSc.sol:RegisterSc']['abi']
bytecodeRegister = register_file['RegisterSc.sol:RegisterSc']['bin']

abiSubscription = subscription_file['SubscriptionSc.sol:SubscriptionSc']['abi']
bytecodeSubscription = subscription_file['SubscriptionSc.sol:SubscriptionSc']['bin']

abiNotary = notary_file['NotarySc.sol:NotarySc']['abi']
bytecodeNotary = notary_file['NotarySc.sol:NotarySc']['bin']

abiTracker = tracker_file['TrackerSc.sol:TrackerSc']['abi']
bytecodeTracker = tracker_file['TrackerSc.sol:TrackerSc']['bin']

abiPayment = payment_file['PaymentSc.sol:PaymentSc']['abi']
bytecodePayment = payment_file['PaymentSc.sol:PaymentSc']['bin']


#
# -- Define Provider & Variables --
#
# Provider
#ganache_url = "http://127.0.0.1:8545"
#web3 = Web3(Web3.HTTPProvider(ganache_url))  # Change to correct network


def deploySystemcontracts(_trailchainURL):

    web3 = Web3(Web3.HTTPProvider(_trailchainURL))
    #
    #  -- Deploy TrackerSc Contract --
    #
    tracker = web3.eth.contract(abi=abiTracker, bytecode=bytecodeTracker)

    construct_txn = tracker.constructor().buildTransaction(
    {
        'from': account_from['address'],
        'nonce': web3.eth.getTransactionCount(account_from['address']),
        'chainId': web3.eth.chain_id,
    }
    )

    tx_create = web3.eth.account.signTransaction(construct_txn, account_from['private_key'])
    tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)


    print(f'TrackerSc Contract deployed at address: { tx_receipt.contractAddress }')
    Tracker_address = tx_receipt.contractAddress
    TrackerSc = web3.eth.contract(address=Tracker_address, abi=abiTracker)

    #
    #  -- Deploy NotarySc Contract --
    #
    notary = web3.eth.contract(abi=abiNotary, bytecode=bytecodeNotary)

    construct_txn = notary.constructor().buildTransaction(
    {
        'from': account_from['address'],
        'nonce': web3.eth.getTransactionCount(account_from['address']),
        'chainId': web3.eth.chain_id,
    }
    )

    tx_create = web3.eth.account.signTransaction(construct_txn, account_from['private_key'])
    tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    gasused = tx_receipt.gasUsed


    print(f'NotarySc Contract deployed at address: { tx_receipt.contractAddress }')
    Notary_address = tx_receipt.contractAddress
    NotarySc = web3.eth.contract(address=Notary_address, abi=abiNotary)


    #
    #  -- Update TrackerSc address in NotarySc --
    #
    setAddresTracker_tx = NotarySc.functions.setAddresTracker(Tracker_address).buildTransaction(
    {
        'from': account_from['address'],
        'nonce': web3.eth.getTransactionCount(account_from['address']),
        'chainId': web3.eth.chain_id,
    }
    )
    tx_create = web3.eth.account.signTransaction(setAddresTracker_tx, account_from['private_key'])
    tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    print('Tracker address is updated in NotarySc')

    return Notary_address, abiNotary, Tracker_address, abiTracker, gasused, tx_receipt.gasUsed


def deployPaymentcontracts(_paymentURL):

    #
    #  -- Deploy PaymentSc Contract --
    #

    web3 = Web3(Web3.HTTPProvider(_paymentURL))

    payment = web3.eth.contract(abi=abiPayment, bytecode=bytecodePayment)
    construct_txn = payment.constructor("ERC20", "erc20", 10000000000).buildTransaction(
    {
        'from': account_from['address'],
        'nonce': web3.eth.getTransactionCount(account_from['address']),
        'chainId': web3.eth.chain_id,
    }
    )

    tx_create = web3.eth.account.signTransaction(construct_txn, account_from['private_key'])
    tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)


    print(f'PaymentSc Contract deployed at address: { tx_receipt.contractAddress }')
    Payment_address = tx_receipt.contractAddress
    PaymentSc = web3.eth.contract(address=Payment_address, abi=abiPayment)
    return Payment_address, abiPayment, tx_receipt.gasUsed


def deployApplication1contracts(_applicationURL, _notaryAddress, _marketplaceName):

    
    web3 = Web3(Web3.HTTPProvider(_applicationURL))
    #  -- Deploy RegisterSc Contract --
    #
    arg1 = _marketplaceName
    arg2 = _notaryAddress

    register = web3.eth.contract(abi=abiRegister, bytecode=bytecodeRegister)

    construct_txn = register.constructor(arg1, arg2).buildTransaction(
    {
        'from': account_from['address'],
        'nonce': web3.eth.getTransactionCount(account_from['address']),
        'chainId': web3.eth.chain_id,
    }
    )

    tx_create = web3.eth.account.signTransaction(construct_txn, account_from['private_key'])
    tx_hash = web3.eth.sendRawTransaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)


    print(f'RegisterSc Contract deployed at address: { tx_receipt.contractAddress }')
    register_address = tx_receipt.contractAddress
    RegisterSc = web3.eth.contract(address=register_address, abi=abiRegister)
    return register_address, abiRegister, tx_receipt.gasUsed

