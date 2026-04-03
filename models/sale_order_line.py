from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_manual_price_from_pricelist = fields.Boolean(
        string="Precio manual desde lista",
        default=False,
        copy=False,
    )

    def _get_channel_price_from_pricelist(self):
        self.ensure_one()

        product = self.product_id.product_tmpl_id
        pricelist = self.order_id.pricelist_id

        if not product or not pricelist:
            return False

        name = (pricelist.name or "").strip().upper()

        # 🔥 DETECCIÓN ROBUSTA (NO FALLA CON "(COP)")
        if "T.A.T" in name:
            return product.x_final_price_tat
        elif "P.O.S" in name:
            return product.x_final_price_pos
        elif "MAYORISTAS" in name:
            return product.x_final_price_mayorista
        elif "OFERTA" in name:
            return product.x_final_price_oferta

        return False

    def _force_channel_price(self):
        for line in self:
            if not line.product_id or line.display_type:
                continue

            price = line._get_channel_price_from_pricelist()
            if price not in (False, None):
                # 🔥 FORZAR PRECIO DESPUÉS DE ODOO
                super(SaleOrderLine, line).write({
                    "price_unit": price
                })
                line.x_manual_price_from_pricelist = True

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self._force_channel_price()

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty(self):
        self._force_channel_price()

    @api.onchange("order_id.pricelist_id")
    def _onchange_pricelist(self):
        self._force_channel_price()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._force_channel_price()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self._force_channel_price()
        return res
