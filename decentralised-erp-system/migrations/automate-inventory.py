from web3 import Web3
from decimal import Decimal
import json

with open('contract_abi.json', 'r') as f:
    contract_abi = json.load(f)

web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))


def setup_parties(parties):

    for party_data in parties:
        parties = Party.find([("name", "=", party_data["name"])])

        if parties:
            party = parties[0]
            print(f"Updating party: {party_data['name']}")
        else:
            party = Party()
            print(f"Creating new party: {party_data['name']}")

        for attr, value in party_data.items():
            setattr(party, attr, value)

        party.active = True

        try:
            start_time = time.time()
            party.save()
            end_time = time.time()
            duration = end_time - start_time
            insert_data_into_table(True, duration)
        except Exception as e:
            print(f"Error saving party: {e}")
            insert_data_into_table(False, 0)
            continue

        print(f"Party {party.name} processed successfully with ID {party.id}")


def setup_currencies(currency_list):
    Currency = Model.get("currency.currency")

    for currency_data in currency_list:
        # Ensure rounding is a Decimal
        if "rounding" in currency_data:
            currency_data["rounding"] = currency_data["rounding"]

        currencies = Currency.find([("code", "=", currency_data["code"])])

        if currencies:
            currency = currencies[0]
            print(f"Updating currency: {currency_data['code']}")
        else:
            currency = Currency()
            print(f"Creating new currency: {currency_data['code']}")

        for attr, value in currency_data.items():
            setattr(currency, attr, value)

        currency.active = True
        try:
            start_time = time.time()
            currency.save()
            end_time = time.time()
            duration = end_time - start_time
            insert_data_into_table(True, duration)
        except Exception as e:
            print(f"Error saving party: {e}")
            insert_data_into_table(False, 0)
            continue
        

        print(f"Currency {currency.name} processed successfully with ID {currency.id}")


def setup_companies(companies):
    Company = Model.get("company.company")
    Currency = Model.get("currency.currency")
    Party = Model.get("party.party")

    for company_data in companies:
        print(company_data)
        companies = Company.find([("party.name", "=", company_data["party"])])
        currencies = Currency.find([("code", "=", company_data["currency"])])
        parties = Party.find([("name", "=", company_data["party"])])

        if companies:
            company = companies[0]
            print(f"Updating company: {company_data['party']}")
        else:
            company = Company()
            print(f"Creating new company: {company_data['party']}")

        company.party = parties[0]
        company.currency = currencies[0]
        try:
            start_time = time.time()
            company.save()
            end_time = time.time()
            duration = end_time - start_time
            insert_data_into_table(True, duration)
        except Exception as e:
            print(f"Error saving party: {e}")
            insert_data_into_table(False, 0)
            continue

        print(
            f"Company {company.party.name} processed successfully with ID {company.id}"
        )


def setup_countries(contries_data):
    Country = Model.get("country.country")
    for country_data in countries_data:
        # Check if the country already exists
        country_exists = Country.find([("code", "=", country_data["code"])])

        if country_exists:
            print(f"Country {country_data['name']} already exists.")
            continue

        country = Country(**country_data)
        try:
            start_time = time.time()
            country.save()
            end_time = time.time()
            duration = end_time - start_time
            insert_data_into_table(True, duration)
        except Exception as e:
            print(f"Error saving party: {e}")
            insert_data_into_table(False, 0)
            continue
       
        print(f"Added country: {country_data['name']}")


def setup_product_uom_categories():
    UomCategory = Model.get("product.uom.category")
    name = "Area"

    uom_categories = UomCategory.find([("name", "=", name)])
    if uom_categories:
        print("UOM categories already exist.")
        return

    uom_category = UomCategory(name=name)
    try:
        start_time = time.time()
        uom_category.save()
        end_time = time.time()
        duration = end_time - start_time
        insert_data_into_table(True, duration)
    except Exception as e:
        print(f"Error saving party: {e}")
        insert_data_into_table(False, 0)
    
    print("Added UOM category: Area")


