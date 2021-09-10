# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import api, fields, models, _
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo.tools.translate import _

import base64
import json
import logging

_logger = logging.getLogger(__name__)


class CapResPartner(models.Model):

    _inherit = 'res.partner'

    source = fields.Many2one('cap.partner.source', string='Source')
    business_card = fields.Binary(string='Business Card', attachment=True,)


class CapPartnerSource(models.Model):

    _name = 'cap.partner.source'

    name = fields.Char(index=True, string="Source")

