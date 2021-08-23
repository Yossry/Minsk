##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.http import Controller, route, request


class Board(Controller):

    @route('/board/add_to_dashboard_tile', type='json', auth='user')
    def add_to_dashboard_tile(
        self, action_id, domain, view_mode, name, user_id, model_name):
        # Retrieve the 'My Dashboard Title' action from its xmlid
        action = request.env.ref(
            'web_dashboard_tile.action_tree_dashboard_tile')

        # TODO Ask about: action['views'][0][1] == 'form'
        if action and action['res_model'] == 'tile.tile' and action_id:
            # if 'model_id' in vals and not vals['model_id'].isdigit():
            # need to replace model_name with its id
            values = {
                'name': name,
                'user_id': user_id,
                'model_id': request.env['ir.model'].search(
                    [('model', '=', model_name)]).id,
                'domain': domain,
                'action_id': action_id,
            }
            request.env['tile.tile'].create(values)
            return True

        return False
