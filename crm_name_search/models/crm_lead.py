from odoo import fields, models
from odoo.osv import expression


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sh_full_name_search = fields.Char(
        string='First or Last Name',
        compute='_compute_sh_full_name_search',
        search='_search_sh_full_name',
        store=False,
    )

    def _compute_sh_full_name_search(self):
        for rec in self:
            parts = filter(None, [rec.sh_firstname, rec.sh_lastname])
            rec.sh_full_name_search = ' '.join(parts)

    def _search_sh_full_name(self, operator, value):
        if operator in ('ilike', 'like', '=ilike', '=like') and value and ' ' in value:
            parts = value.split(' ', 1)
            return expression.OR([
                expression.AND([
                    [('sh_firstname', operator, parts[0])],
                    [('sh_lastname', operator, parts[1])],
                ]),
                expression.AND([
                    [('sh_firstname', operator, parts[1])],
                    [('sh_lastname', operator, parts[0])],
                ]),
            ])
        return ['|', ('sh_firstname', operator, value), ('sh_lastname', operator, value)]
