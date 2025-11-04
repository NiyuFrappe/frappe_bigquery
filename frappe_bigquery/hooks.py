app_name = "frappe_bigquery"
app_title = "BigQuery Connector"
app_publisher = "Niyu Labs"
app_description = "Export Frappe/MariaDB data to Google BigQuery"
app_email = "info@niyulabs.com"
app_license = "MIT"

scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "frappe_bigquery.tasks.scheduler.run_due_queries"
        ]
    }
}

app_logo_url = "/assets/frappe_bigquery/bq_icon.svg"
