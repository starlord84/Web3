import time
from web3 import Web3, HTTPProvider
from eth_account import Account
import json

'''Функция load_contract_abi загружает ABI (Application Binary Interface) для USDC контракта на указанной сети'''


def load_contract_abi(chain: str) -> dict:
    """
    Load the ABI for the USDC contract on the specified chain.
    """
    if chain == "arbitrum":
        # Load ABI for Arbitrum USDC contract
        with open("arbitrum_usdc_abi.json") as f:
            contract_abi = json.load(f)
    else:
        raise ValueError(f"Invalid chain: {chain}")

    return contract_abi


'''Функция connect_web3 устанавливает соединение с Web3-провайдером, используя переданный в неё URL-адрес. 
Она возвращает экземпляр класса Web3, который можно использовать для взаимодействия с блокчейном через этот провайдер.'''


def connect_web3(url: str) -> Web3:
    """
    Connect to a Web3 instance using the specified URL.
    """
    return Web3(HTTPProvider(url))


'''Функция get_contract создает экземпляр контракта из предоставленного Web3-экземпляра, адреса контракта и его ABI (interface)'''


def get_contract(web3: Web3, contract_address: str, contract_abi: dict):
    """
    Load a contract from the specified web3 instance using the specified address and ABI.
    """
    return web3.eth.contract(address=contract_address, abi=contract_abi)


# Connect to the Arbitrum network
arbitrum_url = 'https://arb1.arbitrum.io/rpc'
arbitrum_web3 = connect_web3(arbitrum_url)
# ToDo Вставить адрес откуда будет трансфер
arbitrum_usdc_contract_address_from = '...'
arbitrum_usdc_contract_abi = load_contract_abi("arbitrum")
arbitrum_usdc_contract = get_contract(arbitrum_web3, arbitrum_usdc_contract_address_from, arbitrum_usdc_contract_abi)
# ToDo Вставить адрес куда прийдет трансфер
arbitrum_usdc_contract_address_to = '...'

'''Функция transfer_usdc_arbitrum_to_arbitrum добавляет проверку баланса аккаунта, чтобы убедиться, что на аккаунте достаточно USDC для перевода.
 Также она ожидает, пока транзакция не будет добыта, а затем проверяет, что баланс USDC на целевом адресе
  оптимизма действительно увеличился на сумму перевода.'''


def transfer_usdc_arbitrum_to_arbitrum(amount: int, private_key: str):
    # Set up account for the transaction
    account = Account.from_key(private_key)

    # Get the current USDC balance on Arbitrum
    current_balance = arbitrum_usdc_contract.functions.balanceOf(account.address).call()

    # Ensure that the account has enough USDC to transfer
    if current_balance < amount:
        raise ValueError("Account does not have enough USDC to transfer")

    # Estimate the gas required for the transaction
    gas_limit = arbitrum_usdc_contract.functions.transfer(arbitrum_usdc_contract_address_to, amount).estimateGas()
    gas_price = arbitrum_web3.eth.gas_price

    # Build the transaction to transfer USDC from Arbitrum to Optimism
    transaction = {
        'from': account.address,
        'to': arbitrum_usdc_contract_address_from,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': arbitrum_web3.eth.get_transaction_count(account.address),
        'data': arbitrum_usdc_contract.functions.transfer(arbitrum_usdc_contract_address_to, amount).buildTransaction(
            {'gas': gas_limit})
    }

    # Sign the transaction with the account private key
    signed_transaction = account.sign_transaction(transaction)

    # Send the signed transaction to the Arbitrum network
    tx_hash = arbitrum_web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    receipt = None
    while receipt is None:
        receipt = arbitrum_web3.eth.getTransactionReceipt(tx_hash)
        time.sleep(1)

    # Get the transaction hash for the receipt
    tx_hash = receipt['transactionHash']

    # Get the current USDC balance on Optimism
    current_balance = arbitrum_usdc_contract_address_to.functions.balanceOf(account.address).call()

    # Ensure that the transfer was successful
    if current_balance != amount:
        raise ValueError("Transfer was not successful")

    print(f"Transferred {amount} USDC from Arbitrum to Arbitrum with transaction hash {tx_hash}")
