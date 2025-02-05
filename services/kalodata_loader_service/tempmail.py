import requests


class Email:
    def __init__(self, login: str, domain: str, eid: int, sender: str, do_action):
        self.__login = login
        self.__domain = domain
        self.__eid = eid
        self.__sender = sender
        self.do_action = do_action
        self.__data = None

    def fetch_data(self) -> dict:
        try:
            data = self.do_action({"action": "readMessage", "login": self.__login, "domain": self.__domain, "id": self.__eid})

            self.__data = {
                'id': self.__eid,
                'sender': self.__sender,
                'body': data['body'],
                'text': data['textBody'],
                'html': data['htmlBody'],
            }

            return self.__data
        except Exception as e:
            raise Exception(f"Error have occurred while fetching Email[eid={self.__eid}] data") from e


class TempMail:
    def __init__(self):
        self.req_client = requests.session()

        self.email: str = ''
        self.login: str = ''
        self.domain: str = ''

        self.gen_email()

    def gen_email(self) -> None:
        try:
            self.email = self.do_action({"action": 'genRandomMailbox'})[0]
            self.login = self.email.split('@')[0]
            self.domain = self.email.split('@')[1]
        except Exception as e:
            raise Exception('Error have occurred while generating email') from e

    def do_action(self, params: dict):
        return self.req_client.get('https://www.1secmail.com/api/v1/', params=params).json()

    def fetch_emails(self, _from: str | None = None) -> list[Email]:
        try:
            dat = self.do_action({"action": "getMessages", "login": self.login, "domain": self.domain})
            if _from:
                return [Email(self.login, self.domain, ml['id'], ml['from'], self.do_action)
                        for ml in dat if _from in ml['from']]
            return [Email(self.login, self.domain, ml['id'], ml['from'], self.do_action) for ml in dat]
        except Exception as e:
            raise Exception('Error have occurred while fetching emails') from e
