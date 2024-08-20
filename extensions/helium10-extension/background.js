chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        }
    }
});


chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    let res = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/h10/' + message.header_id + '/' + message.task_id,
        {method: 'post'},
    )
    if (res.status === 200) {
        sendResponse('OK');
        res = await startH10(message);
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
                    errors: [(new Date().toUTCString()) + ' [h10] can\'t send the data'],
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

async function startH10(task) {
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
                chrome.tabs.update(tab.id, {autoDiscardable: false});
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10task.js'],
                });

                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    args: [task],
                    func: (task) => {
                        runH10Task(task);
                    },
                });
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[1],
            }, (tab) => {
                chrome.tabs.update(tab.id, {autoDiscardable: false});
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10product-task.js'],
                });

                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    args: [task._id],
                    func: (task_id) => {
                        runProductTask(task_id);
                    },
                });
            });
            chrome.tabs.create({
                url: 'https://www.amazon.com/dp/' + task.data.asins[0],
            }, (tab) => {
                chrome.tabs.update(tab.id, {autoDiscardable: false});
                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    files: ['helper.js', 'tasks/h10target-product-task.js'],
                });

                chrome.scripting.executeScript({
                    target: {tabId: tab.id},
                    args: [task._id],
                    func: (task_id) => {
                        runTargetProductTask(task_id);
                    },
                });
            });
        });
    });
}
