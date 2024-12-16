class BSRChildrenParser extends Parser {
    // elementsQuerySelector = 'div[role=group] > div[role=treeitem] > a, div[role=group] > div[role=treeitem] > span';
    waitElementQuerySelector = 'div.a-cardui';
    allFunctions = [this.getASINsList, this.getTree, this.getCurrent, this.getParent, this.getChildren];

    tree = [];
    flatTree = [];
    ASINsListWithInternalInfo = [];
    ASINsList = [];
    productsList = [];

    currentBSR = null;

    _getCategoryName(el) {
        return { bsrName: el.textContent.trim() || null };
    }

    _getCategoryLink(el) {
        return { bsrLink: el.href || el.getAttribute('href') || null };
    }

    getASINsList() {
        if (this.ASINsList && this.ASINsList.length) {
            return { asins: this.ASINsList };
        }
        const element = this.root.querySelector('[data-client-recs-list]');
        if (!element) {
            return { asins: (this.ASINsList = []) };
        }
        try {
            this.ASINsListWithInternalInfo = JSON.parse(element.getAttribute('data-client-recs-list'));
            for (const item of this.ASINsListWithInternalInfo) {
                if (item.id) {
                    this.ASINsList.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) });
                }
            }
        } catch (e) {
        }
        return { asins: this.ASINsList };
    }

    async _uploadOtherProductsByRequest(offset){
        this.getASINsList();
        // Get the page without postprocessing
        const pageResponse = await fetch(location.href);
        if (pageResponse.status !== 200) {
            return null;
        }
        const pageContent = await pageResponse.text();
        const docWithoutPostprocessing = this.parser.parseFromString(pageContent, 'text/html');
        // Then get all hidden params for internal requests
        const paramsEl = docWithoutPostprocessing.querySelector('[data-acp-params][data-acp-path][data-acp-stamp][data-acp-tracking]');
        if (!paramsEl) {
            return null;
        }
        let requestPath = paramsEl.getAttribute('data-acp-path'),
            tok_ts_rid_d1_d2= '', requestStamp = '';
        if (!requestPath) {
            return null;
        }
        tok_ts_rid_d1_d2 = paramsEl.getAttribute('data-acp-params');
        requestStamp = paramsEl.getAttribute('data-acp-stamp');

        const reftag = this.root.querySelector('[data-reftag]')?.getAttribute('data-reftag') || '';
        const resDoc = await fetch(`https://www.amazon.com${requestPath}nextPage?page-type=zeitgeist&stamp=${requestStamp}`, {
            headers: {
                'Content-Type': 'application/json',
                'x-amz-acp-params': tok_ts_rid_d1_d2,
                'x-amz-amabot-click-attributes': 'disable',
            },
            body: JSON.stringify({
                faceoutkataname: 'GeneralFaceout',
                ids: this.ASINsListWithInternalInfo.slice(offset).map(el => JSON.stringify(el)),
                indexes: this.ASINsListWithInternalInfo.slice(offset).map(el => Number.parseInt(el.metadataMap['render.zg.rank'])),
                linkparameters: '',
                offset: String(offset),
                reftagprefix: reftag,
            }),
            method: 'POST',
        });
        if (resDoc.status === 200){
            const res = this.parser.parseFromString(await resDoc.text(), 'text/html');
            return res || null;
        }
        return null;
    }

    _parseBSR(doc) {
        const elements = doc?.querySelectorAll('#gridItemRoot, .gridItemRoot') || [];
        let parsedData = [];
        for (let el of elements) {
            el = el.querySelector('div.a-cardui[id*="asin-index"]');
            if (!el) continue;
            el = el.querySelector('[data-asin]');
            const asin = el?.getAttribute('data-asin') || null;
            if (!asin) continue;
            parsedData.push({ asin });
        }
        return parsedData;
    }

    async getProductsInfo() {
        if (this.productsList && this.productsList.length) {
            return { products: this.productsList };
        }
        this.productsList = this._parseBSR(this.root);
        this.productsList = [...this.productsList, ...this._parseBSR(await this._uploadOtherProductsByRequest(this.productsList.length))];
        return { products: this.productsList };
    }

    _findCurrent(elem) {
        for (const groupElement of (elem.group || [])) {
            if (groupElement.bsrLink === this.currentBSR.bsrLink && groupElement.bsrName === this.currentBSR.bsrName) {
                return elem;
            }
            const res = this._findCurrent(groupElement);
            if (res) {
                return res;
            }
        }
        return null;
    }

    getParent() {
        let parentBSR = { ...this._findCurrent({ group: this.tree }) };
        delete parentBSR.group;
        return { parentBSR };
    }

    getCurrent() {
        let currentBSR = { ...this.currentBSR };
        delete currentBSR.group;
        return { currentBSR };
    }

    _getTreeRecursive(treeGroup, group, level) {
        let lastObj = null;
        let index = 0;

        for (const treeElement of treeGroup) {
            if (treeElement.getAttribute('role') === 'treeitem') {
                const el = treeElement.children[0];
                lastObj = { index, ...this._getCategoryName(el), ...this._getCategoryLink(el), level };
                if (!lastObj.bsrLink) {
                    lastObj.bsrLink = location.href;
                    this.currentBSR = lastObj;
                }
                group.push(lastObj);
                this.flatTree.push(lastObj);
                ++index;
            } else {
                lastObj.group = [];
                this._getTreeRecursive(treeElement.children || [], lastObj.group, level + 1);
            }
        }
    }

    getTree() {
        this._getTreeRecursive(this.root.querySelector('div[role=tree]')?.children || [], this.tree, 0);
        return { tree: this.tree };
    }

    getChildren() {
        return { childrenBSR: this.currentBSR.group || [] };
    }

    clickNextPage() {
        const newPage = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
        if (newPage) {
            newPage.click();
            return true;
        }
        return false;
    }
}