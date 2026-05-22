# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GlobalSearchController(http.Controller):

    @http.route(
        '/web/global_search/search',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,
    )
    def search(self, query='', limit=10, **kwargs):
        try:
            return request.env['webright.global.search'].search_records(
                query, int(limit)
            )
        except Exception:
            _logger.exception('webright_global_search: controller error')
            return []
