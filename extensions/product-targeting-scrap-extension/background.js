chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
}, tabs => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'html/control_panel.html',
        }, (tab) => {
            chrome.tabs.update(tab.id, { autoDiscardable: false });
        });
    }
});