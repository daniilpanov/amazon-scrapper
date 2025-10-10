function parseNumber(numStr) {
    if (typeof numStr !== 'string')
        return [null, null, null];
    numStr = numStr.trim();
    const numberRange = numStr.split('-');
    if (numberRange.length > 2) {
        return [null, null, null];
    }
    if (numberRange.length > 1) {
        const parts = [];
        let res, symbol = null, more = false;
        for (let numPart of numberRange) {
            res = parseNumber(numPart);
            symbol = res[0] || symbol;
            more = res[2];
            parts.push(res[1].toString());
        }
        return [symbol, parts.join('-'), more];
    }
    numStr = numStr.replaceAll(',', '');
    // Config
    let more = false, k = 1, symbol = null;
    if (numStr[numStr.length - 1] === '+') {
        more = true;
        numStr = numStr.slice(0, numStr.length - 1);
    }
    if (!/^\d$/.test(numStr[0])) {
        symbol = numStr[0].toLowerCase();
        numStr = numStr.slice(1);
    } else if (!/^\d$/.test(numStr[numStr.length - 1])) {
        symbol = numStr[numStr.length - 1].toLowerCase();
        numStr = numStr.slice(0, numStr.length - 1);
    }
    const symbolsMap = {
        k: 1000,
        m: 1000000,
        b: 1000000000,
    };
    if (symbol in symbolsMap) k = symbolsMap[symbol];
    try {
        const num = Number.parseFloat(numStr);
        return [symbol, num * k, more];
    } catch (e) {
        return [null, null, null];
    }
}
