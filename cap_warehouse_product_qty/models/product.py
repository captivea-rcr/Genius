# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        domain = args or []
        if not name and 'delivery_location_id' not in self._context:
            return []
        if 'delivery_location_id' in self._context:
            product_ids = self.env['stock.quant'].search([
                ('location_id', '=', self._context['delivery_location_id']),
                ('quantity', '>', 0)
            ]).mapped('product_id.id')
            domain += [
                ('id', 'in', product_ids)
            ]
        res = self.search(domain, limit=limit).with_context(self._context).name_get()
        return res

    @api.multi
    def name_get(self):
        result = []
        if 'delivery_location_id' in self._context:
            for p in self:
                result.append((p.id, p.name))
            return result
        return super(Product, self).name_get()
