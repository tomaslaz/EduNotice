"""
Email sending module
"""

import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail, Personalization

from edunotice.constants import(
    SG_FROM_EMAIL,
    SG_SUMMARY_RECIPIENTS,
    SG_API_KEY,
    SG_TEST_EMAIL,
    SG_TEST_FROM,
    SG_TEST_TO,
)

SG_CLIENT = sendgrid.SendGridAPIClient(api_key=SG_API_KEY)


def _prep_to_list(to):
    """
    Prepares a list of unique recipients

    Arguments:
        to - comma separated list of recipients
    Return:
        to_list - unique list of recipients
    """

    if type(to) is list:
        to_arr = to
    elif to is None:
        return []
    else:
        to_arr = [x.strip() for x in to.split(',')]

    to_arr = list(set(to_arr)) # making sure that values are unique
    
    to_list = [] 
    for to_arr_el in to_arr:
        to_list.append(To(to_arr_el))

    return to_list


def send_email(to, subject, html_content):
    """
    A function to send an email

    Arguments:
        to - email receivers (comma separated)
        subject - email subject
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """ 

    # if we are testing functionality - ovewrite from/to
    if SG_TEST_EMAIL:
        print("!!! SendGrid TEST Mode. Overwriting from/to !!!")
        
        from_email = Email(SG_TEST_FROM)
        to_emails =  _prep_to_list(SG_TEST_TO)
    else:
        from_email = Email(SG_FROM_EMAIL)
        to_emails =  _prep_to_list(to)

    if len(to_emails) == 0:
        return False, "Empty recipient list"
    
    content = Content("text/html", html_content)

    mail = Mail(from_email=from_email, to_emails=to_emails, subject=subject, html_content=content)

    response = SG_CLIENT.client.mail.send.post(request_body=mail.get())

    success = str(response.status_code).startswith("2")

    return success, response.status_code


def send_summary_email(html_content, upd_timestamp):
    """
    Sends a summary email

    Arguments:
        upd_timestamp - timestamp when eduhub data has been updated
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    subject = "EduHub Activity Update (%s UTC)" % (upd_timestamp.strftime("%Y-%m-%d %H:%M"))
    
    success, error = send_email(SG_SUMMARY_RECIPIENTS, subject, html_content)

    return success, error