// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataStorage {
    struct Party {
        string name;
        bool active;
    }
    
    struct Currency {
        string name;
        string code;
        uint8 digits;
        uint256 rounding; // Represented in the smallest unit (e.g., cents for USD)
        string symbol;
        uint256 numericCode;
        bool active;
    }
    
    struct Company {
        string partyName;
        string currencyCode;
        bool active;
    }
    
    struct Country {
        string name;
        string code;
        string code3;
        uint256 codeNumeric;
        bool active;
    }
    
    struct Product {
        string name;
        string description;
        string suffixCode;
        bool active;
    }
    
    Party[] public parties;
    Currency[] public currencies;
    Company[] public companies;
    Country[] public countries;
    Product[] public products;
    
    // Function to insert party data
    function insertParty(string memory _name) external {
        parties.push(Party(_name, true));
    }
    
    // Function to insert currency data
    function insertCurrency(
        string memory _name,
        string memory _code,
        uint8 _digits,
        uint256 _rounding,
        string memory _symbol,
        uint256 _numericCode
    ) external {
        currencies.push(Currency(_name, _code, _digits, _rounding, _symbol, _numericCode, true));
    }
    
    // Function to insert company data
    function insertCompany(string memory _partyName, string memory _currencyCode) external {
        companies.push(Company(_partyName, _currencyCode, true));
    }
    
    // Function to insert country data
    function insertCountry(
        string memory _name,
        string memory _code,
        string memory _code3,
        uint256 _codeNumeric
    ) external {
        countries.push(Country(_name, _code, _code3, _codeNumeric, true));
    }
    
    // Function to insert product data
    function insertProduct(
        string memory _name,
        string memory _description,
        string memory _suffixCode
    ) external {
        products.push(Product(_name, _description, _suffixCode, true));
    }
}
