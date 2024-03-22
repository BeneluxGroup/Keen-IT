import datetime

from odoo import api, models


class ResPartner(models.Model):
    """Model res partner extended."""

    _inherit = "res.partner"

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, order=None):
        """Overwritten this method for the select only product vendor in the wizard."""
        context = self._context or {}
        vendor_ids = []
        vendor_list = []
        vendor_rec = self.env["res.partner"].search([])
        if context.get("product_id"):
            product_id = self.env["product.product"].search(
                [("id", "=", context.get("product_id"))], limit=1
            )
            if product_id.seller_ids:
                today_date = datetime.date.today()
                for vendor_id in product_id.seller_ids:
                    if vendor_id.date_start and vendor_id.date_end:
                        if vendor_id.date_start <= today_date <= vendor_id.date_end:
                            vendor_ids.append(vendor_id.name.id)
                            args += [("id", "in", vendor_ids)]

                        elif not (
                            vendor_id.date_start > today_date
                            and vendor_id.date_end < today_date
                        ):
                            if vendor_rec:
                                for rec in vendor_rec:
                                    vendor_list.append(rec.id)
                                    args += [("id", "in", vendor_list)]

                    elif vendor_id.date_start:
                        if vendor_id.date_start <= today_date:
                            vendor_ids.append(vendor_id.name.id)
                            args += [("id", "in", vendor_ids)]
                        else:
                            for rec in vendor_rec:
                                vendor_list.append(rec.id)
                                args += [("id", "in", vendor_list)]

                    elif vendor_id.date_end:

                        if vendor_id.date_end >= today_date:
                            vendor_ids.append(vendor_id.name.id)
                            args += [("id", "in", vendor_ids)]
                        else:
                            for rec in vendor_rec:
                                vendor_list.append(rec.id)
                                args += [("id", "in", vendor_list)]
                    else:
                        for rec in vendor_rec:
                            vendor_list.append(rec.id)
                            args += [("id", "in", vendor_list)]

        return super()._name_search(name, args, operator, limit=limit, order=None)
