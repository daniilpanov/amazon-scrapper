class Scraper {
    constructor() { };

    async getTabHTML(tabId) {
        try {
            const HTML = await chrome.scripting.executeScript({
                target: {
                    tabId: tabId
                },
                func: () => {
                    return document.body.innerHTML;
                }
            });
            return HTML[0].result;
        } catch (error) {
            console.log(error);
        }
    };
}

export default Scraper;