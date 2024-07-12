const endpoint = 'http://195.201.194.213:8832/helium/set';

chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    let res = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/h10/' + message.header_id + '/' + message.task_id,
        {method: 'post'},
    )
    if (res.status === 200) {
        sendResponse('OK');
        res = await startH10(message.asins);
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

async function startH10(asins) {
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
                url: 'https://www.amazon.com/dp/' + task.data.asins[1],
            }, (tab) => {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10product-task.js'],
                });

                sendMessageToTab(tab.id, task);
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[0],
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
