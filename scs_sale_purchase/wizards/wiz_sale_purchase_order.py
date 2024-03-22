"""Wiz Sale Purchase TransientModel ."""
# See LICENSE file for full copyright and licensing details.

from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizSalePurchase(models.TransientModel):
    """Wiz Sale Purchase TransientModel ."""

    _name = "wiz.sale.purchase"
    _description = "Wizard Sale Purchase Order"

    vendor_id = fields.Many2one("res.partner", string="Vendor")
    schedule_date = fields.Datetime(string="Scheduled Date", default=datetime.today())
    order_selection = fields.Selection(
        [("rfq", "RFQ"), ("purchase", "Purchase Order")],
        default="rfq",
    )
    order_lines_ids = fields.One2many("wiz.sale.purchase.line", "wiz_sale_purchase_id")
    vendor_option = fields.Selection(
        [("single", "Single Vendor"), ("multi", "Multi Vendor")], default="single"
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company.id
    )
    l10n_in_company_country_code = fields.Char(
        related="company_id.country_id.code", string="Country code", store=True
    )
    l10n_in_purchase = fields.Boolean(
        compute="_compute_is_l10n_in_purchase",
        string="Is l10n In Purchase?",
        store=True,
    )
    l10n_in_sale = fields.Boolean(
        compute="_compute_is_l10n_in_sale", string="Is l10n In Sale?", store=True
    )
    l10n_in_gst_treatment = fields.Selection(
        [
            ("regular", "Registered Business - Regular"),
            ("composition", "Registered Business - Composition"),
            ("unregistered", "Unregistered Business"),
            ("consumer", "Consumer"),
            ("overseas", "Overseas"),
            ("special_economic_zone", "Special Economic Zone"),
            ("deemed_export", "Deemed Export"),
        ],
        string="GST Treatment",
    )

    @api.depends("vendor_option", "order_lines_ids", "order_selection", "company_id")
    def _compute_is_l10n_in_sale(self):
        """Method to compute the l10n_in_sale."""
        for wiz in self:
            wiz.l10n_in_sale = (
                self.env["ir.module.module"]
                .sudo()
                .search_count(
                    [("name", "=", "l10n_in_sale"), ("state", "=", "installed")]
                )
            )

    @api.depends("vendor_option", "order_lines_ids", "order_selection", "company_id")
    def _compute_is_l10n_in_purchase(self):
        """Method to compute the l10n_in_purchase."""
        for wiz in self:
            wiz.l10n_in_purchase = (
                self.env["ir.module.module"]
                .sudo()
                .search_count(
                    [("name", "=", "l10n_in_purchase"), ("state", "=", "installed")]
                )
            )

    def _get_order_lines(self, order_lines=None):
        """Get Order lines to create PO."""
        if order_lines is None:
            order_lines = []
        po_l_vals = []
        if order_lines:
            po_l_vals = [
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "name": line.name,
                        "product_qty": line.qty,
                        "price_unit": line.price_unit,
                        "product_uom": line.uom_id.id,
                        "taxes_id": line.taxes_id and [(6, 0, line.taxes_id.ids)] or [],
                    },
                )
                for line in order_lines
            ]
        return po_l_vals

    def action_create_purchase_order(self):
        """Button method to create purchase order."""
        purchase_obj = self.env["purchase.order"]
        sale_rec = self.env[self.env.context["active_model"]].browse(
            self.env.context["active_id"]
        )
        vals = {
            "sale_order_id": sale_rec.id,
            "name": "New",
            "origin": sale_rec.name or "",
        }
        for wiz in self:
            if not wiz.order_lines_ids:
                raise ValidationError(
                    _(
                        "Without order lines you "
                        "cannot create purchase order."
                        "\nPlease select at least "
                        "one order line."
                    )
                )
            is_purchase_flag = False
            if wiz.order_selection == "purchase":
                is_purchase_flag = True
                vals.update({"date_approve": wiz.schedule_date})
            else:
                vals.update({"date_order": wiz.schedule_date})

            if wiz.vendor_option == "single":
                if wiz.l10n_in_purchase:
                    vals.update({"l10n_in_gst_treatment": wiz.l10n_in_gst_treatment})
                vals.update(
                    {
                        "partner_id": wiz.vendor_id.id,
                        "order_line": self._get_order_lines(wiz.order_lines_ids),
                    }
                )
                purchase_obj |= purchase_obj.create(vals)
            else:
                vendors = wiz.order_lines_ids.mapped("vendor_id")
                vendor_check = wiz.order_lines_ids.filtered(
                    lambda vendor: not vendor.vendor_id
                )
                if vendor_check:
                    raise ValidationError(
                        _(
                            "Without vendor selection you "
                            "cannot create purchase order."
                            "\n Please select vendor "
                            "in order line."
                        )
                    )
                if not vendors:
                    raise ValidationError(
                        _(
                            "Without vendor selection you "
                            "cannot create purchase order."
                            "\n Please select vendor "
                            "at least in one order line."
                        )
                    )
                for vendor in vendors:
                    vendor_line = wiz.order_lines_ids.filtered(
                        lambda v: v.vendor_id == vendor
                    )
                    if wiz.l10n_in_purchase:
                        gst_treats = list(
                            set(vendor_line.mapped("l10n_in_gst_treatment"))
                        )
                        for gst_treat in gst_treats:
                            gst_v_lines = vendor_line.filtered(
                                lambda v: v.l10n_in_gst_treatment == gst_treat
                            )
                            vals.update(
                                {
                                    "l10n_in_gst_treatment": gst_treat,
                                    "name": "New",
                                    "partner_id": vendor.id,
                                    "order_line": self._get_order_lines(gst_v_lines),
                                }
                            )
                            purchase_obj |= purchase_obj.create(vals)
                    else:
                        vals.update(
                            {
                                "name": "New",
                                "partner_id": vendor.id,
                                "order_line": self._get_order_lines(vendor_line),
                            }
                        )
                        purchase_obj |= purchase_obj.create(vals)
            if purchase_obj:
                if is_purchase_flag:
                    purchase_obj.button_confirm()

    @api.model
    def default_get(self, fields):
        """Default_get method.

        For getting the order lines from sales order
        in create purchase order wizard.
        """
        context = self.env.context
        res = super(WizSalePurchase, self).default_get(fields)
        company = self.env.company
        country_code = company.country_id.code
        sale_order = self.env["sale.order"].browse(context.get("active_id"))
        if sale_order.company_id:
            res.update(
                {
                    "company_id": sale_order
                    and sale_order.company_id
                    and sale_order.company_id.id
                }
            )
        res.update(
            {
                "order_lines_ids": [
                    (
                        0,
                        0,
                        {
                            "name": order_line.name,
                            "product_id": order_line.product_id.id,
                            "qty": order_line.product_uom_qty,
                            "price_unit": order_line.product_id.standard_price
                            or order_line.price_unit,
                            "uom_id": order_line.product_uom.id,
                            "subtotal": order_line.product_uom_qty
                            * (
                                order_line.product_id.standard_price
                                or order_line.price_unit
                            ),
                            "taxes_id": order_line.product_id
                            and [
                                (
                                    6,
                                    0,
                                    order_line.product_id.supplier_taxes_id
                                    and order_line.product_id.supplier_taxes_id.ids
                                    or [],
                                )
                            ],
                        },
                    )
                    for order_line in sale_order.order_line.filtered(
                        lambda ol: ol.product_id.purchase_ok
                    )
                    if not order_line.display_type
                ]
            }
        )
        l10n_in_sale = (
            self.env["ir.module.module"]
            .sudo()
            .search_count([("name", "=", "l10n_in_sale"), ("state", "=", "installed")])
        )
        if l10n_in_sale and country_code == "IN":
            res["l10n_in_gst_treatment"] = sale_order.l10n_in_gst_treatment
        return res

    @api.onchange("vendor_id")
    def onchange_vendor(self):
        for wiz_vendor in self.order_lines_ids:
            if wiz_vendor.wiz_sale_purchase_id.vendor_option == "single":
                if wiz_vendor.wiz_sale_purchase_id.vendor_id:
                    vendor_price = wiz_vendor.product_id.seller_ids.filtered(
                        lambda v: v.partner_id
                        == wiz_vendor.wiz_sale_purchase_id.vendor_id
                    ).mapped("price")
                    wiz_vendor.price_unit = (
                        min(vendor_price)
                        if vendor_price
                        else wiz_vendor.product_id.standard_price or 1.0
                    )
            if wiz_vendor.wiz_sale_purchase_id.vendor_option == "multi":
                wiz_vendor.wiz_sale_purchase_id.vendor_id = False

    # flake8: noqa: C901
    @api.onchange("vendor_option")
    def onchange_vendor_id(self):
        """This is onchange use to set the product price unit"""

        if self.vendor_option == "multi":
            for line in self.order_lines_ids:
                if line.product_id.seller_ids:
                    price_list = []
                    for record in line.product_id.seller_ids:
                        if record.date_start and record.date_end:
                            if (
                                record.date_start <= date.today()
                                and record.date_end >= date.today()
                            ):
                                if line.qty >= record.min_qty:
                                    price_list.append(record.price)
                                    if price_list:
                                        line.price_unit = min(price_list) or 0
                                    if line.price_unit == record.price:
                                        line.vendor_id = record.partner_id or False

                        elif record.date_start:
                            if record.date_start < date.today():
                                if line.qty >= record.min_qty:
                                    price_list.append(record.price)
                                    if price_list:
                                        line.price_unit = min(price_list) or 0
                                    if line.price_unit == record.price:
                                        line.vendor_id = record.partner_id or False

                        elif record.date_end:
                            if record.date_end > date.today():
                                if line.qty >= record.min_qty:
                                    price_list.append(record.price)
                                    if price_list:
                                        line.price_unit = min(price_list) or 0
                                    if line.price_unit == record.price:
                                        line.vendor_id = record.partner_id or False
                        else:
                            if line.qty >= record.min_qty:
                                price_list.append(record.price)
                                if price_list:
                                    line.price_unit = min(price_list) or 0
                                if line.price_unit == record.price:
                                    line.vendor_id = record.partner_id or False

        if self.vendor_option == "single":
            for line in self.order_lines_ids:
                line.price_unit = line.product_id.standard_price or line.price_unit


