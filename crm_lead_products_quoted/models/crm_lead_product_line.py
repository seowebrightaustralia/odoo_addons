from odoo import fields, models


class CrmLeadProductLine(models.Model):
    _name = 'crm.lead.product.line'
    _description = 'CRM Lead Products Quoted'

    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    qty = fields.Float(string='Quantity', default=1.0)
    # store=False: product.template.name is jsonb-translated in Odoo v18; storing
    # it as varchar (no translate=True) causes a psycopg2 type mismatch on flush.
    # display_name reads this at compute time — no DB column needed.
    name = fields.Char(related='product_id.name', store=False, readonly=True)
