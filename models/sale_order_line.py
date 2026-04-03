from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_price(self):
        self.ensure_one()

        product = self.product_id
        pricelist = self.order_id.pricelist_id

        if not product or not pricelist:
            return super()._get_product_price()

        name = (pricelist.name or "").strip().upper()
        tmpl = product.product_tmpl_id

        if "T.A.T" in name:
            return tmpl.x_final_price_tat
        elif "P.O.S" in name:
            return tmpl.x_final_price_pos
        elif "MAYORISTAS" in name:
            return tmpl.x_final_price_mayorista
        elif "OFERTA" in name:
            return tmpl.x_final_price_oferta

        return super()._get_product_price()
