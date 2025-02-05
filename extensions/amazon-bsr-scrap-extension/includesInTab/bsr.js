class BSRMultiParser extends MultiParser {
    elementsQuerySelector = 'div.a-cardui[id*="asin-index"]';
    waitElementQuerySelector = 'div.a-cardui';
    ASINsList = [];

    findASINsList() {
        const element = this.root.querySelector('[data-client-recs-list]');
        if (!element) {
            return this.ASINsList;
        }
        try {
            const data = JSON.parse(element.getAttribute('data-client-recs-list'));
            for (const item of data) {
                this.ASINsList.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) });
            }
        } catch (e) {
        }
        return this.ASINsList;
    }

    collectASINsCards() {
    }

    findElements(findOnlyASINs = false) {
        this.findASINsList();
        if (findOnlyASINs) {
            this.elements = this.ASINsList;
        } else {
            super.findElements();
            this.collectASINsCards();
        }
    }

    clickNextPage() {
        super.clickNextPage();
        const newPage = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
        if (newPage) {
            newPage.click();
            return true;
        }
        return false;
    }
}