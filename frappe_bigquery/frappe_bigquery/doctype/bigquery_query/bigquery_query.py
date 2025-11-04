from __future__ import annotations
import json, pandas as pd
import frappe
from frappe.utils import now_datetime
from ...utils.bq import get_client, table_id_for

def _get_columns_for_table(table: str):
    return [r[0] for r in frappe.db.sql("""
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=%s
        ORDER BY ORDINAL_POSITION
    """, (table,))]

def _has_column(table: str, col: str) -> bool:
    return bool(frappe.db.sql("""
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s
    """, (table, col)))

def build_select_sql(doc) -> str:
    if doc.mode == "Custom SQL":
        if not doc.custom_sql or not doc.destination_table:
            frappe.throw("Provide Custom SQL and Destination Table.")
        return doc.custom_sql.strip()
    if not doc.table_name:
        frappe.throw("Please set Table.")
    cols = [c.column_name for c in doc.columns] if getattr(doc, "columns", None) else []
    if not cols:
        cols = _get_columns_for_table(doc.table_name)
    where = []
    if doc.incremental_sync_enabled:
        if _has_column(doc.table_name, "modified"):
            where.append("modified > %(last_sync_ts)s")
        elif _has_column(doc.table_name, "last_update"):
            where.append("last_update > %(last_sync_ts)s")
        elif _has_column(doc.table_name, "write_date"):
            where.append("write_date > %(last_sync_ts)s")
        elif _has_column(doc.table_name, "id"):
            where.append("id > %(last_sync_id)s")
        elif _has_column(doc.table_name, "name"):
            where.append("CAST(name AS UNSIGNED) > %(last_sync_id)s")
    if doc.additional_where:
        where.append("(" + doc.additional_where + ")")
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    cols_sql = ", ".join(f"`{c}`" for c in cols)
    return f"SELECT {cols_sql} FROM `{doc.table_name}`{where_sql}"

def _infer_schema(df: pd.DataFrame):
    from google.cloud import bigquery
    schema = []
    for col, dtype in df.dtypes.items():
        if pd.api.types.is_integer_dtype(dtype):
            ty = bigquery.enums.SqlTypeNames.INTEGER
        elif pd.api.types.is_float_dtype(dtype):
            ty = bigquery.enums.SqlTypeNames.FLOAT
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            ty = bigquery.enums.SqlTypeNames.TIMESTAMP
        elif pd.api.types.is_bool_dtype(dtype):
            ty = bigquery.enums.SqlTypeNames.BOOL
        else:
            ty = bigquery.enums.SqlTypeNames.STRING
        schema.append(bigquery.SchemaField(str(col), ty))
    return schema

def _coerce_json(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        if df[c].dtype == "object":
            if df[c].apply(lambda v: isinstance(v, (dict, list))).any():
                df[c] = df[c].apply(lambda v: json.dumps(v, default=str) if v is not None else None)
    return df

def _sync_markers(df: pd.DataFrame):
    last_ts = None
    last_id = None
    for col in ["modified","last_update","write_date","creation"]:
        if col in df.columns:
            s = pd.to_datetime(df[col], errors="coerce")
            if s.notna().any():
                last_ts = s.max().to_pydatetime()
                break
    for col in ["id","name"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().any():
                last_id = int(s.max())
                break
    return last_ts, last_id

def to_df(sql: str, params: dict) -> pd.DataFrame:
    con = frappe.db.get_connection()
    return pd.read_sql(sql, con, params=params)

def upload(df: pd.DataFrame, dest_table: str):
    from google.cloud import bigquery
    client = get_client()
    table_id = table_id_for(dest_table)
    df = _coerce_json(df)
    job = client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(schema=_infer_schema(df)))
    job.result()
    return job.output_rows

def run_query_for_doc(name: str):
    doc = frappe.get_doc("BigQuery Query", name)
    if doc.is_locked:
        return
    try:
        doc.db_set("is_locked", 1, commit=True)
        params = {"last_sync_ts": doc.last_sync or "1970-01-01 00:00:00", "last_sync_id": doc.last_sync_id or 0}
        sql = build_select_sql(doc)
        df = to_df(sql, params)
        if df.empty:
            doc.db_set("export_complete", 1, commit=True)
            return
        _ = upload(df, doc.destination_table or (doc.table_name or "frappe_export"))
        ts, iid = _sync_markers(df)
        if ts:
            doc.db_set("last_sync", ts, commit=True)
        if iid is not None:
            doc.db_set("last_sync_id", iid, commit=True)
        doc.db_set("export_complete", 1, commit=True)
    finally:
        doc.db_set("is_locked", 0, commit=True)

@frappe.whitelist()
def run_now(docname: str):
    run_query_for_doc(docname)
    return "OK"

@frappe.whitelist()
def get_columns(table_name: str):
    return [r[0] for r in frappe.db.sql("""
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=%s
        ORDER BY ORDINAL_POSITION
    """, (table_name,))]
