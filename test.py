import requests


def create_helium_task(asins):
    create_task_endpoint = 'http://195.201.194.213:8832/helium/get'
    res = requests.post(create_task_endpoint, json={'asins': asins})
    if res.status_code != 200:
        raise Exception('Internal Server Error:' + res.text)
    return res.text


if __name__ == '__main__':
    create_helium_task(['B0CV66GQ6Q', 'B000EGH36E'])
