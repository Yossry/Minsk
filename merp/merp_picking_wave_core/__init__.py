# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from . import models

def post_init(cr, registry):
    cr.execute('UPDATE stock_picking SET first_proc_picking = id WHERE group_id IS NULL')
    cr.execute('''UPDATE stock_picking AS sp
        SET first_proc_picking = sp3.id
        FROM (
            SELECT MIN(sp2.id) AS id, sp2.group_id
            FROM stock_picking AS sp2
            WHERE sp2.group_id IS NOT NULL
            GROUP BY sp2.group_id
        ) sp3
        WHERE sp.group_id IS NOT NULL AND sp.group_id = sp3.group_id''')

    cr.execute('''UPDATE stock_picking AS sp
        SET wave_location_id = spb.location_id
        FROM stock_picking sp2
        INNER JOIN stock_picking_batch spb ON spb.id = sp2.batch_id
        WHERE sp2.id = sp.first_proc_picking''')
