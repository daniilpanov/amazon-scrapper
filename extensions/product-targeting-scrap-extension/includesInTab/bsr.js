class BSRMultiParser extends MultiParser {
    elementsQuerySelector = 'div.a-cardui[id*="asin-index"]';
    ASINsList = [];

    findASINsList() {
        if (this.ASINsList && this.ASINsList.length) {
            return this.ASINsList;
        }
        const element = document.querySelector('[data-client-recs-list]');
        if (!element) {
            return [];
        }
        try {
            const data = JSON.parse(element.getAttribute('data-client-recs-list'));
            const res = [];
            for (const item of data) {
                res.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) });
            }
            return (this.ASINsList = res);
        } catch (e) {
            return [];
        }
    }

    collectASINsCards() {

    }

    findElements(findOnlyASINs = false) {
        this.findASINsList();
        if (!findOnlyASINs) {
            super.findElements();
            this.collectASINsCards();
        }
    }
}