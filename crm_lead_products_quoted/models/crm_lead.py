from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_line_ids = fields.One2many(
        'crm.lead.product.line', 'lead_id', string='Products Quoted'
    )
    # Virtual Char field — One2many has no search widget in Odoo v18 and causes
    # CrmKanbanArchParser to crash. Wrap behind Char so the arch parser resolves
    # a safe widget type; _search_sh_products routes the query to product_line_ids.
    sh_products_search = fields.Char(
        string='Products Quoted',
        compute='_compute_sh_products_search',
        search='_search_sh_products',
        store=False,
    )

    def _compute_sh_products_search(self):
        for rec in self:
            rec.sh_products_search = ''

    def _search_sh_products(self, operator, value):
        # product_line_ids.name is non-stored (store=False), so traverse to the
        # stored field directly instead of relying on SQL column resolution.
        return [('product_line_ids.product_id.name', operator, value)]
