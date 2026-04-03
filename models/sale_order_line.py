from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'product_uom_qty', 'order_id.pricelist_id')
    def _compute_price_unit(self):
        super()._compute_price_unit()

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
