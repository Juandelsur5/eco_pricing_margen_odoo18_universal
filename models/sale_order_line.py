from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_first_existing_field_value(self, record, field_names):
        for field_name in field_names:
            if field_name in record._fields:
                value = record[field_name]
                if value not in (False, None):
                    return value
        return False

    @api.onchange('product_id')
    def _onchange_product_id_set_price_from_pricelist(self):
        if not self.product_id or not self.order_id:
            return

        product = self.product_id
        pricelist = self.order_id.pricelist_id

        if not pricelist:
            return

        pricelist_name = (pricelist.name or '').upper().strip()

        price = False

        if 'TAT' in pricelist_name:
            price = self._get_first_existing_field_value(product, [
                'x_final_price_tat',
                'x_price_tat',
            ])

        elif 'POS' in pricelist_name:
            price = self._get_first_existing_field_value(product, [
                'x_final_price_pos',
                'x_price_pos',
            ])

        elif 'MAYORISTA' in pricelist_name:
            price = self._get_first_existing_field_value(product, [
                'x_final_price_mayorista',
                'x_price_mayorista',
            ])

        elif 'OFERTA' in pricelist_name:
            price = self._get_first_existing_field_value(product, [
                'x_final_price_oferta',
                'x_price_oferta',
            ])

        if price not in (False, None):
            self.price_unit = price
