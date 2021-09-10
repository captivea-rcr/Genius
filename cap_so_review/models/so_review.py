# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import models, fields, api


class SaleOrderReview(models.Model):
    _name = 'sale.order.review'
    _rec_name = "so_id"
    _description = "Sale Order Review"
    _order = "date DESC, rate DESC"

    date = fields.Date(string="Date", default=fields.Date.today())
    so_id = fields.Many2one("sale.order", string="Order")
    partner_id = fields.Many2one(related="so_id.partner_id")
    note = fields.Text(string="Note")
    rate = fields.Selection([
        ('0', 'None'),
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Normal'),
        ('4', 'High'),
        ('5', 'Very High'),
    ], string="Satisfaction")

    @api.multi
    def action_redirect_to_record(self):
        view_id = self.env.ref('sale.view_order_form')
        return {
            'res_model': 'sale.order',
            'res_id': self.so_id.id,
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current'
        }


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rate_ids = fields.One2many("sale.order.review", "so_id",
                               string="Order Ratings")


class ResPartner(models.Model):
    _inherit = "res.partner"

    rate_ids = fields.One2many("sale.order.review", "partner_id",
                               string="Orders Ratings")
