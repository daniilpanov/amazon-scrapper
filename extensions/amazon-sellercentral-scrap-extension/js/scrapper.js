class Scrapper {
    constructor() { };

    async getTabDOM(tab) {
        try {
            const DOM = await chrome.scripting.executeScript({
                target: {
                    tabId: tab.id
                },
                func: () => {
                    return document.body.cloneNode(true);
                }
            });
            return DOM[0].result; // .cloneNode() возвращает массив, поэтому такой ретёрн
        } catch (error) {
            console.log(error);
        }
    };
}

export default Scrapper;