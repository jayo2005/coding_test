# Part of Softhealer Technologies.
{
    "name": "Import Base Automated",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.19",

    "license": "OPL-1",

    "category": "Sales",

    "summary": "Import Base",

    "description": """Import Base""",

    "depends": ['sale_management','wk_product_dimensions','stock','purchase','sale_order_line_delivery_state','sale_delivery_state','sale_stock','account','stock_account'],

    "data": [
        "security/ir.model.access.csv",
        "data/sh_import_cron_data.xml",

        "views/sh_import_base_views.xml",
        "views/sh_import_base_logs_views.xml",
        "views/sh_import_failed_views.xml",
        "views/sh_import_menus.xml",
        "views/product_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/background.png", ],
    "price": "0",
    "currency": "EUR"
}
