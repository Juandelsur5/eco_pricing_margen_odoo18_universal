from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _onchange_product_id_force_price(self):
        self._force_price()

    @api.onchange('order_id.pricelist_id')
    def _onchange_pricelist_force_price(self):
        self._force_price()

    def _force_price(self):
        for line in self:
            product = line.product_id
            pricelist = line.order_id.pricelist_id

            if not product or not pricelist:
                continue

            name = (pricelist.name or "").strip().upper()
            tmpl = product.product_tmpl_id

            if "T.A.T" in name:
                line.price_unit = tmpl.x_final_price_tat
            elif "P.O.S" in name:
                line.price_unit = tmpl.x_final_price_pos
            elif "MAYORISTAS" in name:
                line.price_unit = tmpl.x_final_price_mayorista
            elif "OFERTA" in name:
                line.price_unit = tmpl.x_final_price_oferta

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._force_price()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self._force_price()
        return res
