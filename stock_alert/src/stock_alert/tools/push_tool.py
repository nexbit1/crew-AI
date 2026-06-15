from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


class PushNotification(BaseModel):
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Email body")

class PushNotificationTool(BaseTool):
    name: str = "Send a Push Notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotification

    def _run(self,subject:str, message: str) -> str:
        """ Send out an email with the given subject and HTML body to all sales prospects """
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('EMAIL_SENDER'))
        to_email = To(os.environ.get('EMAIL_RECIEVER'))
        content = Content("text/plain", message)
        mail = Mail(from_email, to_email, subject, content).get()
        sg.client.mail.send.post(request_body=mail)
        return {"status": "success"}