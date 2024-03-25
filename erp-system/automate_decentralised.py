from web3 import Web3
from abi import abi
from bytecode import bytecode
from datetime import datetime


web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract = web3.eth.contract(abi=abi, bytecode=bytecode)
account = web3.eth.accounts[0]
response_time = 0
tpm = 0
total_time = 0
gas_spent = 0
total_gas = 0


def deploy_contract():
    global gas_spent
    nonce = web3.eth.get_transaction_count(account)
    transaction = contract.constructor().build_transaction(
        {
            "from": account,
            "nonce": nonce,
            "gas": 2000000,
            "gasPrice": web3.to_wei("50", "gwei"),
        }
    )

    tx_hash = web3.eth.send_transaction(transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    gas_spent += tx_receipt.gasUsed
    contract_address = tx_receipt.contractAddress
    return contract_address


def automate_inventory():
    global response_time
    global tpm
    global total_time
    global gas_spent
    global total_gas
    gas_spent = 0
    start_time = datetime.now()
    contract_address = deploy_contract()
    contract_instance = web3.eth.contract(address=contract_address, abi=abi)

    products = [
        {
            "name": "Chocolate Bar",
            "description": "CADBURY X7B6K3A",
            "suffixCode": "ABC",
        },
        {
            "name": "Chocolate Bar",
            "description": "CADBURY Q4M8Z2S",
            "suffixCode": "DEF",
        },
        {
            "name": "Chocolate Bar",
            "description": "CADBURY L8P5R3D",
            "suffixCode": "GHI",
        },
        {
            "name": "Chocolate Bar",
            "description": "CADBURY W5E2F7H",
            "suffixCode": "JKL",
        },
        {
            "name": "Chocolate Bar",
            "description": "CADBURY U9G1K4E",
            "suffixCode": "MNO",
        },
    ]

    for product in products:
        now = datetime.now()
        tx_hash = contract_instance.functions.insertProduct(
            product["name"], product["description"], product["suffixCode"]
        ).transact({"from": account})
        receipt= web3.eth.wait_for_transaction_receipt(tx_hash)
        gas_spent += receipt.gasUsed
        later = datetime.now()
        response_time = (later - now).total_seconds() * 1000
        print(f"Product {product['name']} added successfully.")

    party_data = [
        {
            "name": "John Doe",
        }
    ]

    for party in party_data:
        tx_hash = contract_instance.functions.insertParty(party["name"]).transact(
            {"from": account}
        )
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        gas_spent += receipt.gasUsed
        print(f"Party {party['name']} added successfully.")

    currencies_to_setup = [
        {
            "name": "Euro",
            "code": "EUR",
            "digits": 2,
            "rounding": 100,
            "symbol": "€",
            "numeric_code": 978,
        },
        {
            "name": "US Dollar",
            "code": "USD",
            "digits": 2,
            "rounding": 100,
            "symbol": "$",
            "numeric_code": 840,
        },
        {
            "name": "British Pound",
            "code": "GBP",
            "digits": 2,
            "rounding": 100,
            "symbol": "£",
            "numeric_code": 826,
        },
        {
            "name": "Japanese Yen",
            "code": "JPY",
            "digits": 0,
            "rounding": 100,
            "symbol": "¥",
            "numeric_code": 392,
        },
        {
            "name": "Swiss Franc",
            "code": "CHF",
            "digits": 2,
            "rounding": 5,
            "symbol": "CHF",
            "numeric_code": 756,
        },
        {
            "name": "Canadian Dollar",
            "code": "CAD",
            "digits": 2,
            "rounding": 1,
            "symbol": "C$",
            "numeric_code": 124,
        },
        {
            "name": "Australian Dollar",
            "code": "AUD",
            "digits": 2,
            "rounding": 1,
            "symbol": "A$",
            "numeric_code": 36,
        },
        {
            "name": "Chinese Yuan",
            "code": "CNY",
            "digits": 2,
            "rounding": 1,
            "symbol": "¥",
            "numeric_code": 156,
        },
        {
            "name": "Indian Rupee",
            "code": "INR",
            "digits": 2,
            "rounding": 1,
            "symbol": "₹",
            "numeric_code": 356,
        },
    ]

    for currency in currencies_to_setup:
        tx_hash = contract_instance.functions.insertCurrency(
            currency["name"],
            currency["code"],
            currency["digits"],
            currency["rounding"],
            currency["symbol"],
            currency["numeric_code"],
        ).transact({"from": account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        gas_spent += receipt.gasUsed
        print(f"Currency {currency['name']} added successfully.")

    companies_data = [
        {
            "party": "John Doe",
            "currency": "USD",
        }
    ]

    for company in companies_data:
        tx_hash = contract_instance.functions.insertCompany(
            company["party"], company["currency"]
        ).transact({"from": account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        gas_spent += receipt.gasUsed
        print(f"Company {company['party']} added successfully.")

    countries_data = [
        {
            "name": "United States",
            "code": "US",
            "code3": "USA",
            "code_numeric": 840,
            "region": "",
            "active": True,
        },
        {
            "name": "Germany",
            "code": "DE",
            "code3": "DEU",
            "code_numeric": 276,
            "region": "",
            "active": True,
        },
        {
            "name": "Japan",
            "code": "JP",
            "code3": "JPN",
            "code_numeric": 392,
            "region": "",
            "active": True,
        },
    ]

    for country in countries_data:
        tx_hash = contract_instance.functions.insertCountry(
            country["name"], country["code"], country["code3"], country["code_numeric"]
        ).transact({"from": account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        gas_spent += receipt.gasUsed
        print(f"Country {country['name']} added successfully.")
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    tpm = 60 * 20 / total_time
    total_gas = gas_spent


def get_response_time():
    global response_time
    return response_time

def get_tpm():
    global tpm
    return tpm

def get_total_time():
    global total_time
    return total_time

def get_gas_spent():
    global total_gas
    return total_gas

