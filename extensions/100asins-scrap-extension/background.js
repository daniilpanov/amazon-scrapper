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
            console.log(error);
        }
    }

    return null;
}

endp(':8832/ping', true).then(res => {
    console.log('URL:', res);
    if (!res) {
        console.log('Error! No endpoints found!');
        return;
    }
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

    chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
        sendResponse('OK');
        run(message, sender, sendResponse);
    });

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        sendResponse('OK');
        run(message, sender, sendResponse);
    });
});

async function run(message, sender, sendResponse) {
    if (message.stage > 1) {
        console.error('Bad task');
        return;
    }
    let res = await fetch(
        await endp(':8832/tasks/acquire/100asins/' + message.header_id + '/' + message.task_id),
        { method: 'post' },
    );
    if (res.status === 200) {
        res = await startScraping100ASINS(message.label, message.type, message.limit, message.task_id, sender.id, message.windowId, (message?.stage || 0) <= 0);
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
        console.error('busy');
    } else {
        console.error('fail');
    }
}


async function startScraping100ASINS(label, type, limit, task_id, sender_id, window_id, helium = true) {
    limit = limit || 100;
    let asinList = new Set();
    let countAsins = 0;
    let resData = [];
    label = label.split(' ');
    type = type.split(' ');
    const keywords = [...label, ...type];
    const query = keywords.join(' ');
    let counter = 1;
    let tab;

    while (counter <= limit) {
        tab = await chrome.tabs.create({
            url: encodeURI(`https://amazon.com/s?k=${query}&page=${counter}`),
            active: false,
            windowId: window_id,
        });
        chrome.tabs.update(tab.id, { autoDiscardable: false });
        let result = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            args: [counter, type, label, limit, !helium],
            func: (counter, type, label, limit, returnAllData = false) => {
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
                    const res = new Set();
                    const resData = [];
                    const productCards = document.querySelectorAll('div[data-asin]');
                    for (const card of productCards) {
                        if (!card) continue;

                        if (counter > limit) {
                            return returnAllData ? [[], []] : [];
                        }

                        const asin = card.getAttribute('data-asin');
                        const cardDescription = card.querySelector('a.s-underline-text')?.textContent;
                        if (!asin || !cardDescription) continue;

                        const score = Number(card.querySelector('a i span')?.textContent.trim().split(' ')[0] || 0) || null;
                        let image = card.getElementsByTagName('img')[0]?.getAttribute('src') || null;
                        if (image) {
                            const splitImageUrl = image.split('/');
                            let imageUriName = splitImageUrl[splitImageUrl.length - 1];
                            // Make it universal (remove size spec)
                            const imageUriNameParts = imageUriName.split('.');
                            imageUriName = imageUriNameParts.slice(0, -2).join('.') + '.' + imageUriNameParts[imageUriNameParts.length - 1];
                            image = splitImageUrl.slice(0, -1).join('/') + '/' + imageUriName;
                        }
                        const brandTitle = card.querySelector('h2 > span')?.textContent;
                        const priceEls = card.querySelector('[data-cy="secondary-offer-recipe"]')?.children[0]?.children || [];
                        let price = null;
                        for (const priceEl of priceEls) {
                            const text = priceEl.textContent.trim();
                            if (text.startsWith('$')) {
                                price = Number(text.slice(1));
                            }
                        }

                        const oldLength = res.size;
                        if (returnAllData || check(type, cardDescription) && (!brandTitle || check(label, brandTitle) || check(label, cardDescription))) {
                            res.add(asin);
                        }
                        if (oldLength < res.size) {
                            resData.push({
                                asin,
                                title: brandTitle,
                                score,
                                image,
                                price,
                            });
                        }
                    }
                    return returnAllData ? [Array.from(res), resData] : Array.from(res);
                }

                const appElement = document.querySelector('.s-result-item');
                if (appElement) {
                    window.finish_collecting = true;
                    return scrap(document);
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
                });
            },
        });
        result = result[0]?.result || (helium ? [] : [[], []]);
        if (result) {
            if (helium)
                asinList = asinList.union(new Set(result));
            else {
                asinList = asinList.union(new Set(result[0]));
                resData = [...resData, ...result[1]];
            }
        }
        await chrome.tabs.remove(tab.id);
        ++counter;
        countAsins = asinList.size;
        if (!result || !result.length) {
            break;
        }
    }
    asinList = Array.from(asinList);
    return helium ? await sendData(asinList, task_id) : await sendUsualData(resData, task_id);
}

async function sendUsualData(data, task_id) {
    const sendDelay = 10000;
    const maxAttemptsCount = 3;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        const response = await fetch(await endp(':8832/tasks/stage/' + task_id), {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'PATCH',
            body: JSON.stringify({
                release: true,
                stage: 2,
                result: data,
            }),
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

async function sendData(asins, task_id) {
    const sendDelay = 10000;
    const maxAttemptsCount = 3;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        const response = await fetch(await endp(':8832/helium/set_100asins/' + task_id), {
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
