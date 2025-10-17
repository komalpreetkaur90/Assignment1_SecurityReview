import os
import pymysql
from urllib.request import urlopen
from email.message import EmailMessage
import smtplib

# FIX: OWASP A02: move secrets to env vars, no hardcoded creds
# FIX: OWASP A02: prefer least privilege db user, enable TLS to DB if available
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    # 'ssl': {'ca': '/path/to/ca.pem'}  # optional, db TLS
}

def get_user_input():
    name = input('Enter your name: ')
    # FIX: OWASP A03: basic input validation, trim, simple allowlist
    safe = ''.join(ch for ch in name if ch.isalnum() or ch in " _.'-").strip()
    return safe

def send_email(to, subject, body):
    # FIX: OWASP A03: avoid os.system, command injection risk, use SMTP client
    # FIX: OWASP A02: use TLS if available
    msg = EmailMessage()
    msg['From'] = os.getenv('SMTP_FROM', 'noreply@example.com')
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    host = os.getenv('SMTP_HOST', 'localhost')
    port = int(os.getenv('SMTP_PORT', '25'))
    use_tls = os.getenv('SMTP_TLS', '1') == '1'

    with smtplib.SMTP(host, port, timeout=10) as s:
        if use_tls:
            s.starttls()
        s.send_message(msg)

def get_data():
    # FIX: OWASP A05: use HTTPS not HTTP, add timeout
    url = 'https://secure-api.example/get-data'
    with urlopen(url, timeout=5) as resp:
        data = resp.read().decode('utf-8', 'ignore')
    return data

def save_to_db(data):
    # FIX: OWASP A03: parameterized query, stop string concat
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        # ssl={'ca': '/path/to/ca.pem'}  # optional, db TLS
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mytable (column1, column2) VALUES (%s, %s)",
                (data, 'Another Value')
            )
        connection.commit()
    finally:
        connection.close()

if __name__ == '__main__':
    user_input = get_user_input()
    data = get_data()
    save_to_db(data)
    # NOTE: body comes from user, SMTP path avoids shell injection
    send_email('admin@example.com', 'User Input', user_input)
