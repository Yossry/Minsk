# -*- coding: utf-8 -*-

import subprocess
import logging

from odoo import http
from odoo.addons.hw_screen.controllers import main as homepage

_logger = logging.getLogger(__name__)


class HardwareScreenCups(homepage.HardwareScreen):

    def _get_html(self):
        res = super(HardwareScreenCups, self)._get_html()
        res = res.replace('Odoo Point of Sale', 'Odoo Point of Sale <em>with Hibou ShipBox</em>')

        process = subprocess.Popen('lpstat -p'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        pre = '<pre>' + (error.replace("\n", '<br/>') if error else output.replace("\n", '<br/>')) + '</pre>'
        res = res.replace('<h3>My IPs</h3>', '<h3>My Printers</h3>' + pre + '<h3>My IPs</h3>')

        return res
