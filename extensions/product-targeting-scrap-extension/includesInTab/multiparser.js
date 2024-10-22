class MultiParser extends Parser {
    elements = [];
    elementsQuerySelector;

    newIteration() {
    }

    findElements() {
        if (this.elementsQuerySelector) {
            this.elements = this.root?.querySelectorAll(this.elementsQuerySelector) || [];
        }
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