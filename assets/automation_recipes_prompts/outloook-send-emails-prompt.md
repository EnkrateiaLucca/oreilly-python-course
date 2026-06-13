1️⃣ Automating Outlook Table Processing & Sending Emails

Example Prompt:

“Generate a Python script using win32com.client to read the latest email in an Outlook inbox, extract a table from the email body, process the data to extract relevant information (e.g., rows where ‘Status’ is ‘Pending’ and amounts greater than $1,000), and send a summary email to multiple recipients. The script should format the extracted data into an HTML table and send an email with a custom message.”

Additional Requirements for the Script:
	•	The script should use win32com.client to access Outlook emails.
	•	It should identify and extract the latest email containing a table.
	•	Use pandas to parse and filter the table based on business logic (e.g., only extract rows where a certain condition is met).
	•	Format the extracted data as an HTML email.
	•	Send an email to multiple recipients using win32com.client with a customized message.