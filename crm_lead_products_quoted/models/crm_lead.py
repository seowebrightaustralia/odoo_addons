from odoo import fields, models
from odoo.osv import expression


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
    sh_product_categ_search = fields.Char(
        string='Products Quoted — Category',
        compute='_compute_sh_product_categ_search',
        search='_search_sh_product_categ',
        store=False,
    )

    def _compute_sh_products_search(self):
        for rec in self:
            rec.sh_products_search = ''

    def _compute_sh_product_categ_search(self):
        for rec in self:
            rec.sh_product_categ_search = ''

    def _product_ids_for(self, operator, value):
        """Return product.template IDs matching name or internal reference.

        product.template.name is a jsonb-translated column in Odoo v18.
        On databases migrated from v16 the column may still be character
        varying, causing jsonb SQL functions to raise a DB error.  We isolate
        the name search inside a savepoint so a failure there does not abort
        the whole transaction; default_code (plain varchar) is always safe.
        """
        Product = self.env['product.template'].sudo()
        pids = set()
        # Name search — isolated in a savepoint in case of jsonb/varchar mismatch
        try:
            with self.env.cr.savepoint():
                pids.update(Product.search([('name', operator, value)], limit=2000).ids)
        except Exception:
            pass  # column type mismatch on migrated DB — skip name, use default_code
        # Internal reference — plain varchar, always safe
        pids.update(Product.search([('default_code', operator, value)], limit=2000).ids)
        return list(pids)

    def _categ_ids_for(self, operator, value):
        """Return product.public.category IDs matching name.

        category.name is translatable (jsonb in v18) — same DB migration risk
        as product.template.name.  Isolate in a savepoint so a SQL failure
        does not abort the surrounding transaction.
        """
        Categ = self.env['product.public.category'].sudo()
        try:
            with self.env.cr.savepoint():
                return Categ.search([('name', operator, value)], limit=2000).ids
        except Exception:
            return []

    def _search_sh_products(self, operator, value):
        domain = [('id', '=', False)]
        if self._enabled('crm_search.products'):
            pids = self._product_ids_for(operator, value)
            if pids:
                domain = expression.OR([domain, [('product_line_ids.product_id', 'in', pids)]])
        if self._enabled('crm_search.product_categ', False):
            cids = self._categ_ids_for(operator, value)
            if cids:
                domain = expression.OR([domain, [('product_line_ids.product_id.public_categ_ids', 'in', cids)]])
        return domain

    def _search_sh_product_categ(self, operator, value):
        cids = self._categ_ids_for(operator, value)
        if not cids:
            return [('id', '=', False)]
        return [('product_line_ids.product_id.public_categ_ids', 'in', cids)]

    def _search_sh_lead(self, operator, value):
        domain = super()._search_sh_lead(operator, value)
        if self._enabled('crm_search.products'):
            domain = expression.OR([
                domain,
                [('product_line_ids.product_id.default_code', operator, value)],
            ])
            pids = self._product_ids_for(operator, value)
            if pids:
                domain = expression.OR([domain, [('product_line_ids.product_id', 'in', pids)]])
        if self._enabled('crm_search.product_categ', False):
            cids = self._categ_ids_for(operator, value)
            if cids:
                domain = expression.OR([domain, [('product_line_ids.product_id.public_categ_ids', 'in', cids)]])
        return domain
