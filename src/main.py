from twilio.rest import Client
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
NOTION_API_BASE_URL = 'https://api.notion.com/v1'
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')





# 0
def send_reminder(client: dict):
    """
    This function sends a WhatsApp notification using the Twilio WhatsApp Business API.
    """

    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # This is the Twilio Sandbox number. Don't change it.
    from_whatsapp_number = 'whatsapp:+14155238886',
    to_whatsapp_number = f"whatsapp:{client['phone_number']}"
    body: str = f" {client['name']} is due since {client['due_date']}."

    try:
        twilio_client.messages.create(body=body,
                                      from_=from_whatsapp_number,
                                      to=to_whatsapp_number)
    except:
        print('There was an error sending the message')


# 1
def get_client_details() -> list:
    """
    This function calls the Notion API to get a list of clients that we need to monitor.
    """

    headers: dict = {
        'Authorization': f'Bearer {NOTION_API_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
    }

    # uses <https://developers.notion.com/reference/post-database-query>
    response: Response = requests.post(
        f'{NOTION_API_BASE_URL}/databases/{NOTION_DATABASE_ID}/query', headers=headers)

    if response.status_code == 200:
        json_response: dict = response.json()['results']
    else:
        print("Something went wrong")
        return

    # 2
    clients: list = []
    for item in json_response:
        client: dict = {
            'id': item['id'],
            'name': item['properties']['Assignment Names']['title'][0]['plain_text'],
  
            'due_date': item['properties']['Due Date']['date']['start'],
            'phone_number': item['properties']['Students Number']['phone_number'],
        }
        clients.append(client)

    return clients

# 3
def is_due(due_date: str) -> bool:
    """
    This function checks if the date is due or not.
    """

    today = datetime.today()
    delta = datetime.strptime(due_date, "%Y-%m-%d") - today
    return delta.days == 7 or delta.days == 3 or delta.days == 1 or delta.days < 0

# 4
def main():
    clients: list = get_client_details()
    for client in clients:
        if is_due(client['due_date']):
            print(client)
            send_reminder(client)

if __name__ == '__main__':
    main()
