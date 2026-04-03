from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_set_price_from_tat(self):
        if not self.product_id:
            return

        product = self.product_id

        costo = product.standard_price or 0
        margen = 0.15
        precio = costo * (1 + margen)

        self.price_unit = precio
