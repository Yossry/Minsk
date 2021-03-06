=============================================
Carrier configuration with server_environment
=============================================

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fserver--env-lightgray.png?logo=github
    :target: https://github.com/OCA/server-env/tree/12.0/carrier_environment
    :alt: OCA/server-env
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/server-env-12-0/server-env-12-0-carrier_environment
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runbot-Try%20me-875A7B.png
    :target: https://runbot.odoo-community.org/runbot/254/12.0
    :alt: Try me on Runbot

|badge1| |badge2| |badge3| |badge4| |badge5| 

This module allows to configure carrier informations 
using the `server_environment` mechanism: you can then have different 
servers for the production and the test environment.

**Table of contents**

.. contents::
   :local:

Configuration
=============

With this module installed, the delivery carrier are
configured in the `server_environment_files` module (which is a module
you should provide, see the documentation of `server_environment` for
more information).

In the configuration file of each environment, you may first use the
section `[carrier_account]`.

Then for each server, you can define additional values or override the
default values with a section named `[carrier_account.resource_name]` where "resource_name" is the name of the server.

Example of config file ::


  [carrier_account]
  # here is the default format
  file_format = 'ZPL'


  [carrier_account.mycarrier]
  name = mycarrier
  account = 587
  password = 123promenons-nous-dans-les-bois456cueillir-des-saucisses


  [carrier_account.mycarrier2]
  name = mycarrier2
  account = 666
  password = wazaaaaa
  file_format = PDF

Usage
=====

Once configured, Odoo will read the carrier values from the
configuration file related to each environment defined in the main
Odoo file or in carrier.account model.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-env/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-env/issues/new?body=module:%20carrier_environment%0Aversion:%2012.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Akretion
* Camptocamp

Contributors
~~~~~~~~~~~~

* David B??al <david.beal@akretion.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/server-env <https://github.com/OCA/server-env/tree/12.0/carrier_environment>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
