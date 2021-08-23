.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=========================
Counting Invoice Interest
=========================

Charge interest in 30 day increments on overdue invoices. Creates a new invoice for the partner
and adds interest charges from all past-due invoices to that invoice.

Installation
============

This module depends on :

* account

Usage
=====

* Create the Interest Product that will be used in the Interest Charge invoice lines.
* Edit your Payment Terms to define Interest charging settings.

The daily cron job will process interest charges on relevant invoices.


Known issues / Roadmap
======================

 * No known issues

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/thinkwelltwd/countinghouse>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.
