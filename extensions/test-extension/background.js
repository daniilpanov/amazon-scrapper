chrome.tabs.create({url: 'http://195.201.194.213:8830/cp'}, (tab) => {
    chrome.scripting.executeScript({
        target: {tabId: tab.id},
        files: ['tasks/test-task.js'],
    });
});
