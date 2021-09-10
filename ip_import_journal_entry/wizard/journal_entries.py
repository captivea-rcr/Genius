# -*- coding: utf-8 -*-
import tempfile
import binascii
import xlrd
import logging
from datetime import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    from io import StringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class ImportJournalEntries(models.TransientModel):
    _name = "import.account.move"

    file = fields.Binary(string='File')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='csv')

    @api.multi
    def create_journal_entries(self, values):
        return {
            'name': _(values.get('name')),
            'debit': float(values.get('debit')),
            'credit': float(values.get('credit')),
            'account_id': self.check_account(values.get('account_id')),
            'move_id': self._context.get('active_id'),
            'currency_id': self.check_currency(values.get('currency_id')),
            'amount_currency': values.get('amount_currency'),
            'partner_id': self.check_partner(values.get('partner_id')),
            'date_maturity': values.get('date_maturity'),
            'company_id': self.env.user.company_id.id,
        }

    @api.multi
    def check_partner(self, name):
        partner_id = self.env['res.partner'].search([('name', '=', name)])
        if not partner_id:
            raise Warning(_(' "%s" Partner is not available.') % name)
        return partner_id.id

    @api.multi
    def check_account(self, code):
        account_id = self.env['account.account'].search([('code', '=', code)])
        if not account_id:
            raise Warning(_(' "%s" Account is not available.') % code)
        return account_id.id

    @api.multi
    def check_currency(self, name):
        currency_id = self.env['res.currency'].search([('name', '=', name)])
        if not currency_id:
            raise Warning(_(' "%s" Currency is not available.') % name)
        return currency_id.id

    @api.multi
    def import_journal_entries(self):
        res = []
        journal_id = self.env['account.move'].browse(self._context.get('active_id'))
        if self.import_option == 'csv':
            keys = ['name', 'account_id', 'partner_id', 'analytic_account_id', 'amount_currency', 'currency_id', 'debit', 'credit', 'date_maturity']
            data = base64.b64decode(self.file)
            file_input = StringIO(data.decode("utf-8"))
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')
            try:
                reader_info.extend(reader)
            except Exception:
                raise Warning(_("Not a valid file!"))
            values = {}
            for i in range(len(reader_info)):
                field = map(str, reader_info[i])
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'option': self.import_option})
                        res.append((0, 0, self.create_journal_entries(values)))
        else:
            fx = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fx.write(binascii.a2b_base64(self.file))
            fx.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fx.name)
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    field = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    journal_line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                    datetime_xlt = datetime(*xlrd.xldate_as_tuple(int(float(journal_line[8])), workbook.datemode))
                    string_dt = datetime_xlt.date().strftime('%Y-%m-%d')
                    values.update({
                            'name': journal_line[0],
                            'account_id': journal_line[1],
                            'partner_id': journal_line[2],
                            'analytic_account_id': journal_line[3],
                            'amount_currency': journal_line[4],
                            'currency_id': journal_line[5],
                            'debit': journal_line[6],
                            'credit': journal_line[7],
                            'date_maturity': string_dt,
                            })
                    res.append((0, 0, self.create_journal_entries(values)))
        journal_id.line_ids = res
        return res
