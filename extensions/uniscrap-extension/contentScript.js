
function sendMessageToTab(tabId, message, retryDelay = 500, maxRetries = 100) {
    let attempts = 0;

    function sendMessage() {
        ++attempts;
        chrome.tabs.sendMessage(tabId, message, () => {
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

async function h10scrap(task) {
    const res = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/h10/' + task.taskHeader._id + '/' + task._id,
        {method: 'post'},
    );
    if (res.status !== 200) {
        if (res.status === 409) {
            // console.log('This task is busy');
        } else {
            console.error('Error when try to acquire task:', res.statusText);
        }
        return;
    }
    chrome.tabs.create({
        url: 'https://members.helium10.com/cerebro/?accountId=1545531519',
    }, (tab) => {
        chrome.tabs.update(tab.id, {autoDiscardable: false});
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['helper.js', 'tasks/h10task.js'],
        });

        sendMessageToTab(tab.id, task);
    });
    chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + task.data.asins[1],
    }, (tab) => {
        chrome.tabs.update(tab.id, {autoDiscardable: false});
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['helper.js', 'tasks/h10product-task.js'],
        });

        sendMessageToTab(tab.id, task);
    });
    chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + task.data.asins[0],
    }, (tab) => {
        chrome.tabs.update(tab.id, {autoDiscardable: false});
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['helper.js', 'tasks/h10target-product-task.js'],
        });

        sendMessageToTab(tab.id, task);
    });
}


async function sendTask(ext_name, data, script) {
    const all_extensions = await chrome.management.getAll();
    let found = false;
    let tabs = 0;
    for (const ext of all_extensions) {
        if (ext.name.toLowerCase().includes(ext_name)) {
            found = true;
            const msg = await chrome.runtime.sendMessage(ext.id, data);
            console.log('Message sent to', ext.name, `[${ext.id}]`);
            switch (msg) {
                case 'OK':
                    console.log('task started:', data);
                    ++tabs;
                    break;
                case 'fail':
                    console.log('task can not be started due to unknown error:', data);
                    break;
                case 'busy':
                    console.log('task is busy:', data);
                    break;
            }
        }
    }
    if (!found) {
        console.log('No extensions found for script', script);
    }
    return tabs;
}


let interval_id, self, tabs_limit = ((await chrome.tabs.query({})).length || 2) + 10, curr_limit = tabs_limit;
self = await chrome.management.getSelf();
async function main() {
    // Limit by the tabs counting
    let tabs = await chrome.tabs.query({});
    let is_finished;
    for (const tab of tabs) {
        is_finished = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: () => {
                return window.finish_collecting || false;
            },
        });
        if (is_finished[0]?.result) {
            await chrome.tabs.remove(tab.id);
        }
    }
    tabs = await chrome.tabs.query({});
    let tabs_count = tabs.length;
    if (tabs_count >= tabs_limit) {
        console.log('exit from function! limit!', tabs_limit, tabs_count);
        return interval_id = setTimeout(main, 10000);
    }
    curr_limit = tabs_limit - tabs_count;
    try {
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available');
        const data = await res.json();
        for (let i in data) {
            console.log('Available space left:', curr_limit, '; limit & count:', tabs_limit, tabs_count);
            if (curr_limit <= 0) {
                console.log('exit from cycle! limit!');
                break;
            }
            switch (data[i].script) {
                case '100asins':
                    curr_limit -= await sendTask('amazon 100 asins scraper', {...data[i].data, task_id: data[i]._id, header_id: data[i].header_id}, '100asins')
                    break;
                case 'h10':
                    setTimeout(h10scrap, 500, data[i]);
                    --curr_limit;
                    console.log('h10:', curr_limit, tabs_limit, tabs_count);
                    break;
                case 'products':
                    curr_limit -= await sendTask('amazon products scraper', {root: self, task: data[i]}, 'products')
                    break;
                case 'bsr':
                    if ((data[i].stage || 0) >= 2) {
                        break;
                    }
                    curr_limit -= await sendTask('amazon bsr scraper', {root: self, task: data[i]}, 'bsr')
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

await main();