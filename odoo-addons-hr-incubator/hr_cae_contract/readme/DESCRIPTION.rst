Extends `hr.contract` to handle employee contracts in a CAE - Cooperative Activité Emploi

* Introduces two echelons of contract types: main contracts (CDI, CDD, ...) and amendments (Bonus, Salary Evolution, ...).
* A button is added to create an amendment of a contract. It's information, or that of it's latest amendment, is copied into a new amendment.
* Amendments of a main contract are indexed.
* Creation of amendments can be limited by type of amendment to a certain number
* Fields are added to contracts regarding duration and dates (signature, mailing, ...).
* The monthly wage is computed based on monthly working hours and hourly wage.
* Contract attachements can be uploaded
