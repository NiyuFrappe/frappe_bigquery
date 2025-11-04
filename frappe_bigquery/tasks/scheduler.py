import frappe
from frappe.utils import now_datetime, add_to_date
from ..frappe_bigquery.doctype.bigquery_query.bigquery_query import run_query_for_doc

def run_due_queries():
    docs = frappe.get_all("BigQuery Query",
                          filters={"incremental_sync_enabled": 1, "is_locked": 0},
                          fields=["name","interval_minutes","last_sync"])
    now = now_datetime()
    for d in docs:
        interval = d.get("interval_minutes") or 15
        last_sync = d.get("last_sync")
        due = True
        if last_sync:
            due = now >= add_to_date(last_sync, minutes=interval)
        if due:
            try:
                run_query_for_doc(d["name"])
            except Exception:
                frappe.log_error(frappe.get_traceback(), f"BigQuery Scheduler Error: {d['name']}")
