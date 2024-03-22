"""Inherit the sale order model."""
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    """Inherit the sale order model."""

    _inherit = "sale.order"

    name = fields.Char(index=True, required=True)

    def _get_purchase_orders(self):
        purchase_obj = self.env["purchase.order"]
        return super()._get_purchase_orders() | purchase_obj.search(
            [("sale_order_id", "=", self.id)]
        )
