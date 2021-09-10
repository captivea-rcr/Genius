# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import api, fields, models, _, tools
from email.utils import formataddr
from odoo.exceptions import UserError
from odoo.tools.translate import _

import base64
import json
import logging

_logger = logging.getLogger(__name__)


class PartnerCreationShortcut(models.TransientModel):
    _name = "partner.creation.shortcut"

    _description = "Shortcut to create partners"

    name = fields.Char(index=True, string="Business Name")
    contact = fields.Char(index=True, string="Contact")
    title = fields.Many2one('res.partner.title')
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    email_formatted = fields.Char(
        'Formatted Email', compute='_compute_email_formatted',
        help='Format email address "Name <email@domain>"')
    business_card = fields.Binary(string='Business Card')
    source = fields.Many2one('cap.partner.source', string='Source')
    user_id = fields.Many2one('res.users', string='Sales Rep')
    comment = fields.Text(string='Notes')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    @api.depends('name', 'email')
    def _compute_email_formatted(self):
        for partner in self:
            if partner.email:
                partner.email_formatted = formataddr((partner.name or u"False", partner.email or u"False"))
            else:
                partner.email_formatted = ''


    @api.multi
    def create_partner(self):
        partner_obj = self.env['res.partner']
        business_card = False
        if self.business_card:
            image = base64.b64decode(self.business_card)
            business_card = tools.image_resize_image_big(base64.b64encode(image))
        values = {
            'name': self.name,
            'title': self.title.id,
            'phone': self.phone,
            # 'mobile': self.mobile,
            'email': self.email,
            'email_formatted': self.email_formatted,
            'source': self.source.id,
            'business_card': business_card,
            'user_id': self.user_id.id,
            'comment': self.comment,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
        }

        if 'x_studio_primary_contact' in partner_obj._fields:
            values['x_studio_primary_contact'] = self.contact
        new_partner_id = partner_obj.create(values)
        image_attach = self.attach_image(business_card, new_partner_id)

        if 'action' in self.env.context:
            if self.env.context['action'] == 'next':
                view_id = self.env.ref('cap_contacts.cap_view_create_partner_short_form')
                return {
                    'res_model': 'partner.creation.shortcut',
                    'type': 'ir.actions.act_window',
                    'view_id': view_id.id,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new'
                }

        return new_partner_id

    @api.multi
    def attach_image(self, image_bin, partner_id):

        iao = self.env['ir.attachment']
        file_name = "business_card_%s.png" % partner_id.name
        data_attach = {
            'name': file_name,
            'datas': image_bin,
            'res_model': 'res.partner',
            'datas_fname': file_name,
            'res_id': partner_id.id,
            'type': 'binary',
        }
        attach_id = iao.sudo().create(data_attach)

        return attach_id
