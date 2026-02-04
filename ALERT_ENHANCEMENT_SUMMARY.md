# ✅ Alerting System Enhancements

I have implemented the requested changes to prevent duplicate alerts and allow including log details in messages.

## 1. 🚫 Duplicate Alert Prevention
I implemented a **"Watermark" tracking system**. 
- The system now remembers the last log entry it analyzed for each alert.
- When it runs again, it **only checks logs created since the last run**.
- This ensures that a single log line will trigger exactly **one incident** and **one email**, even if the alert check runs multiple times.

## 2. 📧 Include Log Details in Email
You now have the option to include the matched log content in your alerts.

### How to use:
1.  **Create/Edit Alert:** You will see a new checkbox in the Email and ServiceNow configuration sections.
2.  **Toggle Option:** 
    - ☑ **Checked:** The email/incident will include a "MATCHED LOG DETAILS" section with the timestamp and the actual log message.
    - ☐ **Unchecked:** Only your custom message will be sent.
3.  **User Choice:** This is set per alert, so some alerts can be detailed while others are brief.

---

### Technical Summary:
- **Database:** Added `last_processed_log_id` to `AlertRun` table.
- **Analyzer:** Updated `analyze_logs_for_alert` to use the new watermark logic.
- **UI:** Restored and fixed the mapping for `include_log` checkboxes in Create and Edit templates.
- **Executors:** Updated Email and ServiceNow executors to append log details when the option is selected.

These changes are now active. Please restart your application to ensure all background tasks pick up the new logic!
