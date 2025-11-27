import json
from google.cloud import bigquery
from google.oauth2 import service_account
import frappe

def get_settings():
    return frappe.get_single("BigQuery Settings")

def get_client():
    s = get_settings()
    if not s.credentials_json or not s.project_id or not s.dataset_id:
        frappe.throw("Configure BigQuery Settings (Project ID, Dataset ID, Credentials JSON).")
    info = json.loads(s.credentials_json)
    creds = service_account.Credentials.from_service_account_info(info)
    return bigquery.Client(project=s.project_id, credentials=creds)

def table_id_for(destination_table: str):
    s = get_settings()
    norm = frappe.scrub(destination_table or "frappe_export")
    return f"{s.project_id}.{s.dataset_id}.{norm}"
