# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import content_disposition, request

import base64
import io


class DownloadXMLMasterData(http.Controller):

    '''
        Download link for files stored as binary fields.

        :param str filename: name of the file to download
        :param str xml_string: xml file as string
    '''
    @http.route('/web/binary/download_data', type='http', auth="public")
    def download_xml_master_data(self, filename, model_id, **kwargs):
        master_data_obj = request.env['import.master.data'].sudo().search_read(
            [('id', '=', int(model_id))], ["xml_file"])
        if master_data_obj:
            master_data_obj = master_data_obj[0]

        xml_data = io.BytesIO(
            base64.standard_b64decode(master_data_obj["xml_file"]))
        return request.make_response(xml_data, headers=[
            ('Content-Disposition', content_disposition(filename))
        ])
