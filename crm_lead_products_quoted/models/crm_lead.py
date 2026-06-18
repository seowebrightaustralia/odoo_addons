from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_line_ids = fields.One2many(
        'crm.lead.product.line', 'lead_id', string='Products Quoted'
    )
