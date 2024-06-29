
function sendMessageToTab(tabId, message, retryDelay = 500, maxRetries = 100) {
    let attempts = 0;

    function sendMessage() {
        ++attempts;
        chrome.tabs.sendMessage(tabId, message, function(response) {
            if (chrome.runtime.lastError) {
                if (attempts < maxRetries) {
                    // console.error(`Ошибка при отправке сообщения: ${chrome.runtime.lastError.message}. Повторная попытка ${attempts} из ${maxRetries}...`);
                    setTimeout(sendMessage, retryDelay);
                } else {
                    console.error(`Не удалось отправить сообщение после ${maxRetries} попыток.`);
                }
            } else {
                // console.log('Сообщение отправлено успешно:', response);
            }
        });
    }

    sendMessage();
}

function h10scrap(task) {
    fetch(
        'http://195.201.194.213:8832/tasks/acquire/h10/' + task.taskHeader._id + '/' + task._id,
        {method: 'post'},
    ).then((res) => {
        if (res.status !== 200) {
            if (res.status === 409) {
                // console.log('This task is busy');
            } else {
                console.error('Error when try to acquire task:', res.statusText);
            }
            return;
        }
        res.json().then((data) => {
            chrome.tabs.create({
                url: 'https://members.helium10.com/cerebro/?accountId=1545531519',
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[0],
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10product-task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
        });
    });
}


let interval_id, self, tabs_limit = ((await chrome.tabs.query({})).length || 2) + 10, curr_limit = tabs_limit;
(async () => {
    self = await chrome.management.getSelf();
    const main = async () => {
        // Limit by the tabs counting
        let tabs_count = (await chrome.tabs.query({})).length;
        if (tabs_count >= tabs_limit) {
            return;
        }
        curr_limit = tabs_limit - tabs_count;
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available');
        const data = await res.json();
        let all_extensions, found;
        for (let i in data) {
            if (curr_limit <= 0) {
                break;
            }
            switch (data[i].script) {
                case 'h10':
                    setTimeout(h10scrap, 500, data[i]);
                    --curr_limit;
                    break;
                case 'products':
                    all_extensions = await chrome.management.getAll();
                    found = false;
                    all_extensions.forEach((async (ext) => {
                        if (ext.name.toLowerCase().includes('amazon products scraper')) {
                            found = true;
                            const msg = await chrome.runtime.sendMessage(ext.id, {root: self, task: data[i]});
                            console.log('Message sent to', ext.name, `[${ext.id}]`);
                            switch (msg) {
                                case 'OK':
                                    console.log('task started:', data[i]);
                                    --curr_limit;
                                    break;
                                case 'fail':
                                    console.log('task can not be started due to unknown error:', data[i]);
                                    break;
                                case 'busy':
                                    console.log('task is busy:', data[i]);
                                    break;
                            }
                        }
                    }));
                    if (!found) {
                        console.log('No extensions found for script products!');
                    }
                    break;
                case 'bsr':
                    if ((data[i].stage || 0) >= 2) {
                        break;
                    }
                    all_extensions = await chrome.management.getAll();
                    found = false;
                    all_extensions.forEach(ext => {
                        if (ext.name.toLowerCase().includes('amazon bsr scraper')) {
                            found = true;
                            chrome.runtime.sendMessage(ext.id, {root: self, task: data[i]}, (res) => {
                                switch (res) {
                                    case 'OK':
                                        console.log('task started:', data[i]);
                                        --curr_limit;
                                        break;
                                    case 'fail':
                                        console.log('task can not be started due to unknown error:', data[i]);
                                        break;
                                    case 'busy':
                                        console.log('task is busy:', data[i]);
                                        break;
                                }
                            })
                            console.log('Message sent to', ext.name, `[${ext.id}]`);
                        }
                    });
                    if (!found) {
                        console.log('No extensions found for script BSR!');
                    }
                    break;
                default:
                    console.log('Unknown script:', data[i].script);
                    break;
            }
        }
        interval_id = setTimeout(main, 10000);
    };
    await main();
})();