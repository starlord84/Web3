from web3 import Web3
import time

# initialize Web3 with Arbitrum node address
w3 = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))

# define USDC contract address on Arbitrum network
usdc_contract_address = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'


# define function to get contract instance
def get_contract(abi, contract_address):
    contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)
    return contract


# define function to transfer USDC from one account to another on Arbitrum network
def transfer_usdc_arbitrum_to_arbitrum(arbitrum_usdc_contract_address_from, arbitrum_usdc_contract_address_to, amount):
    # get USDC contract instance
    usdc_contract = get_contract(usdc_abi, usdc_contract_address)

    # get sender's address
    sender_address = arbitrum_usdc_contract_address_from

    # get recipient's address
    recipient_address = arbitrum_usdc_contract_address_to

    # define transfer parameters
    transfer_params = {'from': sender_address, 'to': recipient_address, 'value': amount}

    # send transfer transaction
    try:
        tx_hash = usdc_contract.functions.transfer(**transfer_params).transact({'gas': 100000})
    except:
        print('Failed to send transaction')
        return

    # wait for transaction to be mined
    tx_receipt = None
    while tx_receipt is None:
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        time.sleep(1)

    # check if transaction was successful
    if tx_receipt['status'] != 1:
        print('Transaction failed')
        return
    else:
        print('Transaction successful')
        return tx_receipt


# define USDC contract ABI
usdc_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "recipient",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

'''# example usage
arbitrum_usdc_contract_address_from = '0x123...'
arbitrum_usdc_contract_address_to = '0x456...'
amount = 1000000000000000000 # 1 USDC with 18 decimal places
transfer_usdc_arbitrum_to_arbitrum(arbitrum_usdc_contract_address_from, arbitrum_usdc_contract_address_to, amount)'''
