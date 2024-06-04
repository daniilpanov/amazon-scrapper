let interval_id = setInterval(() => {
    // Limit by the tabs counting
    chrome.tabs.query({}, arr => {
        if (arr.length > 12) {
            return;
        }
        fetch('http://195.201.194.213:8832/tasks/get_available').then((res) => {
            res.json().then((data) => {
                for (let i in data) {
                    switch (data[i].script) {
                        case 'h10':
                            setTimeout(h10scrap, 500, data[i]);
                            break;
                        case 'products':
                            console.log('Will be released soon');
                            break;
                        case 'product_media':
                            console.log('Will be released soon');
                            break;
                        default:
                            console.log('Unknown script:', data[i].script);
                            break;
                    }
                }
            });
        });
    });
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
        'http://195.201.194.213:8832/tasks/acquire/h10/' + task.taskHeader._id.$oid + '/' + task._id.$oid,
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
                    files: ['tasks/h10task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
        });
    });
}