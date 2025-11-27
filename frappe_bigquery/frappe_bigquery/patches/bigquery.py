import os

import frappe
from frappe.modules.import_file import import_file_by_path
from frappe.modules.utils import get_module_path, scrub


def ensure_bigquery_doctype():
    """Re-create BigQuery Query DocType if migrate has deleted it."""
    doctype_name = "BigQuery Query"

    # If it already exists, nothing to do
    if frappe.db.exists("DocType", doctype_name):
        return

    # Locate the JSON file of this DocType in the app
    module_path = get_module_path("BigQuery Connector")  # uses modules.txt
    folder_name = scrub(doctype_name)                    # "bigquery_query"
    json_path = os.path.join(
        module_path,
        "doctype",
        folder_name,
        f"{folder_name}.json",
    )

    if not os.path.exists(json_path):
        frappe.log_error(
            f"BigQuery Query JSON not found at {json_path}",
            "frappe_bigquery.ensure_bigquery_doctype",
        )
        return

    # Import the DocType definition from JSON
    import_file_by_path(json_path, force=True)
    frappe.db.commit()
