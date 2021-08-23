.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===========
Project Bid
===========

A Project Bid represents the process in Odoo by which a company can prepare
an estimate of the planned costs and revenues that a future project may
undertake.

The bid is often created as a response to a solicitation by a customer.
In project management, the bid specifications provided by customer will
often be presented in the form of a Statement of Work (SOW), identifying
the project need and product scope description. Other times the customer may
provide more detailed requirements, including a decomposition of deliverables
or work packages that needs to be covered.

Profit & Loss Statement
-----------------------

Managing Projects is analogous to managing companies.
The Project Bid presents the results in the format of a
Profit & Loss Statement (also called Income Statement). The P&L is the most
important measure of the company (and analogously to the project’s) health
and sustainability.

The statement is presented as follows:


Revenue - Cost of Sales = Gross Profit = Gross Margin (%)

Gross Profit - Total Overhead = Net Profit Margin = Net Profit Margin (%)

** Revenue represents ** the income that you plan to receive from the
customer out of the project. It is obtained in the Bid application as a
% of Cost of Goods Sales. The user can specify the % in the Bid Template,
so that the same % can be used across multiple Bids.

** Cost of Sales (COGS) ** represents the costs that are directly
attributable to the delivering project. These are often called direct costs
to the project. The bidder enters the Cost of Sales in the sections
“Components”, “Other Labor” and “Other expenses”.

** Gross Profit ** is Revenue - Cost of Sales, and indicates what’s left from
revenue after we deduct the costs that are directly related to deliver
the project. The project manager is accountable for this key figure,
since he is in full control it’s elements.

** Gross Margin (%) ** is (Revenue - Cost of Sales) / Cost of Sales, and is
very important because it allows to compare profitability across projects.
Project managers are often enforced to achieve a target Gross Margin
consistently across their projects. It is often considered a key go/no go
criteria for a project. In projectized organizations, the company gross margin
is composed by the individual gross margins of the individual projects.
A company willing to achieve an overall gross margin of 40% would easily drop
a project with 5% gross margin, because it would drag the target profitability
of the overall company.

** Total Overhead ** represents the costs that are not directly attributable
 to the project. These are generally costs associated to running the overall
 company (electricity for the building, administration or general management
 labor expenses,...). In the Bid application the Total Overhead is estimated
 as a % of Cost of Sales. The user can specify the % in the Bid Template,
 so that the same % can be used across multiple Bids.

Components
----------
The Bid application allows the user to decompose the customer specifications
into Components, identifying for each, a description of the scope of work,
and estimates of materials and labor required to complete the Component.

Bidders are able to take advantage of Components that were used in other
Bids by choosing them in the “Project Bid Component Template”.
The data from the other Bid’s Component will then be copied to the
new Bid Component.

Each Labor, Material entered provides details of its contribution to the
overall Income Statement, indicating planned Revenue, COGS, Gross Margin,
Overhead,  Net Margin.

Other Labor
-----------
This section allows the user to enter labor cost not directly related
to specific Components. E.g. Cost of the project manager.

Other Expenses
--------------
This section allows the user to enter other costs not directly related to
specific Components. E.g. Flights.


Configuration
=============

If your company is required to generate a balanced balance sheet by
Operating Unit you can specify at company level that Operating Units should
be self-balanced, and then indicate a self-balancing clearing account.

* Create an account for "Inter-OU Clearing" of type Regular.

* Go to *Settings / Companies / Companies* and Set the "Operating Units are
  self-balanced" checkbox.

  Then Set the "Inter-OU Clearing"  account in "Inter-Operating Unit
  clearing account" field.

* Assign Operating Unit in Accounts.


Usage
=====

* Add users to the groups 'Project Bid / User' or 'Project Bid / Manager'
* Go to 'Project / Configuration / Project Bid Templates' and define standard
  parameters that will be used across multiple bids.
* Go to 'Project / Project Bid' to create new Bids.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Aarón Henríquez <ahenriquez@eficent.com>

Maintainer
----------

This module is maintained by Eficent.
