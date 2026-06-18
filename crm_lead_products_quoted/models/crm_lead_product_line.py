from odoo import fields, models


class CrmLeadProductLine(models.Model):
    _name = 'crm.lead.product.line'
    _description = 'CRM Lead Products Quoted'

    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    qty = fields.Float(string='Quantity', default=1.0)
    # Mirrors product name so display_name shows the product instead of "crm.lead.product.line,{id}".
    name = fields.Char(related='product_id.name', store=True, readonly=True)
