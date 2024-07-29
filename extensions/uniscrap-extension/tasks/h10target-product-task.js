// Wait data
chrome.runtime.onMessage.addListener((task, sender, sendResponse) => {
    sendResponse('OK');  // Success
    waitForElement('#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]', (els, c) => {
        let description = null, title = null, brand = null;

        for (const el_id of ['titleSection', 'title', 'productTitle']) {
            title = document.getElementById(el_id)?.innerText || null;
            if (title) {
                break;
            }
        }

        if (els && els.length) {
            description = els[0]?.innerText || null;
        }

        brand = document.querySelector('.po-brand')?.innerText.split(/\s+/) || null;

        chrome.runtime.sendMessage(
            {
                fetch: [
                    'http://195.201.194.213:8832/helium/set/' + task._id + '/amazon_target',
                    {
                        headers: {
                            // 'Content-Encoding': 'gzip',
                            'Content-Type': 'application/json',
                        },
                        method: 'POST',
                        body: JSON.stringify({
                            title,
                            description,
                            brand,
                        }),
                    },
                ]
            },
            (response) => {
                // Close the window!!!
                window.close();
            },
        );
    });
});
