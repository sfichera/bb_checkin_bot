import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
import time
from eth_abi import decode_single
from eth_account import Account
import logging

# Logger config
logging.basicConfig(
    filename='bb_checkin_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# CHAIN RPC & SMARTCONTRACT Config
chain_rpc='https://mainnet.base.org'
#contract_address='0xE842537260634175891925F058498F9099C102eB'
contract_address='0xcf77e83f9745429d2722641f07edb2fbc96de240'
contract_abi = '''[{"inputs":[{"internalType":"address","name":"_collection","type":"address"},{"internalType":"address","name":"_initialOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"EnforcedPause","type":"error"},{"inputs":[],"name":"ExpectedPause","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"CheckIn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"name":"ban","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"banned","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"name":"canCheckIn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"checkIn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"checkIns","outputs":[{"internalType":"uint256","name":"lastCheckIn","type":"uint256"},{"internalType":"uint16","name":"streak","type":"uint16"},{"internalType":"uint16","name":"count","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"collection","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"name":"isBanned","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"name":"unban","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newCollection","type":"address"}],"name":"updateCollection","outputs":[],"stateMutability":"nonpayable","type":"function"}]'''

# Your Wallet PK. Please keep in mind:
# 1. Never ever share your PK to anyone, unless you want to get drained.
# 2. Needs to holds BB NFT. (You can get one at: https://opensea.io/collection/based-bits)
# 3. Needs to have some ETH to cover gas fees.
PK = "<YOUR WALLET PK>" 

print(f"Starting BB Checkin Bot. Contract Addy [{contract_address}]")

logline = f"Starting BB Checkin Bot. Contract Addy [{contract_address}]"
logging.info(logline)

# Creating Web3 connection
w3 = Web3(Web3.HTTPProvider(chain_rpc))
if w3.isConnected():
    logline = f"Connected to the blockchain"
    logging.info(logline)
else:
    logline = f"Can't connect to the blockchain"
    logging.error(logline)
    exit(0)

contract_obj = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=contract_abi)
chain_id = w3.eth.chain_id
WALLET = Account.from_key(PK)

def checkIn():

    WALLET_NONCE = w3.eth.getTransactionCount(WALLET.address)

    data = contract_obj.encodeABI(fn_name="checkIn", args=[])

    transaction = {
        "from": WALLET.address,
        "to": Web3.toChecksumAddress(contract_address),
        "data": data
    }

    gas_estimate = w3.eth.estimateGas(transaction)
    print(f"Creating Checkin Txn... Address, {WALLET.address}")
    logline = f"Creating Checkin Txn... Address, {WALLET.address}"
    logging.info(logline)

    transaction = {
        "nonce": WALLET_NONCE,
        "gasPrice": (w3.eth.gas_price),
        "gas": gas_estimate,
        "to": Web3.toChecksumAddress(contract_address),
        "data": data,
        "chainId": chain_id
    }

    signed_txn = w3.eth.account.signTransaction(transaction, PK)

    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_hash_str = w3.toHex(tx_hash)
    print(f"Checkin Done Hash: [{tx_hash_str}]")
    logline = f"Checkin Done, {tx_hash_str}, {WALLET.address}, {WALLET_NONCE}"
    logging.info(logline)
    WALLET_NONCE = WALLET_NONCE + 1


# Main Loop... Will hopefully running forever ;-)
while True:
    try:
        current_block = w3.eth.block_number
        print(f"Triggering a CheckIn Txn. Current block: [{current_block}]")
        checkIn()
        print(f"Sleeping for: [{(60*60*24) + 60}] seconds...")
        time.sleep((60*60*24) + 60) # adjust sleeping time here if needed...
    except Exception as e:
        print(f"Error in main loop: {e}")
        print("Restarting in 60 secs...")
        time.sleep(60)
        continue
