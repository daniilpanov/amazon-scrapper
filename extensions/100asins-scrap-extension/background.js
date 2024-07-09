const endpoint = 'http://195.201.194.213:8832/helium/set_100asins'; // заменить

chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    if (message.action === 'START_ASIN_SCRAPING_QUERY') {
        sendResponse('OK');
        await startScraping100ASINS(message.label, message.type, message.task_id, sender.id);
    }
});

async function startScraping100ASINS(label, type, task_id, sender_id) {
    let asinList = new Set();
    label = label.split(' ');
    type = type.split(' ');
    const keywords = [...label, ...type];
    const query = encodeURI(keywords.join(' '));
    let counter = 1;

    const tab = await chrome.tabs.create({
        url: encodeURI(`https://amazon.com/s?k=${query}&page=${counter}`),
        active: false,
    });
    while (asinList.size <= 100) {
        asinList = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            args: [asinList, keywords, label],
            func: (asinList, keywords, label) => {
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
                        if (asinList.size >= 100) {
                            return asinList;
                        }
                        const asin = card.getAttribute('data-asin');
                        const cardDescription = card.querySelector('a.s-underline-text')?.textContent;
                        if (!asin || !cardDescription) {
                            continue;
                        }
                        const brandTitle = card.querySelector('h2 > span')?.textContent;

                        if (check(keywords, cardDescription) && (!brandTitle || check(label, brandTitle))) {
                            asinList.add(asin);
                        }
                    }
                }

                return new Promise((resolve) => {
                    const observer = new MutationObserver((mutationsList, observer) => {
                        for (let mutation of mutationsList) {
                            if (mutation.type === 'childList' || mutation.type === 'subtree') {
                                const appElement = document.querySelector('.s-result-item');
                                if (appElement) {
                                    observer.disconnect();
                                    resolve(scrap(document));
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
                        resolve(scrap(document));
                    }
                });
            }
        });
        await chrome.tabs.remove(tab.id);
    }

    console.log(Array.from(asinList));
    await sendData(Array.from(asinList), task_id, sender_id);
}

async function sendData(data, task_id, sender_id) {
    const sendDelay = 500;
    const maxAttemptsCount = 50;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        try {
            const response = await fetch(`${endpoint}/${task_id}`, {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok && response.status === 200) {
                console.log('Данные отправлены успешно, статус код: ', response.status);
                return;
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
    fetch('http://195.201.194.213:8832/tasks/report/' + task_id, {
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
