class MultiParser {
    elements = [];
    functions = [];
    elementsQuerySelector;
    root = document;
    waitElementQuerySelector;
    result = [];

    constructor(funcs, doc) {
        this.functions = funcs || [];
        this.root = doc || this.root;
    }
    
    waitLoading() {
        if (!this.waitElementQuerySelector) {
            return null;
        }
        return new Promise((function (resolve) {
            let appElement = document.querySelector(this.waitElementQuerySelector);
            if (appElement) {
                return resolve(appElement);
            }

            const observer = new MutationObserver((function (mutationsList, observer) {
                for (let mutation of mutationsList) {
                    if (mutation.type === 'childList' || mutation.type === 'subtree') {
                        appElement = document.querySelector(this.waitElementQuerySelector);
                        if (appElement) {
                            observer.disconnect();
                            return resolve(appElement);
                        }
                    }
                }
            }).bind(this));

            observer.observe(document.body, {
                childList: true,
                subtree: true,
            });
        }).bind(this));
    }

    newIteration() {
    }

    appendFunctions(funcs) {
        this.functions = [...this.functions, ...(funcs || [])];
    }

    findElements() {
        if (this.elementsQuerySelector) {
            this.elements = this.root?.querySelectorAll(this.elementsQuerySelector) || [];
        }
    }

    errorHandler(e) {
        console.error(e);
    }

    applyFunctions() {
        this.result = [];
        for (let elIndex = 0; elIndex < this.elements.length; ++elIndex) {
            this.newIteration();
            let row = {}, item;
            for (const func of this.functions) {
                try {
                    item = func.bind(this)(this.elements[elIndex], elIndex, this.result);
                } catch (e) {
                    this.errorHandler(e);
                    continue;
                }
                if (item === false) {
                    console.log('OKOKOK!!!');
                    break;
                }
                else if (typeof item === 'object') {
                    row = {...row, ...item};
                }
            }
            if (item !== false) {
                this.result.push(row);
            }
        }
        return this.result;
    }
}