import json
import os.path


def chunk(s, w=10):
    return set([s[i:i + w] for i in range(0, len(s), w)])


def convert():
    if not os.path.exists('state.json'):
        return
    if not os.path.exists('./states/'):
        os.mkdir('states')
    jsd = json.JSONDecoder()
    with open('state.json') as f:
        data = jsd.decode(f.read())
    statepath = 'states/collect-reviews.state'
    collected_asins = set()
    for asin in data:
        if int(data[asin]) >= 959:
            collected_asins.add(asin)
        else:
            with open(f'states/collect-reviews-{asin}.currstate', 'w') as csf:
                csf.write(str(data[asin]))
    with open(statepath, 'a' if os.path.exists(statepath) else 'w') as sf:
        for asin in collected_asins:
            sf.write(asin)


def get_asin(asin, _type='reviews'):
    if not os.path.exists(f'states/collect-{_type}.state'):
        return False
    with open(f'states/collect-{_type}.state') as sf:
        asins = chunk(sf.read())
    if asin in asins:
        return -1
    if not os.path.exists(f'states/collect-{_type}-{asin}.currstate'):
        return False
    with open(f'states/collect-{_type}-{asin}.currstate') as csf:
        return int(csf.read().strip())


def write_asin(asin, value, _type='reviews'):
    spec_state_path = f'states/collect-{_type}-{asin}.currstate'
    if value >= 959:
        statepath = f'states/collect-{_type}.state'
        with open(statepath, 'a' if os.path.exists(statepath) else 'w') as sf:
            sf.write(asin)
            if os.path.exists(spec_state_path):
                os.remove(spec_state_path)
    else:
        with open(spec_state_path, 'w') as csf:
            csf.write(str(value))


if __name__ == '__main__':
    print(get_asin('B09K4XHTWZ'))
