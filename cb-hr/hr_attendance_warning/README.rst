=====================
Hr Attendance Warning
=====================

This module allows you to get warnings when there are
inconsistencies between the theoric check in time of an employee
and what has happened.

Every time there is a check_in or a check_out the module checks whether
it is inside the employee's working time or not and creates a warning if it's
not.

It also testes the opposite case, an employee not coming to work at expected
time. A cron is executed every 5 minutes checking resource.calendar.attendances
and checks if every employee related to it has done what it was expected.

The module also adds a systray icon to receive notifications about warnings,
which can be disabled by setting show_attendance_warning system parameter to
false.

**Table of contents**

.. contents::
   :local:

Usage
=====

Two new columns are added to resource.calendar.attendances, margin_from and
margin_to. This two fields indicate the margin an employee has to check in
and check out. If an employee enters at 9:00 with a margin of 30 minutes,
it is expected to enter between 8:30 and 9:30, otherwise a warning will be
generated.

Different warnings created to a single employee the same day are stacked as
lines in a hr.attendance.warning object. From there you can check employee's
attendances to check the reason of the warning and correct the issues.

After that, click on the Solve button to mark the warning as resolved.

Credits
=======

Authors
~~~~~~~

* Creu Blanca

Contributors
~~~~~~~~~~~~

* Jaime Arroyo <jaime.arroyo@creublanca.es>
* Enric Tobella <etobella@creublanca.es>
