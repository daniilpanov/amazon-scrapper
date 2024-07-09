chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    if (message.action == 'START_ASIN_SCRAPING_QUERY') {
        const query = message.keywords.split(' ').join('+').trim().toLowerCase();
        chrome.storage.local.set({ 'queryData': { query: query, keywords: message.keywords.split(' '), brand: message.brand, task_id: message.task_id } });
        chrome.tabs.query({
            url: 'chrome-extension://' + chrome.runtime.id + 'html/control_panel.html',
        }, (tabs) => {
            if (!tabs || !tabs.length) {
                chrome.tabs.create({
                    url: 'html/work.html',
                    active: false
                }, (tab) => {
                    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
                        if (message.action === 'ASIN_LIST_COMPLETE' && sender.tab.id === tab.id) {
                            chrome.tabs.remove(tab.id);
                        }
                    });
                });
            }
        });
    }
});