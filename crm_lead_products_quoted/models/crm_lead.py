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
        get = self.env['ir.config_parameter'].sudo().get_param
        products_on = get('crm_search.products', '1') != '0'
        categ_on = get('crm_search.product_categ', '0') != '0'
        parts = []
        if products_on:
            # product_line_ids.name is non-stored — traverse to stored field.
            parts.append(('product_line_ids.product_id.name', operator, value))
        if categ_on:
            parts.append(('product_line_ids.product_id.public_categ_ids.display_name', operator, value))
        if not parts:
            return [('id', '=', False)]
        if len(parts) == 1:
            return [parts[0]]
        return ['|'] + [list(p) for p in parts]
