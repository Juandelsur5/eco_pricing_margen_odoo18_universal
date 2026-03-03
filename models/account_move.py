from odoo import models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):

        # Bypass solo para admin
        if not (self.env.is_superuser() or self.env.user.has_group("base.group_system")):

            for move in self:

                # Compras → requiere permiso actualizar costo
                if move.move_type in ["in_invoice", "in_refund", "in_receipt"]:
                    if not self.env.user.has_group(
                        "eco_pricing_margen.group_margen_precios_update_cost"
                    ):
                        raise UserError(
                            "No tiene permisos para postear documentos de compra que actualizan costo."
                        )

                # Ventas → requiere permiso aplicar venta
                if move.move_type in ["out_invoice", "out_refund", "out_receipt"]:
                    if not self.env.user.has_group(
                        "eco_pricing_margen.group_margen_precios_apply_sale"
                    ):
                        raise UserError(
                            "No tiene permisos para postear documentos de venta."
                        )

        res = super().action_post()

        # Lógica original intacta
        for move in self:
            if move.move_type in ["in_invoice", "in_refund"]:
                for line in move.invoice_line_ids:
                    if line.product_id and line.quantity:
                        cost_unit = line.price_subtotal / line.quantity
                        line.product_id.product_tmpl_id.x_cost_base = cost_unit

        return res
