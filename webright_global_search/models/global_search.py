# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models

_logger = logging.getLogger(__name__)

_SEARCH_CONFIG = [
    {
        'model': 'res.partner',
        'label': 'Contact',
        'domain': [('active', '=', True)],
        'extra_fields': ['email', 'phone', 'ref', 'vat'],
    },
    {
        'model': 'sale.order',
        'label': 'Sale Order',
        'domain': [],
        'extra_fields': ['client_order_ref'],
    },
    {
        'model': 'purchase.order',
        'label': 'Purchase Order',
        'domain': [],
        'extra_fields': ['partner_ref'],
    },
    {
        'model': 'account.move',
        'label': 'Invoice',
        'domain': [('move_type', 'in', [
            'out_invoice', 'in_invoice', 'out_refund', 'in_refund',
        ])],
        'extra_fields': ['ref', 'invoice_origin'],
    },
    {
        'model': 'project.project',
        'label': 'Project',
        'domain': [('active', '=', True)],
        'extra_fields': [],
    },
    {
        'model': 'project.task',
        'label': 'Task',
        'domain': [],
        'extra_fields': [],
    },
    {
        'model': 'product.template',
        'label': 'Product',
        'domain': [('active', '=', True)],
        'extra_fields': ['default_code', 'barcode'],
    },
    {
        'model': 'stock.picking',
        'label': 'Delivery',
        'domain': [('state', '!=', 'cancel')],
        'extra_fields': ['origin'],
    },
    {
        'model': 'hr.employee',
        'label': 'Employee',
        'domain': [('active', '=', True)],
        'extra_fields': ['work_email', 'job_title'],
    },
    {
        'model': 'mrp.production',
        'label': 'Manufacturing',
        'domain': [],
        'extra_fields': ['origin'],
    },
    {
        'model': 'crm.lead',
        'label': 'Lead / Opportunity',
        'domain': [('active', '=', True)],
        'extra_fields': ['partner_name', 'email_from'],
    },
    {
        'model': 'helpdesk.ticket',
        'label': 'Helpdesk Ticket',
        'domain': [],
        'extra_fields': ['partner_name', 'partner_email'],
    },
]

class WebrightGlobalSearch(models.AbstractModel):
    _name = 'webright.global.search'
    _description = 'Webright Global Search'

    @api.model
    def search_records(self, query, limit=10, date_filter='all', date_from='', date_to=''):
        """Search across configured models and return matching records."""
        query = (query or '').strip().lstrip('/')
        if not query:
            return []

        limit = int(limit)
        is_numeric = query.isdigit()
        results = []

        # --- Parse exact Start and End bounds to prevent 2023 bleeding into ranges ---
        date_domain = []
        try:
            if date_filter == 'custom':
                if date_from:
                    date_domain.append(('create_date', '>=', f"{date_from} 00:00:00"))
                if date_to:
                    date_domain.append(('create_date', '<=', f"{date_to} 23:59:59"))
            elif date_filter != 'all':
                if date_filter.startswith('year_'):
                    year = int(date_filter.split('_')[1])
                    date_domain = [
                        ('create_date', '>=', f"{year}-01-01 00:00:00"),
                        ('create_date', '<=', f"{year}-12-31 23:59:59")
                    ]
                elif date_filter.startswith('month_'):
                    _, m_str, y_str = date_filter.split('_')
                    m, y = int(m_str), int(y_str)
                    start_dt = datetime(y, m, 1)
                    end_dt = start_dt + relativedelta(months=1, days=-1)
                    date_domain = [
                        ('create_date', '>=', start_dt.strftime('%Y-%m-%d 00:00:00')),
                        ('create_date', '<=', end_dt.strftime('%Y-%m-%d 23:59:59'))
                    ]
                elif date_filter.startswith('q'):
                    parts = date_filter.split('_')
                    q = int(parts[0][1])  # '1', '2', '3', '4'
                    y = int(parts[1])
                    start_month = (q - 1) * 3 + 1
                    start_dt = datetime(y, start_month, 1)
                    end_dt = start_dt + relativedelta(months=3, days=-1)
                    date_domain = [
                        ('create_date', '>=', start_dt.strftime('%Y-%m-%d 00:00:00')),
                        ('create_date', '<=', end_dt.strftime('%Y-%m-%d 23:59:59'))
                    ]
        except Exception as e:
            _logger.error("Error parsing date_filter: %s", e)

        for cfg in _SEARCH_CONFIG:
            model_name = cfg['model']
            if model_name not in self.env:
                continue
            model = self.env[model_name]
            if not model.check_access_rights('read', raise_exception=False):
                continue

            base_domain = list(cfg.get('domain', []))
            
            # Apply date domain only if the model has a create_date field
            if date_domain and 'create_date' in model._fields:
                base_domain += date_domain

            try:
                found = {}  # {record_id: label_string}
                
                rec_name = getattr(model, '_rec_name', None) or 'name'
                if rec_name not in model._fields:
                    rec_name = 'name'

                # Strategy 1: search the _rec_name field 
                if rec_name in model._fields:
                    for rec in model.search_read(
                        base_domain + [(rec_name, 'ilike', query)],
                        fields=['id', rec_name],
                        limit=limit,
                    ):
                        found[rec['id']] = _label(rec, rec_name)

                # Strategy 2: search by database ID
                if is_numeric:
                    num_id = int(query)
                    if num_id not in found:
                        for rec in model.search_read(
                            base_domain + [('id', '=', num_id)],
                            fields=['id', rec_name],
                            limit=1,
                        ):
                            found[rec['id']] = _label(rec, rec_name)

                # Strategy 3: search extra fields 
                extra = [
                    f for f in cfg.get('extra_fields', [])
                    if '.' not in f and f in model._fields
                ]
                if extra and len(found) < limit:
                    already = list(found.keys())
                    or_domain = ['|'] * (len(extra) - 1) + [(f, 'ilike', query) for f in extra]
                    exclude = [('id', 'not in', already)] if already else []
                    for rec in model.search_read(
                        base_domain + exclude + or_domain,
                        fields=['id', rec_name],
                        limit=limit - len(found),
                    ):
                        if rec['id'] not in found:
                            found[rec['id']] = _label(rec, rec_name)

                for rec_id, name in list(found.items())[:limit]:
                    results.append({
                        'id': rec_id,
                        'name': name,
                        'model': model_name,
                        'model_label': cfg['label'],
                    })

            except Exception:
                _logger.exception(
                    'webright_global_search: error searching %s', model_name
                )

        return results

def _label(rec, field):
    """Extract a plain string label from a search_read record."""
    val = rec.get(field)
    if isinstance(val, (list, tuple)):
        return val[1] if len(val) > 1 else str(val[0])
    return val or str(rec.get('id', ''))