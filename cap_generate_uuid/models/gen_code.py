from odoo import api, fields, models, _
from odoo.exceptions import UserError
import string
import random


class BinId(models.Model):
    _name = 'bin.identifier'

    @staticmethod
    def code_generator(size=48, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @api.multi
    def default_code(self):
      code = self.code_generator()
      while self.env['bin.identifier'].search([("code", "=", code)], limit=1):
        code = self.code_generator()
      return code

    code = fields.Char(string='Identifier', size=48, default=default_code)

    # def generate_id(self):
    #     code = self.id_generator()
    #     if not self.env['bin.identifier'].sudo().search([('code', '=', code)]):
    #         values = {'code':code}
    #         new_bin_code = self.env['bin.identifier'].write(values)
    #     else:
    #         generate_id()
