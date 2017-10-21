import nexmo
from config import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY


def main():
    client = setup_nexmo()

    call_received = False
    while not call_received:
        response = client.get_calls()
        print(response)
        # response = client.get_call(uuid)


def setup_nexmo():
    return nexmo.Client(application_id=NEXMO_APPLICATION_ID, private_key=NEXMO_PRIVATE_KEY)


main()
