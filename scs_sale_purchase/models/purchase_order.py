"""Inherited Purchase order model."""
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class PurchaseOrder(models.Model):
    """inherit the purchase order model."""

    _inherit = "purchase.order"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", copy=False)
