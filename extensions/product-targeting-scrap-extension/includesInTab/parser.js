class Parser {
    functions = [];
    root = document;
    waitElementQuerySelector;
    result = {};

    constructor({ funcs, doc }) {
        this.functions = funcs || [];
        this.root = doc || this.root;
    }

    getElementByIds(ids) {
        let r;
        for (const el_id of ids) {
            r = this.root.getElementById(el_id);
            if (r) {
                return r;
            }
        }
        return null;
    }

    waitLoading(overrideRoot = false) {
        if (!this.waitElementQuerySelector) {
            return null;
        }
        return new Promise(resolve => {
            let appElement = document.querySelector(this.waitElementQuerySelector);
            if (appElement) {
                if (overrideRoot) {
                    this.root = appElement;
                }
                return resolve(appElement);
            }

            const observer = new MutationObserver((mutationsList, observer) => {
                for (let mutation of mutationsList) {
                    if (mutation.type === 'childList' || mutation.type === 'subtree') {
                        appElement = document.querySelector(this.waitElementQuerySelector);
                        if (appElement) {
                            observer.disconnect();
                            if (overrideRoot) {
                                this.root = appElement;
                            }
                            return resolve(appElement);
                        }
                    }
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
            });
        });
    }

    appendFunctions(funcs) {
        this.functions = [...this.functions, ...(funcs || [])];
    }

    errorHandler(e) {
        console.error(e);
    }

    async applyAsyncFunctions() {
        this.result = {};
        let item;
        for (let func of this.functions) {
            try {
                if (func.bind) {
                    func = func.bind(this);
                }
                item = func(this.root, this.result);
                if (func.constructor.name === 'AsyncFunction') {
                    item = await item;
                }
            } catch (e) {
                this.errorHandler(e);
                continue;
            }
            if (item === false) {
                return null;
            }
            else if (typeof item === 'object') {
                this.result = {...this.result, ...item};
            }
        }
        return this.result;
    }

    applyFunctions() {
        this.result = {};
        let item;
        for (let func of this.functions) {
            try {
                if (func.bind) {
                    func = func.bind(this);
                }
                item = func(this.root, this.result);
            } catch (e) {
                this.errorHandler(e);
                continue;
            }
            if (item === false) {
                return null;
            }
            else if (typeof item === 'object') {
                this.result = {...this.result, ...item};
            }
        }
        return this.result;
    }
}