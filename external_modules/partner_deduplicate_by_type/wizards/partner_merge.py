# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    group_by_type = fields.Boolean('Address Type')

    def _generate_query(self, fields, maximum_group=100):
        """Inject the additional criteria 'type IS NOT NULL' when needed.
        There's no better wasy to do it, as there are no hooks for adding
        this criteria regularly.
        """
        query = super()._generate_query(
            fields, maximum_group=maximum_group)
        if 'type' in fields:
            if 'WHERE' in query:
                index = query.find('WHERE')
                query = (query[:index + 6] + "type = 'invoice' AND " +
                         query[index + 6:])
            else:
                index = query.find(' GROUP BY')
                query = (query[:index] + " WHERE type = 'invoice' NOT NULL" +
                         query[index:])
        return query
