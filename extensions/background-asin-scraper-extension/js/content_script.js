const parser = new DOMParser();
const asinList = new Set();
const endpoint = 'http://195.201.194.213:8832/helium/set_100asins'; // заменить

chrome.storage.local.get('queryData', function (result) {
    if (result.queryData) {
        let counter = 1;

        const processTab = async () => {
            if (asinList.size >= 100) {
                console.log(Array.from(asinList));
                await sendData(Array.from(asinList), result.queryData.task_id);
                setTimeout(() => {
                    chrome.runtime.sendMessage({
                        action: 'ASIN_LIST_COMPLETE'
                    });
                }, 3500);

                return;
            }

            chrome.tabs.create({
                url: encodeURI(`https://amazon.com/s?k=${result.queryData.query}&page=${counter}`),
                active: false
            }, function (tab) {
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        return new Promise((resolve) => {
                            const observer = new MutationObserver((mutationsList, observer) => {
                                for (let mutation of mutationsList) {
                                    if (mutation.type === 'childList' || mutation.type === 'subtree') {
                                        const appElement = document.querySelector('.s-result-item');
                                        if (appElement) {
                                            observer.disconnect();
                                            resolve(document.body.innerHTML);
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
                                resolve(document.body.innerHTML);
                            }
                        });
                    }
                }).then((HTML) => {
                    const DOM = parser.parseFromString(HTML[0].result, 'text/html');
                    const productCards = DOM.querySelectorAll('div[data-asin]');
                    for (const card of productCards) {
                        const asin = card.getAttribute('data-asin');
                        const brandTitle = card.querySelector('h2 > span')?.textContent;
                        const cardDescription = card.querySelector('a.s-underline-text')?.textContent;

                        if (brandTitle && brandTitle.toLowerCase().includes(result.queryData.brand) && asin && !asinList.has(asin) && cardDescription) {
                            asinList.add(asin);
                            if (asinList.size > 100) {
                                asinList.delete(asinList.values().next().value);
                            }
                        } else if (asin && cardDescription) {
                            let cardDescriptionCheck = true;
                            for (const keyword of result.queryData.keywords) {
                                if (!cardDescription.toLowerCase().includes(keyword)) {
                                    cardDescriptionCheck = false;
                                    break;
                                }
                            }
                            if (cardDescriptionCheck) {
                                asinList.add(asin);
                                if (asinList.size > 100) {
                                    asinList.delete(asinList.values().next().value);
                                }
                            }
                        }
                    }

                    chrome.tabs.remove(tab.id);

                    counter++;
                    processTab();
                });
            });
        };

        processTab();
    }
});

async function sendData(data, task_id) {
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

            if (response.ok && response.status == 200) {
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
};
