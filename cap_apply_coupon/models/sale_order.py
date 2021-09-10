# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

from odoo.exceptions import UserError

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _genius_get_reward_values_discount(self, program):
        if program.discount_type == 'fixed_amount':
            return [{
                'name': _("Discount: ") + program.name,
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'product_uom_qty': 1.0,
                'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in program.discount_line_product_id.taxes_id],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = line.price_reduce * (program.discount_percentage / 100)
                if discount_line_amount:
                    taxes = line.tax_id
                    if self.fiscal_position_id:
                        taxes = self.fiscal_position_id.map_tax(taxes)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: ") + program.name,
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in program.discount_line_product_id.taxes_id],
                    }
        elif program.discount_apply_on in ['specific_product', 'on_order']:
            if program.discount_apply_on == 'specific_product':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['sale.coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', '=', program.discount_specific_product_id.id)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id == program.discount_specific_product_id or x.product_id in free_product_lines)

            for line in lines:
                discount_line_amount = self._get_reward_values_discount_percentage_per_line(program, line)

                if discount_line_amount:

                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = line.tax_id
                        if self.fiscal_position_id:
                            taxes = self.fiscal_position_id.map_tax(taxes)

                        tax_name = ""
                        if len(taxes) == 1:
                            tax_name = " - " + _("On product with following tax: ") + ', '.join(taxes.mapped('name'))
                        elif len(taxes) > 1:
                            tax_name = " - " + _("On product with following taxes: ") + ', '.join(taxes.mapped('name'))

                        reward_dict[line.tax_id] = {
                            'name': _("Discount: ") + program.name + tax_name,
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in program.discount_line_product_id.taxes_id],
                        }

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()

    def _genius_get_reward_line_values(self, program):
        self.ensure_one()
        self = self.with_context(lang=self.partner_id.lang)
        program = program.with_context(lang=self.partner_id.lang)
        if program.reward_type == 'discount':
            return self._genius_get_reward_values_discount(program)
        elif program.reward_type == 'product':
            return [self._get_reward_values_product(program)]

    @api.multi
    def api_create_reward_line(self, coupon_code):
        program = self.env['sale.coupon.program'].search([('promo_code', '=', coupon_code)])
        self.write({'order_line': [(0, False, value) for value in self._genius_get_reward_line_values(program)]})
