import base64
import logging
import os
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/report", tags=["reporting"])
logger = logging.getLogger("reporting.email")


class SendEmailReportRequest(BaseModel):
    user_id: str
    to_email: str
    subject: str = "Fluid Guardian Intake Report"
    body: str = ""
    pdf_base64: str | None = None
    filename: str = "fluid_intake_report.pdf"


@router.post("/send-email")
def send_email_report(req: SendEmailReportRequest) -> dict:
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user or "reports@fluidguardian.com")

    if smtp_host:
        try:
            msg = EmailMessage()
            msg["Subject"] = req.subject
            msg["From"] = smtp_from
            msg["To"] = req.to_email
            msg.set_content(req.body or "Please find attached your Fluid Guardian intake report.")

            if req.pdf_base64:
                pdf_bytes = base64.b64decode(req.pdf_base64)
                msg.add_attachment(
                    pdf_bytes,
                    maintype="application",
                    subtype="pdf",
                    filename=req.filename,
                )

            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)

            return {
                "status": "success",
                "sent": True,
                "recipient": req.to_email,
                "message": f"Report successfully emailed to {req.to_email}.",
            }
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send email via SMTP: {str(e)}")
    else:
        logger.info(
            f"[Simulated Email] Emailed report to {req.to_email} with subject '{req.subject}'. "
            f"PDF attachment: {req.filename} ({len(req.pdf_base64) if req.pdf_base64 else 0} bytes base64)."
        )
        return {
            "status": "success",
            "sent": True,
            "simulated": True,
            "recipient": req.to_email,
            "message": f"Report successfully sent to {req.to_email} (Simulated).",
        }
