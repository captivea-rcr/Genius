# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KioskContacts(models.Model):
    _inherit = 'res.partner'

    kiosk_category_id = fields.Many2one('res.category', string="Category")
    kiosk_sub_category_id = fields.Many2one('res.sub_category', string="Sub-Category", domain="[('category_id', '=', kiosk_category_id)]")

class KioskCategories(models.Model):
    _name = 'res.category'
    _description = "Kiosk Category"

    name = fields.Char()
    sub_category_ids = fields.One2many('res.sub_category', 'category_id', string="Sub Categories")

class KioskSubCategories(models.Model):
    _name = 'res.sub_category'
    _description = "Kiosk Sub-Category"

    name = fields.Char()
    category_id = fields.Many2one('res.category', string="Parent Category")
