from proteus import config, Model
from decimal import Decimal


def setup_parties(parties):
    Party = Model.get("party.party")

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
        party.save()

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
        currency.save()

        print(f"Currency {currency.name} processed successfully with ID {currency.id}")


def setup_companies(companies):
    Company = Model.get("company.company")
    Currency = Model.get("currency.currency")
    Party = Model.get("party.party")

    for company_data in companies:
        companies = Company.find([("party.name", "=", company_data["party"])])
        currencies = Currency.find([("code", "=", company_data["currency"])])
        parties = Party.find([("name", "=", company_data["party"])])

        if companies:
            company = companies[0]
            print(f"Updating company: {company_data['party']}")
        else:
            company = Company()
            print(f"Creating new company: {company_data['party']}")

        companies_data[0]["currency"] = currencies[0]
        companies_data[0]["party"] = parties[0]
        for attr, value in company_data.items():
            setattr(company, attr, value)

        company.save()

        print(f"Company {company.party.name} processed successfully with ID {company.id}")


def setup_countries(contries_data):
    Country = Model.get("country.country")
    for country_data in countries_data:
        # Check if the country already exists
        country_exists = Country.find([("code", "=", country_data["code"])])

        if country_exists:
            print(f"Country {country_data['name']} already exists.")
            continue

        country = Country(**country_data)
        country.save()
        print(f"Added country: {country_data['name']}")


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

config.set_trytond(database="trytonnew", config_file="trytond.conf")
setup_parties(party_data)
setup_currencies(currencies_to_setup)
setup_companies(companies_data)
setup_countries(countries_data)
