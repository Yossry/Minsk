# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def anonymise_emails(record_id, fields):
    return ', '.join(
        map(lambda field:
            "%s=case when %s is null or %s='' then %s "
            "else '%s%s-anonymise@anonymise.fr' end" % (
                field.replace("'", ''), field.replace(
                    "'", ''), field.replace("'", ''), field.replace("'", ''),
                field.replace("'", ''), record_id), fields))


def anonymise_phones(fields):
    return ', '.join(
        map(lambda field:
            "%s=case when %s is null or %s='' then %s "
            "else '+33000000000' end" % (
                field.replace("'", ''), field.replace("'", ''),
                field.replace("'", ''), field.replace("'", '')), fields))


def anonymise_fields(record_id, fields):
    return ', '.join(
        map(lambda field: "%s=case when %s is null or %s='' then %s "
            "else '%s%s-anonym' end" % (
                field.replace("'", ''), field.replace(
                    "'", ''), field.replace("'", ''), field.replace("'", ''),
                field.replace("'", '')[:7], record_id), fields))


def is_anonymised_fields(fields):
    return ', '.join(
        map(lambda field: "%s=True" % field.replace("'", ''), fields))


def anonymise_object(
        self, table, record_id, fields_list=None,
        phones_list=None, email_list=None):
    anonymised_vals = ''
    if fields_list:
        anonymised_vals = anonymise_fields(record_id, fields_list)
    if phones_list:
        anonymised_vals = anonymised_vals and '%s, %s' % (
            anonymised_vals, anonymise_phones(phones_list)
        ) or anonymise_phones(phones_list)
    if email_list:
        anonymised_vals = anonymised_vals and '%s, %s' % (
            anonymised_vals, anonymise_emails(record_id, email_list)
        ) or anonymise_emails(record_id, email_list)
    query = 'update {table} set {values} where id = {record_id}'.format(
        table=table, values=anonymised_vals, record_id=record_id)
    self._cr.execute(query)
    return
