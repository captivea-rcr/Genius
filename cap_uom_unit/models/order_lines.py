# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

from odoo.exceptions import UserError

from odoo import api, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for res in self:
            super(SaleOrderLine, res)._compute_amount()
            if res and res.product_uom.category_id.measure_type == 'unit' and \
                    res.product_uom_qty and res.product_uom_qty.is_integer():
                raise UserError(_(
                    "Invalid Product Quantity. You can not sell "
                    "partial quantities of items sold as Units."))


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        for res in self:
            super(StockMove, res)._compute_product_qty()
            if res and res.product_uom.category_id.measure_type == 'unit' and \
                    not res.product_uom_qty.is_integer():
                raise UserError(_(
                    "Invalid Product Quantity. You can not move "
                    "partial quantities of items sold as Units."))
