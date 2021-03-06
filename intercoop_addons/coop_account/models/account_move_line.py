# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        related='move_id.statement_line_id',
        string='Bank Statement Line')

    @api.multi
    @api.constrains('move_id', 'account_id')
    def check_account_type_bank(self):
        for line in self:
            if line.move_id:
                line_account_bank = line.move_id.line_ids.filtered(
                        lambda a: a.account_id.reconciled_account)
                if len(line_account_bank) > 1:
                    raise UserError(_(
                        'Only one journal item on an account requiring ' +
                        'bank reconciliation can be booked in this ' +
                        'account move. It is impossible to add another ' +
                        'one. Please create a distinct account move to ' +
                        'registrer this account.move.line and its ' +
                        'counterpart.'))

    def _create_writeoff(self, vals):
        res = super(AccountMoveLine, self)._create_writeoff(vals)
        partner = self.mapped('partner_id')
        lines = res.mapped('move_id.line_ids')
        for line in lines:
            line.partner_id = partner.id if len(partner) == 1 and\
                not any(not line.partner_id for line in self)\
                else False
        return res
