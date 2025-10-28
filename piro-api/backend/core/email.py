import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.config import Settings
from logger import logger


class Email:
    """
        Class for sending emails.

    Thin wrapper around the smtplib and email.mime built-in libraries.

    Example Usage:

    HTML_BODY = ''' <html> <body> <h1>Testing sending emails from the
    servers</h1> <p>Please ignore; just testing. This text <em>can</em> be
    <strong>formatted</strong>.</p> <img src="cid:per_day"> </body> </html> '''

    email = Email(
        from_address="<some email address>",
        subject="Example of sending emails from the server.",
        html_body=HTML_BODY,
    )

    # standard attachment
    email.add_attachment(
        # pylint: disable=line-too-long
        path_to_file="/srv/magic/cbp-home/app/static/access/img
        /slack_postings/cBioPortal_Usage_Report.pdf",
        file_display_name="cBioPortal_Usage_Report.pdf",
    )

    # image embedded in body of email.
    email.add_attachment(
        path_to_file="/srv/magic/cbp-home/app/static/access/img
        /slack_postings/per_day.png",
        file_display_name="per_day.png",
        extra_headers={"Content-ID": "<per_day>"},
    )

    email.send(
        to=('"Smith, John" <some email address>',),
        cc=("<some email address>",),
        bcc=("<some email address>",),
    )
    """

    def __init__(self, subject: str, html_body: str):
        self.email_server_hostname = Settings.EMAIL_SMTP_SERVER
        self.email = MIMEMultipart()
        self.from_address = Settings.EMAIL_FROM
        self.email["From"] = Settings.EMAIL_FROM
        self.email["Subject"] = subject
        self.email.attach(MIMEText(html_body, "html"))

    def add_attachment(
        self, path_to_file, file_display_name, extra_headers=None
    ):
        """
            Attach the specified filename to the email.

        Among other things, the 'extra_headers' attribute can be used to
        embed images into the body of the email.  Add HTML like "<img
        src='cid:image_name'>" and submit a dict containing {'Content-ID':
        '<image_name>'} to embed the image (note that the angle brackets in
        the dict are required).
        """
        with open(path_to_file, "rb") as the_file:
            file_attachment = MIMEApplication(the_file.read())
        # Add a header for the attachment
        file_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_display_name}",
        )

        # Define extra headers for the attachment.
        # Can be used for embedding images into HTML.
        if extra_headers is not None:
            for name, value in extra_headers.items():
                file_attachment.add_header(name, value)

        # Attach the file to the message
        self.email.attach(file_attachment)

    def send(
        self,
        to: str,
        cc: str,
        bcc: str,
    ):
        """
        Send an email.
        """
        # Try to log in to server and send email
        try:
            if to:
                self.email["To"] = to
                recipients = to
            else:
                to = ""
            if cc:
                self.email["Cc"] = cc
                if recipients != "" and recipients.endswith(",") is False:
                    recipients = recipients + "," + cc
                else:
                    recipients = recipients + cc
            else:
                cc = ""
            if bcc:
                self.email["Bcc"] = bcc
                if recipients != "" and recipients.endswith(",") is False:
                    recipients = recipients + "," + bcc
                else:
                    recipients = recipients + bcc
            else:
                bcc = ""

            smtp_obj = smtplib.SMTP(self.email_server_hostname)
            smtp_obj.sendmail(
                self.from_address,
                recipients.split(","),
                self.email.as_string(),
            )
        except Exception as exc:
            # Print any error messages to stdout
            logger.error(f"Send Email " f"<{str(exc)} : {exc.args}>")
        finally:
            smtp_obj.quit()
