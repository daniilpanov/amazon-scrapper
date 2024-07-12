
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
                // autoDiscardable: false,
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[1],
                // autoDiscardable: false,
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10product-task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[0],
                // autoDiscardable: false,
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10target-product-task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
        });
    });
}


let interval_id, tabs_switching_interval_id, self, tabs_limit = ((await chrome.tabs.query({})).length || 2) + 10, curr_limit = tabs_limit;
self = await chrome.management.getSelf();
async function main() {
    // Limit by the tabs counting
    let tabs_count = (await chrome.tabs.query({})).length;
    if (tabs_count >= tabs_limit) {
        console.log('exit from function! limit!', tabs_limit, tabs_count);
        return;
    }
    curr_limit = tabs_limit - tabs_count;
    try {
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available');
        const data = await res.json();
        let all_extensions, found;
        for (let i in data) {
            console.log('Available space left:', curr_limit, '; limit & count:', tabs_limit, tabs_count);
            if (curr_limit <= 0) {
                console.log('exit from cycle! limit!');
                break;
            }
            switch (data[i].script) {
                case '100asins':
                    all_extensions = await chrome.management.getAll();
                    found = false;
                    all_extensions.forEach((async (ext) => {
                        if (ext.name.toLowerCase().includes('amazon 100 asins scraper')) {
                            found = true;
                            const msg = await chrome.runtime.sendMessage(ext.id, {...data[i].data, task_id: data[i]._id, header_id: data[i].header_id});
                            console.log('Message sent to', ext.name, `[${ext.id}]`);
                            switch (msg) {
                                case 'OK':
                                    console.log('task started:', data[i]);
                                    --curr_limit;
                                    console.log(curr_limit, tabs_limit, tabs_count);
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
                case 'h10':
                    setTimeout(h10scrap, 500, data[i]);
                    --curr_limit;
                    console.log('h10:', curr_limit, tabs_limit, tabs_count);
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
                                    console.log(curr_limit, tabs_limit, tabs_count);
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
                                        console.log(curr_limit, tabs_limit, tabs_count);
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
    } catch (e) {
        console.log(e);
    }
    interval_id = setTimeout(main, 10000);
}

async function switchTabs() {
    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
        await chrome.tabs.switching()
    }
    tabs_switching_interval_id = setTimeout(switchTabs, 30000);
}

await main();