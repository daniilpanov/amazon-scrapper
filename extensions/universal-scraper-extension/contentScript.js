let interval_id, self;
(async () => {
    self = await chrome.management.getSelf();
    interval_id = setInterval(async () => {
        // Limit by the tabs counting
        const tabs = await chrome.tabs.query({});
        if (tabs.length > 12) {
            // return;
        }
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available');
        const data = await res.json();
        for (let i in data) {
            switch (data[i].script) {
                case 'h10':
                    setTimeout(h10scrap, 500, data[i]);
                    break;
                case 'products':
                    const all_extensions = await chrome.management.getAll();
                    let found = false;
                    all_extensions.forEach(ext => {
                        if (ext.name.toLowerCase().includes('amazon products scraper')) {
                            found = true;
                            chrome.runtime.sendMessage(ext.id, {root: self, task: data[i]}, (res) => {
                                switch (res) {
                                    case 'OK':
                                        console.log('task started:', data[i]);
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
                        console.log('No extensions found for script products!');
                    }
                    break;
                default:
                    console.log('Unknown script:', data[i].script);
                    break;
            }
        }
    }, 10000);

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
})()