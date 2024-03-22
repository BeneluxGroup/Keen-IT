# See LICENSE file for full copyright and licensing details.

{
    # Module information
    "name": "Instant Purchase Order From Sale Order",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "category": "Sales Management",
    "summary": """
    Create purchase order with single vendor
    or multiple vendor from sale order.
    Instant Purchase Order From Sale Order
    Quick Purchase Order From Sale Order
    Purchase Order From Sale Order
    SCS Sale Purchase
    SCS Sale Purchase odoo apps
    Sale Purchase module
    Quick purchase order
    scs_sale_purchase
    odoo apps scs sale purchase
    odoo apps create purchase order
    odoo apps sale to purchase
    odoo apps purchase document
    sale order to purchase order odoo apps
    create purchase order from sale order
    create purchase order from sale order odoo apps
    Multi Vendor Odoo apps by Serpentcs
    Single vendor Odoo apps by Serpentcs
    Quick Purchase Order odoo apps
    Quick RFQ/Purchase Order odoo apps
    Multi vendor
    Single Vendor
    Purchase Order
    Sale Order
    Purchase
    Sale
    """,
    # Author
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    # Dependencies
    "depends": ["sale_purchase"],
    # Views
    "data": [
        "security/ir.model.access.csv",
        "wizards/wiz_sale_purchase_order.xml",
        "views/purchase_order_views.xml",
        "views/sale_order_views.xml",
    ],
    # Odoo App Store Specific
    "images": ["static/description/Banner_scs_sale_purchase.png"],
    "live_test_url": "https://youtu.be/wE68idvriHc",
    # Technical
    "installable": True,
    "price": 30,
    "currency": "EUR",
}
