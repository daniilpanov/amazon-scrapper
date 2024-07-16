const endpoint = 'http://195.201.194.213:8832/helium/set_100asins';

chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    let res = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/100asins/' + message.header_id + '/' + message.task_id,
        {method: 'post'},
    )
    if (res.status === 200) {
        sendResponse('OK');
        res = await startScraping100ASINS(message.label, message.type, message.task_id, sender.id);
        if (res) {
            fetch(
                'http://195.201.194.213:8832/tasks/finish/' + message.task_id,
                {method: 'PATCH'},
            )
            fetch(
                'http://195.201.194.213:8832/tasks/release/' + message.task_id,
                {method: 'POST'},
            )
        } else {
            fetch('http://195.201.194.213:8832/tasks/report/' + message.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    confirm: true,
                    errors: [(new Date().toUTCString()) + ' [100asins] can\'t send the data'],
                    stop: true,
                }),
            });
        }
    } else if (res.status === 409) {
        sendResponse('busy');
    } else {
        sendResponse('fail');
    }
});

async function startScraping100ASINS(label, type, task_id, sender_id) {
    let asinList = [];
    label = label.split(' ');
    type = type.split(' ');
    const keywords = [...label, ...type];
    const query = keywords.join(' ');
    let counter = 1;
    let tab;

    while (asinList.length < 100) {
        tab = await chrome.tabs.create({
            url: encodeURI(`https://amazon.com/s?k=${query}&page=${counter}`),
            active: false,
        });
        chrome.tabs.update(tab.id, {autoDiscardable: false});
        const result = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            args: [asinList, type, label],
            func: (asinList, type, label) => {
                window.finish_collecting = false;
                function check(kw, str) {
                    str = str.toLowerCase();
                    for (const keyword of kw) {
                        if (!str.includes(keyword)) {
                            return false;
                        }
                    }
                    return true;
                }

                function scrap(document) {
                    const productCards = document.querySelectorAll('div[data-asin]');
                    for (const card of productCards) {
                        if (asinList.length >= 100) {
                            console.log(asinList);
                            return asinList;
                        }
                        const asin = card.getAttribute('data-asin');
                        const cardDescription = card.querySelector('a.s-underline-text')?.textContent;
                        if (!asin || !cardDescription) {
                            continue;
                        }
                        const brandTitle = card.querySelector('h2 > span')?.textContent;

                        if (check(type, cardDescription) && (!brandTitle || check(label, brandTitle))) {
                            asinList.push(asin);
                        }
                    }
                    return asinList;
                }

                return new Promise((resolve) => {
                    const observer = new MutationObserver((mutationsList, observer) => {
                        for (let mutation of mutationsList) {
                            if (mutation.type === 'childList' || mutation.type === 'subtree') {
                                const appElement = document.querySelector('.s-result-item');
                                if (appElement) {
                                    observer.disconnect();
                                    window.finish_collecting = true;
                                    return resolve(scrap(document));
                                }
                            }
                        }
                    });

                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                    });

                    const appElement = document.querySelector('.s-result-item');
                    if (appElement) {
                        observer.disconnect();
                        window.finish_collecting = true;
                        return resolve(scrap(document));
                    }
                });
            }
        });
        console.log(result);
        asinList = result[0]?.result || asinList;
        await chrome.tabs.remove(tab.id);
        ++counter;
        if (!asinList || !asinList.length || counter > 100) {
            break;
        }
    }
    asinList = new Set(asinList);
    console.log(Array.from(asinList));
    return await sendData(Array.from(asinList), task_id, sender_id);
}

async function sendData(asins, task_id, sender_id) {
    const sendDelay = 500;
    const maxAttemptsCount = 50;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        try {
            const response = await fetch(`${endpoint}/${task_id}`, {
                method: 'POST',
                body: JSON.stringify({asins: asins}),
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok && response.status === 200) {
                console.log('Данные отправлены успешно, статус код: ', response.status);
                return true;
            } else {
                throw new Error('Получен статус код: ', response.status)
            }
        } catch (error) {
            attempts++;
            console.log(`Ошибка при отправке данных, новая попытка через: ${sendDelay}ms...`);
            await new Promise(resolve => setTimeout(resolve, sendDelay));
        }
    }

    console.log(`Совершено ${attempts} попыток отправки, что является максимальным количеством.`);
    return false;
}
