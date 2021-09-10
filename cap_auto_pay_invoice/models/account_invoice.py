# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def auto_payment(self, id, journal_id, payment_method_id):
        try:
            inv = self.sudo().search([('id', '=', id)])
            if inv.state != 'open':
                return False
            bank = inv.partner_id.bank_ids and \
                   inv.partner_id.bank_ids[0].id or False
            vals = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': inv.partner_id.id,
                'partner_bank_account_id': bank,
                'amount': inv.amount_total,
                'communication': inv.number,
                'journal_id': journal_id,
                'payment_method_id': payment_method_id,
            }
            payment = self.env["account.payment"].create(vals)
            payment.post()
            inv.assign_outstanding_credit(
                payment.move_line_ids.filtered(lambda s: s.credit).id)
        except Exception as e:
            return e
        return True
