# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2020- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'AF Demodata for base',
    'version': '12.0.1.0',
    'license': 'AGPL-3',
    'description': """
CSV File Creator -- dokumentation
2020-03-20
**/usr/share/odoo-af/base_afdemo/data**

## Länk till dokumentation:
https://www.tutorialspoint.com/makefile/makefile_quick_guide.htm
https://makefiletutorial.com


## Förutsättningar
Namet på filen ska vara TestData_base.xlsx, TestData_[modulnamn].xlsx ,och flikarna ska heta saker i stil med något.bra.namn.csv
Koden skapar csv-filer baserat på namnen av flikarna.
En flik kan heta nåt annat och kommer då inte med som en fil.


## Logga in i Terminalen och knappa in...

## SCRIPT MED FÖRKLARING:
$ make
-- skapar alla .csv-filer baserade på vad flikarna heter.

$ make clean
-- tar bort alla .csv och .tmp filerna.

$ touch TestData_Config.xlsx
-- ändrar "senast ändrad" datum i filen så koden kan köras igen.

$ sudo chmod 777 -R data
-- om det spökar... om koden inte fungerar fast den borde.


## FELHANTERING, KÄNDA
- TestData_base.xlsx = måste heta så. Ändra namnet i koden!
- TestData_[modulnamn].xlsx = måste heta så. Ändra namnet i koden!
- Toma flikar. En flik som heter något.bra.namn.csv får inte vara helt tom.

""",
    'author': ' Vertel AB',
    'website': 'http://vertel.se',
    'category': 'Extra Tools',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    'demo': ['data/res.users.csv', 'data/res.partner.csv'],
    'installable': 'True',
    'application': 'False',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