class WizSalePurchaseLine(models.TransientModel):
    """Wiz Sale Purchase Line model."""

    _name = "wiz.sale.purchase.line"
    _description = "Wizard Sale Purchase Line"

    product_id = fields.Many2one("product.product", string="Product")
    wiz_sale_purchase_id = fields.Many2one(
        "wiz.sale.purchase", string="Wiz Sale Purchase"
    )
    name = fields.Text(string="Description")
    qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(compute="_compute_sub_total", store=True)
    uom_id = fields.Many2one("uom.uom", "UoM")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
    )
    l10n_in_gst_treatment = fields.Selection(
        [
            ("regular", "Registered Business - Regular"),
            ("composition", "Registered Business - Composition"),
            ("unregistered", "Unregistered Business"),
            ("consumer", "Consumer"),
            ("overseas", "Overseas"),
            ("special_economic_zone", "Special Economic Zone"),
            ("deemed_export", "Deemed Export"),
        ],
        string="GST Treatment",
    )
    l10n_in_company_country_code = fields.Char(
        related="wiz_sale_purchase_id.l10n_in_company_country_code",
        string="Country code",
        store=True,
    )
    l10n_in_purchase = fields.Boolean(
        related="wiz_sale_purchase_id.l10n_in_purchase",
        string="Is l10n In Purchase?",
        store=True,
    )
    l10n_in_sale = fields.Boolean(
        related="wiz_sale_purchase_id.l10n_in_sale",
        string="Is l10n In Sale?",
        store=True,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Onchange to calculate the subtotal."""
        product_des = ""
        product = self.product_id
        vendor_price = 1.0
        if product:
            code = product.default_code and "[" + product.default_code + "] " or ""
            product_des = code + product.name or ""

        if self.wiz_sale_purchase_id.vendor_option == "single":
            if self.wiz_sale_purchase_id.vendor_id:
                vendor_price = self.product_id.seller_ids.filtered(
                    lambda v: v.partner_id == self.wiz_sale_purchase_id.vendor_id
                ).mapped("price")
                vendor_price = (
                    min(vendor_price)
                    if vendor_price
                    else self.product_id.standard_price or 1.0
                )
        else:
            if self.product_id.seller_ids:
                self.vendor_id = self.product_id.seller_ids.partner_id[0] or False
                self.price_unit = self.product_id.seller_ids[0].price or False

        self.update(
            {
                "name": product_des or "",
                "price_unit": vendor_price,
                "qty": self.qty or 1.0,
                "uom_id": product
                and product.uom_po_id
                or product
                and product.uom_id
                or False,
                "taxes_id": product
                and [
                    (
                        6,
                        0,
                        product.supplier_taxes_id
                        and product.supplier_taxes_id.ids
                        or [],
                    )
                ]
                or [],
            }
        )

    @api.onchange("vendor_id", "wiz_sale_purchase_id")
    def onchange_vendor_id(self):
        for line in self:
            if line.wiz_sale_purchase_id.vendor_option == "multi":
                if line.vendor_id:
                    vendor_price = line.product_id.seller_ids.filtered(
                        lambda v: v.partner_id == line.vendor_id
                    ).mapped("price")
                    line.price_unit = (
                        min(vendor_price)
                        if vendor_price
                        else line.product_id.standard_price or 1.0
                    )
            if line.wiz_sale_purchase_id.vendor_option == "single":
                line.vendor_id = False

    @api.depends("qty", "price_unit")
    def _compute_sub_total(self):
        """Method to compute the subtotal."""
        for line in self:
            line.subtotal = line.qty * line.price_unit
