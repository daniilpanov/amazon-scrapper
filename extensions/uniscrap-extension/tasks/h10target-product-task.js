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

        const raw_brand = document.querySelector('.po-brand')?.innerText.split(/\s+/) || null;
        if (raw_brand && raw_brand.length) {
            for (const i in raw_brand) {
                const next = Number(i) + 1;
                if (raw_brand[i].toLowerCase() === 'brand' && next < raw_brand.length) {
                    brand = raw_brand[next];
                    break;
                }
            }
        }

        console.log(chrome.runtime.sendMessage(
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
        ));
    });
});
