from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)

        for line in lines:
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

        return lines
