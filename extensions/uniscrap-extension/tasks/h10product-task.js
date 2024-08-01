// Wait data
chrome.runtime.onMessage.addListener((task, sender, sendResponse) => {
    sendResponse('OK');  // Success
    waitForElement('#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]', (els, c) => {
        let variation = {}, characteristics = {}, about = [], manufacturer = null;

        const variation_cont = (typeof twisterContainer === 'undefined' ? null : twisterContainer.querySelector('[id^=variation_]'));
        if (variation_cont) {
            const vari = variation_cont.innerText.trim().split('\n')[0].split(':');
            if (vari.length && vari.length > 1) {
                variation[vari[0].trim()] = vari[1].trim();
            }
        }
        if (typeof productOverview_feature_div !== 'undefined') {
            const trs = productOverview_feature_div.getElementsByTagName('tr');
            for (const tr of trs) {
                const cells = tr.getElementsByTagName('td');
                if (cells.length && cells.length > 1) {
                    characteristics[cells[0].innerText.trim()] = cells[1].innerText.trim();
                }
            }
        }
        if (typeof featurebullets_feature_div !== 'undefined') {
            const list = featurebullets_feature_div.getElementsByTagName('ul');
            if (list.length && list.length > 0) {
                const items = list[0].getElementsByTagName('li');
                for (const item of items) {
                    about.push(item.innerText);
                }
            }
        }
        let aplus_content = null;
        if (typeof aplus !== 'undefined' || typeof aplus_feature_div !== 'undefined') {
            aplus_content = (typeof aplus === 'undefined' ? aplus_feature_div : aplus)?.innerHTML?.trim();
        }
        if (!aplus_content && typeof productDescription_feature_div !== 'undefined') {
            if (typeof productDescription !== 'undefined') {
                aplus_content = productDescription?.innerHTML?.trim();
            } else {
                aplus_content = productDescription_feature_div.innerHTML?.trim();
            }
        }
        if (typeof detailBulletsWithExceptions_feature_div !== 'undefined') {
            const uls = detailBulletsWithExceptions_feature_div.getElementsByTagName('ul');
            if (uls.length) {
                for (const item of uls[0].getElementsByTagName('li')) {
                    const key_val = item.innerText.split(':');
                    if (key_val[0].trim() === 'Manufacturer') {
                        manufacturer = key_val[1].trim();
                        break;
                    }
                }
            }
        } else if (typeof productDetails_feature_div !== 'undefined') {
            const tables = productDetails_feature_div.getElementsByTagName('table');
            if (tables.length) {
                for (const item of tables[0].getElementsByTagName('tr')) {
                    const key_val = item.innerText.split('\t');
                    if (key_val[0].trim() === 'Manufacturer') {
                        manufacturer = key_val[1].trim();
                        break;
                    }
                }
            }
        }

        chrome.runtime.sendMessage(
            {
                fetch: [
                    'http://195.201.194.213:8832/helium/set/' + task._id + '/amazon',
                    {
                        headers: {
                            // 'Content-Encoding': 'gzip',
                            'Content-Type': 'application/json',
                        },
                        method: 'POST',
                        body: JSON.stringify({
                            characteristics: characteristics,
                            about: about,
                            variant: variation,
                            aplus: aplus_content,
                            manufacturer: manufacturer,
                        }),
                    },
                ]
            },
            (response) => {
                // Close the window!!!
                window.close();
            },
        );
    }, c => {
        if (c > 10) {
            window.close();
            return true;
        }
        return false;
    });
});