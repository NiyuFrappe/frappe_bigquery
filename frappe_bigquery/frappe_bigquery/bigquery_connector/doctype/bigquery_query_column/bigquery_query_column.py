import frappe
from frappe.model.document import Document

class BigQueryQueryColumn(Document):
    """Child table for storing selected columns for a BigQuery Query."""
    pass
