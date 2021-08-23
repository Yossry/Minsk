from odoo.http import request, route, Controller


class BannerController(Controller):
    @route('/plant/credit_status', type='json', auth='user')
    def credit_status(self):
        credit = request.env['iap.account'].get_credits('plant_id')
        credit_url = request.env['iap.account'].get_credits_url('plant_id')
        return {
            'html': request.env['ir.ui.view'].render_template('plant_identification.credit_banner', {'credit': credit, 'credit_url': credit_url})
        }