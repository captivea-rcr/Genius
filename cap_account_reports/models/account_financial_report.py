# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import models
from operator import itemgetter
from odoo.tools.safe_eval import safe_eval
from odoo.addons.account_reports.models.account_financial_report import FormulaLine
from odoo.addons.account_reports.models.account_financial_report import FormulaContext


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    def _get_columns_name(self, options):
        columns = [{'name': ''}]
        if options.get('analytic_tags'):
            for period in options['selected_analytic_tag_names']:
                columns += [{'name': period, 'class': 'number'}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number'},
                        {'name': _('Credit'), 'class': 'number'}]
        columns += [{'name': self.format_date(options), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                for analytic in options['selected_analytic_tag_names']:
                    columns += [{'name': analytic, 'class': 'number'}]
                columns += [{'name': period.get('string'), 'class': 'number'}]
            if options['comparison'].get('number_period') == 1 and not options.get('groups'):
                columns += [{'name': '%', 'class': 'number'}]

        if options.get('groups', {}).get('ids'):
            columns_for_groups = []
            for column in columns[1:]:
                for ids in options['groups'].get('ids'):
                    group_column_name = ''
                    for index, id in enumerate(ids):
                        column_name = self._get_column_name(
                            id, options['groups']['fields'][index])
                        group_column_name += ' ' + column_name
                    columns_for_groups.append(
                        {'name': column.get('name') + group_column_name, 'class': 'number'})
            columns = columns[:1] + columns_for_groups
        return columns


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _compute_line(self, currency_table, financial_report, group_by=None, domain=[]):
        results = super(AccountFinancialReportLine, self)._compute_line(
            currency_table, financial_report, group_by=group_by, domain=domain)
        if 'analytic_tag_ids' in self.env.context:
            analytic_tag_ids = self.env.context.get('analytic_tag_ids')
            tag_ids = analytic_tag_ids.ids
            for i in range(len(tag_ids)):
                domain = self._get_aml_domain()
                tables, where_clause, where_params = self.env[
                    'account.move.line']._query_get_tags(domain=domain, tags=int(tag_ids[i]))
                tag_no = str(tag_ids[i])
                sql = "SELECT COALESCE(SUM(\"account_move_line\".balance), 0) AS" + \
                    tag_no + "_balance  FROM " + tables + " WHERE " + where_clause
                self.env.cr.execute(sql, where_params)
                r = self.env.cr.dictfetchall()[0]
                results.update(r)
        return results

    def _eval_formula(self, financial_report, debit_credit, currency_table, linesDict_per_group, groups=False):
        groups = groups or {'fields': [], 'ids': [()]}
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        currency = self.env.user.company_id.currency_id
        line_res_per_group = []

        if not groups['ids']:
            return [{'line': {'balance': 0.0}}]

        # this computes the results of the line itself
        for group_index, group in enumerate(groups['ids']):
            self_for_group = self.with_context(
                group_domain=self._get_group_domain(group, groups))
            linesDict = linesDict_per_group[group_index]
            line = False

            if self.code and self.code in linesDict:
                line = linesDict[self.code]
            elif formulas and formulas['balance'].strip() == 'count_rows' and self.groupby:
                line_res_per_group.append(
                    {'line': {'balance': self_for_group._get_rows_count()}})
            elif formulas and formulas['balance'].strip() == 'from_context':
                line_res_per_group.append(
                    {'line': {'balance': self_for_group._get_value_from_context()}})
            else:
                line = FormulaLine(self_for_group, currency_table,
                                   financial_report, linesDict=linesDict)

            if line:
                res = {}
                res['balance'] = line.balance
                res['balance'] = currency.round(line.balance)
                if 'analytic_tag_ids' in self.env.context:
                    analytic_tag_ids = self.env.context['analytic_tag_ids']
                    tag_ids = analytic_tag_ids.ids
                    for i in range(len(tag_ids)):
                        tag_balance = "as" + str(tag_ids[i]) + "_balance"
                        if tag_balance not in line.__dict__:
                            res[tag_balance] = 0.0
                        for key, value in line.__dict__.items():
                            if key == tag_balance:
                                res[key] = value
                if debit_credit:
                    res['credit'] = currency.round(line.credit)
                    res['debit'] = currency.round(line.debit)
                line_res_per_group.append(res)
        # don't need any groupby lines for count_rows and from_context formulas
        if all('line' in val for val in line_res_per_group):
            return line_res_per_group

        columns = []
        # this computes children lines in case the groupby field is set
        if self.domain and self.groupby and self.show_domain != 'never':
            if self.groupby not in self.env['account.move.line']:
                raise ValueError(
                    _('Groupby should be a field from account.move.line'))

            groupby = [self.groupby or 'id']
            if groups:
                groupby = groups['fields'] + groupby
            groupby = ', '.join(['"account_move_line".%s' %
                                 field for field in groupby])

            aml_obj = self.env['account.move.line']
            sql, params = self._get_with_statement(financial_report)
            tables, where_clause, where_params = aml_obj._query_get(
                domain=self._get_aml_domain())
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''
            select, select_params = self._query_get_select_sum(currency_table)

            if 'analytic_tag_ids' in self.env.context:
                analytic_tag_ids = self.env.context.get('analytic_tag_ids')
                tag_ids = analytic_tag_ids.ids
                final_tag_list = []
                for i in range(len(tag_ids)):
                    domain = self._get_aml_domain()
                    tables, where_clause, where_params_new = self.env[
                        'account.move.line']._query_get_tags(domain=domain, tags=int(tag_ids[i]))
                    tag_no = str(tag_ids[i])
                    tag_balance = "as" + str(tag_ids[i]) + "_balance"
                    tag_sql = "select account_move_line.id, account_move_line.account_id, rel.account_analytic_tag_id, \
                        account_move_line.balance/count(rel1.account_analytic_tag_id) as " + tag_balance + ", " + groupby + "  \
                        from" + tables + " \
                        left join account_analytic_tag_account_move_line_rel as rel1 on rel1.account_move_line_id = account_move_line.id \
                        left join account_analytic_tag_account_move_line_rel as rel on rel.account_move_line_id = account_move_line.id \
                        where rel.account_analytic_tag_id =" + str(tag_ids[i]) + "AND " + where_clause + "\
                        group by account_move_line.id,rel.account_analytic_tag_id \
                        order by account_move_line.id"
                    params_new = params + where_params_new
                    self.env.cr.execute(tag_sql, where_params_new)
                    tag_result = self.env.cr.dictfetchall()
                    data = []
                    for result in tag_result:
                        data.append(result.get('account_id'))
                    account_list = set(data)
                    tag_dict = {}
                    for account in account_list:
                        tag_dict[account] = {tag_balance: 0}
                        tag_total = 0
                        for result in tag_result:
                            if result.get('account_id') == account:
                                tag_total += result.get(tag_balance)
                        tag_dict[account][tag_balance] = tag_total
                        tag_dict[account]['tag_id'] = result.get(
                            'account_analytic_tag_id')
                    final_tag_list.append(tag_dict)
                analytic_tag_ids = self.env.context.get('analytic_tag_ids')
                tag_ids = analytic_tag_ids.ids
            params += select_params
            #params += select_params
            sql = sql + "SELECT " + groupby + ", " + select + " FROM " + tables + \
                " WHERE " + where_clause + " GROUP BY " + groupby + " ORDER BY " + groupby
            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            self.env.cr.execute(sql, params)
            dict_tag_result = self.env.cr.dictfetchall()
            for group_index, group in enumerate(groups['ids']):
                linesDict = linesDict_per_group[group_index]
                results_for_group = [
                    result for result in results if group == result[:len(group)]]
                if results_for_group:
                    results_for_group = [r[len(group):]
                                         for r in results_for_group]
                    if 'analytic_tag_ids' in self.env.context:
                        analytic_tag_ids = self.env.context.get(
                            'analytic_tag_ids')
                        tag_ids = analytic_tag_ids.ids
                        tag_name = [
                            "as" + str(tag_ids[i]) + "_balance" for i in range(len(tag_ids))]
                        if dict_tag_result:
                            l = {}
                            tag_list = []
                            new_list = []
                            for list_dict in final_tag_list:
                                for tag in list_dict:
                                    for i in range(len(tag_ids)):
                                        tag_balance = "as" + \
                                            str(tag_ids[i]) + "_balance"
                                        for dict_result in dict_tag_result:
                                            account_id = dict_result.get(
                                                'account_id')
                                            if account_id == tag and list_dict[tag].get('tag_id') in tag_ids:
                                                if list_dict[tag].get(tag_balance) and tag_balance:
                                                    tag_list.append({'account_id': account_id, tag_balance: list_dict[
                                                                    tag].get(tag_balance) or 0.0})
                                        for z in tag_list:
                                            if tag_balance not in z:
                                                z.update({tag_balance: 0.0})
                                        new_list.append(tag_list)
                            tag_new_list = []
                            for n, i in enumerate(new_list):
                                if i not in new_list[n + 1:]:
                                    tag_new_list.append(i)
                            for data in dict_tag_result:
                                for x in tag_new_list[0]:
                                    if data.get('account_id') == x.get('account_id'):
                                        for key, value in x.items():
                                            if key != 'account_id':
                                                data.update({key: value})
                            dict_result_list = []
                            for data in dict_tag_result:
                                l = {}
                                for j in range(len(tag_ids)):
                                    tag_balance = "as" + \
                                        str(tag_ids[j]) + "_balance"
                                    if tag_balance not in data:
                                        data.update({tag_balance: 0.0})
                                for key, value in data.items():
                                    l.update({key: value})
                                    dict_result_list.append(l)
                            results_for_group = dict(
                                [(i.get('account_id'), i) for i in dict_result_list])
                        else:
                            results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[
                                2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                    else:
                        results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[
                            2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                    c = FormulaContext(self.env['account.financial.html.report.line'].with_context(
                        group_domain=self._get_group_domain(group, groups)), linesDict, currency_table, financial_report, only_sum=True)
                    if formulas:
                        for key in results_for_group:
                            c['sum'] = FormulaLine(
                                results_for_group[key], currency_table, financial_report, type='not_computed')
                            c['sum_if_pos'] = FormulaLine(results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed')
                            c['sum_if_neg'] = FormulaLine(results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                          currency_table, financial_report, type='not_computed')
                            for col, formula in formulas.items():
                                if col in results_for_group[key]:
                                    results_for_group[key][col] = safe_eval(
                                        formula, c, nocopy=True)
                    to_del = []
                    for key in results_for_group:
                        if self.env.user.company_id.currency_id.is_zero(results_for_group[key]['balance']):
                            to_del.append(key)
                    for key in to_del:
                        del results_for_group[key]
                    results_for_group.update(
                        {'line': line_res_per_group[group_index]})
                    columns.append(results_for_group)
                else:
                    res_vals = {'balance': 0.0}
                    if 'analytic_tag_ids' in self.env.context:
                        analytic_tag_ids = self.env.context['analytic_tag_ids']
                        tag_ids = analytic_tag_ids.ids
                        for i in range(len(tag_ids)):
                            tag_balance = "as" + str(tag_ids[i]) + "_balance"
                            res_vals.update({tag_balance: 0.0})
                    if debit_credit:
                        res_vals.update({'debit': 0.0, 'credit': 0.0})
                    columns.append({'line': res_vals})
        return columns or [{'line': res} for res in line_res_per_group]

    def _put_columns_together(self, data, domain_ids):
        res = dict((domain_id, []) for domain_id in domain_ids)
        for period in data:
            debit_credit = False
            if 'debit' in period['line']:
                debit_credit = True
            for domain_id in domain_ids:
                if 'analytic_tag_ids' in self.env.context:
                    analytic_tag_ids = self.env.context['analytic_tag_ids']
                    tag_ids = analytic_tag_ids.ids
                    for i in range(len(tag_ids)):
                        tag_balance = "as" + str(tag_ids[i]) + "_balance"
                        if tag_balance not in res:
                            res[domain_id].append(period.get(
                                domain_id, {tag_balance: 0})[tag_balance])
                if debit_credit:
                    res[domain_id].append(period.get(
                        domain_id, {'debit': 0})['debit'])
                    res[domain_id].append(period.get(
                        domain_id, {'credit': 0})['credit'])
                res[domain_id].append(period.get(
                    domain_id, {'balance': 0})['balance'])
        return res


class FormulaLine(FormulaLine):

    def __init__(self, obj, currency_table, financial_report, type='balance', linesDict=None):
        context = dict(financial_report._context or {})
        if linesDict is None:
            linesDict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
        if 'analytic_tag_ids' in context:
            analytic_tag_ids = context['analytic_tag_ids']
            tag_ids = analytic_tag_ids.ids
            for i in range(len(tag_ids)):
                field_name = "as" + str(tag_ids[i]) + "_balance"
                fields.update({field_name: 0.0})
        if type == 'balance':
            fields = obj._get_balance(
                linesDict, currency_table, financial_report)[0]
            linesDict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'account.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report)
                self.amount_residual = fields['amount_residual']
                if 'analytic_tag_ids' in context:
                    analytic_tag_ids = context['analytic_tag_ids']
                    tag_ids = analytic_tag_ids.ids
                    for i in range(len(tag_ids)):
                        tag_balance = "as" + str(tag_ids[i]) + "_balance"
                        if tag_balance in fields:
                            setattr(self, tag_balance, fields[tag_balance])

            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['account.financial.html.report.line']._compute_line(
                    currency_table, financial_report)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        if 'analytic_tag_ids' in context:
            self.__dict__ = fields
        for field_names in fields:
            setattr(self, field_names, fields[field_names])
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']
