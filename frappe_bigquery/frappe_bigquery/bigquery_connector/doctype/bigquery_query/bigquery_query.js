frappe.ui.form.on("BigQuery Query", {
  refresh(frm) {
    // Button: Run Export Now
    if (!frm.is_new()) {
      frm
        .add_custom_button(__("Run Export Now"), () => {
          frappe.call({
            method:
              "frappe_bigquery.bigquery_connector.doctype.bigquery_query.bigquery_query.run_now",
            args: { docname: frm.doc.name },
            callback: () => {
              frappe.show_alert({
                message: __("Export started"),
                indicator: "green",
              });
            },
          });
        })
        .addClass("btn-primary");
    }

    // Button: Get Columns
    frm.add_custom_button(__("Get Columns"), () => {
      if (!frm.doc.table_name) {
        frappe.msgprint(__("Set Table first."));
        return;
      }

      frappe.call({
        method:
          "frappe_bigquery.bigquery_connector.doctype.bigquery_query.bigquery_query.get_columns",
        args: { table_name: frm.doc.table_name },
        callback: (r) => {
          const cols = r.message || [];

          frm.clear_table("columns");
          cols.forEach((c) => {
            const row = frm.add_child("columns");
            row.column_name = c;
          });
          frm.refresh_field("columns");

          frappe.show_alert({
            message: __(`Loaded ${cols.length} columns`),
            indicator: "green",
          });

          if (!frm.doc.destination_table && frm.doc.table_name) {
            frm.set_value(
              "destination_table",
              (frm.doc.table_name || "")
                .replace(/`/g, "")
                .replace(/\W+/g, "_")
            );
          }
        },
      });
    });

    // Auto-suggest destination table
    if (!frm.doc.destination_table && frm.doc.table_name) {
      frm.set_value(
        "destination_table",
        (frm.doc.table_name || "").replace(/`/g, "").replace(/\W+/g, "_")
      );
    }
  },

  table_name(frm) {
    if (!frm.doc.destination_table && frm.doc.table_name) {
      frm.set_value(
        "destination_table",
        (frm.doc.table_name || "").replace(/`/g, "").replace(/\W+/g, "_")
      );
    }
  },
});
