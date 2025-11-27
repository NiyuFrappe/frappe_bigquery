from frappe import _

def get_data():
    return [
        {
            "module_name": "BigQuery Connector",
            "label": _("BigQuery Connector"),
            "icon": "fa fa-database",
            "image": "/assets/frappe_bigquery/icon.png",  # 
            "color": "blue",
            "type": "module",
            "description": _("Export Frappe data to Google BigQuery"),
            "items": [
                {
                    "type": "doctype",
                    "name": "BigQuery Settings",
                    "label": _("BigQuery Settings"),
                },
                {
                    "type": "doctype",
                    "name": "BigQuery Query",
                    "label": _("BigQuery Query"),
                }
            ]
        }
    ]
