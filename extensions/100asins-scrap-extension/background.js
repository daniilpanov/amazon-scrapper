AbortSignal.timeout ??= function timeout(ms) {
    const ctrl = new AbortController();
    setTimeout(() => ctrl.abort(), ms);
    return ctrl.signal;
};

let lastUpdate = Date.now();
const urlList = [
    'https://localhost',
    'http://localhost',
    'https://cp.nyle.ai',
    'http://cp.nyle.ai',
    'https://195.201.194.213',
    'http://195.201.194.213',
];
let currentUrl = urlList[0];

const URL_EXPIRATION_TIME = 5 * 60 * 1000;

async function endp(uri, force = false) {
    if (!force && Date.now() - lastUpdate < URL_EXPIRATION_TIME) {
        return currentUrl + uri;
    }

    for (const url of urlList) {
        try {
            const response = await fetch(url + ':8832/ping', { method: 'GET', signal: AbortSignal.timeout(5000) });
            if (response.ok) {
                currentUrl = new URL(url).origin;
                lastUpdate = Date.now();
                return currentUrl + uri;
            }
        } catch (error) {
        }
    }

    return null;
}

await endp('/ping', true);


chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
}, tabs => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'html/control_panel.html',
        }, tab => {
            chrome.tabs.update(tab.id, { autoDiscardable: false });
        });
    }
});

chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    if (message.stage > 1) {
        sendResponse('Bad task');
        return;
    }
    let res = await fetch(
        await endp(':8832/tasks/acquire/100asins/' + message.header_id + '/' + message.task_id),
        { method: 'post' },
    );
    if (res.status === 200) {
        sendResponse('OK');
        res = await startScraping100ASINS(message.label, message.type, message.limit, message.task_id, sender.id, message.windowId);
        if (!res) {
            fetch(await endp(':8832/tasks/report/' + message.task_id), {
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

async function startScraping100ASINS(label, type, limit, task_id, sender_id, window_id) {
    limit = limit || 100;
    let asinList = [];
    label = label.split(' ');
    type = type.split(' ');
    const keywords = [...label, ...type];
    const query = keywords.join(' ');
    let counter = 1;
    let tab;

    while (asinList.length < limit) {
        tab = await chrome.tabs.create({
            url: encodeURI(`https://amazon.com/s?k=${query}&page=${counter}`),
            active: false,
            windowId: window_id,
        });
        chrome.tabs.update(tab.id, { autoDiscardable: false });
        const result = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            args: [asinList, type, label, limit],
            func: (asinList, type, label, limit) => {
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
                        if (asinList.length >= limit) {
                            console.log(asinList);
                            return asinList;
                        }
                        const asin = card.getAttribute('data-asin');
                        const cardDescription = card.querySelector('a.s-underline-text')?.textContent;
                        if (!asin || !cardDescription) {
                            continue;
                        }
                        const brandTitle = card.querySelector('h2 > span')?.textContent;

                        if (check(type, cardDescription) && (!brandTitle || check(label, brandTitle) || check(label, cardDescription))) {
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
            },
        });
        console.log(result);
        asinList = result[0]?.result || asinList;
        await chrome.tabs.remove(tab.id);
        ++counter;
        if (!asinList || !asinList.length || counter > limit) {
            break;
        }
    }
    asinList = new Set(asinList);
    console.log(Array.from(asinList));
    return await sendData(Array.from(asinList), task_id);
}

async function sendData(asins, task_id) {
    const sendDelay = 10000;
    const maxAttemptsCount = 3;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        const response = await fetch(await endp(':8832/helium/set_100asins/' + task_id)`, {
            method: 'POST',
            body: JSON.stringify({ asins: asins }),
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok && response.status === 200) {
            console.log('Данные отправлены успешно, статус код: ', response.status);
            return true;
        } else {
            console.log('Получен статус код: ', response.status);
            console.log(`Ошибка при отправке данных, новая попытка через: ${sendDelay}ms...`);
            await new Promise(resolve => setTimeout(resolve, sendDelay));
            ++attempts;
        }
    }

    console.log(`Совершено ${attempts} попыток отправки, что является максимальным количеством.`);
    return false;
}
