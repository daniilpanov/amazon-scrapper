import Scrapper from "./scrapper.js";


const scrapeButton = document.getElementById('toParseButton');
const amazonUrl = 'https://sellercentral.amazon.com/';
const testUrl = 'https://labs.perplexity.ai/';


const scrapper = new Scrapper();

scrapeButton.addEventListener('click', async (event) => {
    scrapeButton.disabled = true;
    scrapeButton.innerHTML = 'Wait...';

    try {
        const tabs = await chrome.tabs.query({ currentWindow: true, active: true }); // Получаю открытые вкладки
        const activeTabUrl = tabs[0].url; // Получаю ссылку активной вкладки 

        try {
            // const HTML = await chrome.scripting.executeScript({
            //     target: {
            //         tabId: tabs[0].id
            //     },
            //     func: () => {
            //         return document.body.innerHTML;
            //     }
            // });
            // const DOM = await scrapper.getTabDOM(tabs[0]);
            // const parser = new DOMParser();
            // const DOM = parser.parseFromString(html, "text/html");

            // console.log(DOM)
            // const h1 = await DOM.();
            // console.log(h1);

        } catch (error) {
            console.log(error);
        }

    } catch (error) {
        console.error(error);
        alert('Error on getting the active tab.');
    } finally {
        scrapeButton.disabled = false;
        scrapeButton.innerHTML = 'Scrape';
    }
})


// if (activeTabUrl.includes(testUrl)) {
//     try {
//         chrome.scripting.executeScript({
//             target: {
//                 tabId: tabs[0].id
//             },
//             func: () => {
//                 console.log(document.body.innerHTML)
//             }
//         })
//     } catch (error) {
//         console.error(error);
//     }
// } else {
//     alert(`Wrong URL! It must starts with\n${testUrl}*`);
//     console.log(123);
// }