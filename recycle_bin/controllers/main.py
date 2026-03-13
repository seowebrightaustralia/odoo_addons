# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime


class Screenshot(http.Controller):

    @http.route('/unlink-screenshot', type='json', auth="public")
    def save_screenshot(self, image, model, records):
        if request.env.company.trash_screenshot:
            name = datetime.strftime(datetime.now(), "%Y-%m-%d %H-%M-%S") + '.png'
            recycle_obj = request.env['recycle.bin'].sudo()
            for record in records:
                recycle_bin = recycle_obj.search([
                    ('model_name', '=', model),
                    ('record_id', '=', record)
                ])
                recycle_bin.write({
                    'screenshot': image,
                    'screenshot_name': name
                })
