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

        if name == "T.A.T":
            return product.x_final_price_tat
        elif name == "P.O.S":
            return product.x_final_price_pos
        elif name == "MAYORISTAS":
            return product.x_final_price_mayorista
        elif name == "OFERTA":
            return product.x_final_price_oferta

        return False

    def _apply_channel_price(self):
        for line in self:
            if not line.product_id or line.display_type:
                continue

            channel_price = line._get_channel_price_from_pricelist()
            if channel_price not in (False, None):
                line.price_unit = channel_price
                line.x_manual_price_from_pricelist = True

    @api.onchange("product_id")
    def _onchange_product_id_set_channel_price(self):
        self._apply_channel_price()

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty_keep_channel_price(self):
        self._apply_channel_price()

    @api.onchange("order_id.pricelist_id")
    def _onchange_pricelist_id_set_channel_price(self):
        self._apply_channel_price()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._apply_channel_price()
        return lines

    def write(self, vals):
        res = super().write(vals)

        fields_that_reprice = {"product_id", "product_uom_qty"}
        if set(vals.keys()) & fields_that_reprice:
            for line in self:
                if line.display_type:
                    continue
                if line.x_manual_price_from_pricelist:
                    line._apply_channel_price()

        return res