def setup_product_template():
    ProductTemplate = Model.get("product.template")
    name = "Chocolate Bar"
    type = "goods"
    product_template = ProductTemplate.find([("name", "=", name)])

    if product_template:
        print("Product template already exists.")
        return

    ProductUOM = Model.get("product.uom")
    uom = ProductUOM.find([("name", "=", "Kilogram")])[0]
    product_template = ProductTemplate()
    product_template.name = name
    product_template.type = type
    product_template.default_uom = uom
    product_template.consumable = True
    product_template.active = True
    try:
        start_time = time.time()
        product_template.save()
        end_time = time.time()
        duration = end_time - start_time
        insert_data_into_table(True, duration)
    except Exception as e:
        print(f"Error saving party: {e}")
        insert_data_into_table(False, 0)
    
    print("Added product template: Chocolate Bar")


def setup_products(products):
    Product = Model.get("product.product")
    ProductTemplate = Model.get("product.template")

    for product_data in products:
        product = Product.find([("suffix_code", "=", product_data["suffix_code"])])
        product_template = ProductTemplate.find([("name", "=", product_data["name"])])[
            0
        ]
        if product:
            print(f"Product {product_data['name']} already exists.")
            continue
        else:
            product = Product()
            print(f"Creating new product: {product_data['suffix_code']}")
            product.template = product_template
            product.description = product_data["description"]
            product.suffix_code = product_data["suffix_code"]
            product.active = True
        
        try:
            start_time = time.time()
            product.save()
            end_time = time.time()
            duration = end_time - start_time
            insert_data_into_table(True, duration)
        except Exception as e:
            print(f"Error saving party: {e}")
            insert_data_into_table(False, 0)
            continue

        print(
            f"Product {product.suffix_code} processed successfully with ID {product.id}"
        )




party_data = [
    {
        "name": "John Doe",
    }
]

currencies_to_setup = [
    {
        "name": "Euro",
        "code": "EUR",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "€",
        "numeric_code": "978",
    },
    {
        "name": "US Dollar",
        "code": "USD",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "$",
        "numeric_code": "840",
    },
    {
        "name": "British Pound",
        "code": "GBP",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "£",
        "numeric_code": "826",
    },
    {
        "name": "Japanese Yen",
        "code": "JPY",
        "digits": 0,
        "rounding": Decimal("1"),
        "symbol": "¥",
        "numeric_code": "392",
    },
    {
        "name": "Swiss Franc",
        "code": "CHF",
        "digits": 2,
        "rounding": Decimal("0.05"),
        "symbol": "CHF",
        "numeric_code": "756",
    },
    {
        "name": "Canadian Dollar",
        "code": "CAD",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "C$",
        "numeric_code": "124",
    },
    {
        "name": "Australian Dollar",
        "code": "AUD",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "A$",
        "numeric_code": "036",
    },
    {
        "name": "Chinese Yuan",
        "code": "CNY",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "¥",
        "numeric_code": "156",
    },
    {
        "name": "Indian Rupee",
        "code": "INR",
        "digits": 2,
        "rounding": Decimal("0.01"),
        "symbol": "₹",
        "numeric_code": "356",
    },
]

companies_data = [
    {
        "party": "John Doe",
        "currency": "USD",
    }
]

countries_data = [
    {
        "name": "United States",
        "code": "US",
        "code3": "USA",
        "code_numeric": "840",
        "region": None,
        "active": True,
    },
    {
        "name": "Germany",
        "code": "DE",
        "code3": "DEU",
        "code_numeric": "276",
        "region": None,
        "active": True,
    },
    {
        "name": "Japan",
        "code": "JP",
        "code3": "JPN",
        "code_numeric": "392",
        "region": None,
        "active": True,
    },
]

products = [
    {"name": "Chocolate Bar", "description": "CADBURY X7B6K3A", "suffix_code": "ABC"},
    {"name": "Chocolate Bar", "description": "CADBURY Q4M8Z2S", "suffix_code": "DEF"},
    {"name": "Chocolate Bar", "description": "CADBURY L8P5R3D", "suffix_code": "GHI"},
    {"name": "Chocolate Bar", "description": "CADBURY W5E2F7H", "suffix_code": "JKL"},
    {"name": "Chocolate Bar", "description": "CADBURY U9G1K4E", "suffix_code": "MNO"},
]


def setup_all():
    """
    Function to setup parties, currencies, companies, countries, product uom categories, product templates, and products.
    """
    while True:
        try:
            setup_parties(party_data)
            setup_currencies(currencies_to_setup)
            setup_companies(companies_data)
            setup_countries(countries_data)
            setup_product_uom_categories()
            setup_product_template()
            setup_products(products)
        except Exception as e:
            print(f"Error setting up data: {e}")
            continue


setup_all()
