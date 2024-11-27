let needle_tab_id = null;

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (needle_tab_id !== tabId) {
        return;
    }
    console.log('needle tab:', tabId);
    if (changeInfo.status === 'complete') {
        console.log('completed!', tabId)
        chrome.scripting.executeScript({
            target: {tabId: tabId, allFrames: false},
            func: (function () {
                console.log('hello!');
                setTimeout(() => {
                    // Send data
                    fetch('http://localhost:8895/agencies/clutchio', {
                        method: 'POST',
                        mode: 'no-cors',
                        headers: {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': '*',
                            'Content-Type': 'text/html',
                        },
                        body: document.body.innerHTML,
                    }).then((resp) => {
                        console.log('Success!');
                        console.log(resp);
                        // Pagination
                        const nav = document.getElementById('pagination-nav');
                        const next_page_el = nav.querySelector('.page-item.next a');
                        if (!next_page_el) {
                            fetch('http://localhost:8895/agencies/clutchio/end', {
                                method: 'POST',
                                mode: 'no-cors',
                                headers: {
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': '*',
                                },
                            }).then(r => {
                                console.log('Ended!');
                            });
                            return;
                        }
                        next_page_el.click();
                    }).catch(reason => {
                        console.error('Error when sending data!');
                        console.error(reason);
                    });
                }, 1500);
            }),
        });
    }
});

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    needle_tab_id = message;
});
