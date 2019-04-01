import smtplib
import email.mime.multipart
import email.mime.text


def send_email(content=''):
    """
    发送邮件
    :param SMTP_host: smtp.163.com
    :param from_addr: 发送地址：xxx@163.com
    :param password: 密码: password
    :param to_addrs: 发送给谁的邮箱： xxx@qq.com
    :param subject:  邮件主题： test
    :param content:  邮件内容： test
    :return: None
    """

    # 发送邮箱smtp服务器地址
    SMTP_host = 'smtp.163.com'
    # 发送邮箱账户
    from_addr = ''
    # 发送邮箱账户密码
    password = ''
    # 收件人邮箱地址
    to_addrs = 'chengjiwen@fangjia.com'
    # 右键主题
    subject = '～～～～～～爬虫挂了～～～～～～'

    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = from_addr
    msg['to'] = to_addrs
    msg['subject'] = subject
    # content = content + '\n状态异常'
    txt = email.mime.text.MIMEText('大众点评')
    msg.attach(txt)

    smtp = smtplib.SMTP()
    smtp.connect(SMTP_host, '25')
    smtp.login(from_addr, password)
    smtp.sendmail(from_addr, to_addrs, str(msg))
    smtp.quit()


if __name__ == '__main__':
    send_email()
