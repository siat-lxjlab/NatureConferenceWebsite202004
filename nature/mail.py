import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
 
mail_host="smtp.office365.com"
mail_user="neuroengineering@outlook.com"
mail_pass="202004lxj"

sender = 'neuroengineering@outlook.com'

email_from = ["neuroengineering@outlook.com", "technologiesforneuroengineering@outlook.com"]

def send_verify_code(target, content):
    receivers = [target]
    body_content = "Use %s as code for https://technologiesforneuroengineering.cn" %content
    message = MIMEText(body_content, 'plain', 'utf-8')
    message['From'] = "Technologies for Neuroengineering<neuroengineering@outlook.com>"
    message['To'] = "%s<%s>"%("Hi", target)
    subject = """Help change your password"""
    message['Subject'] = Header(subject, 'utf-8')
    smtpObj = smtplib.SMTP(mail_host, 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.set_debuglevel(1)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("Sended successfully!")
    smtpObj.quit()


if __name__ == "__main__":
    receivers = ['1051969307@qq.com', 'bin.yue@siat.ac.cn']
    body_content = """ 测试文本  """
    
    message = MIMEText(body_content, 'plain', 'utf-8')
    message['From'] = "Technologies for Neuroengineering<neuroengineering@outlook.com>"
    message['To'] = "Bin<1051969307@qq.com>"
    subject = """
    测试
    """
    message['Subject'] = Header(subject, 'utf-8')
    smtpObj = smtplib.SMTP(mail_host, 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.set_debuglevel(1)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
    smtpObj.quit()