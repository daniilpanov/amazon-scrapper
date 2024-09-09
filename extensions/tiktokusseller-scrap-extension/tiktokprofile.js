function parseNumber(numStr) {
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
    if (numStr[numStr.length - 1] === 'K') {
        k = 1000;
        numStr = numStr.slice(0, numStr.length - 1);
    } else if (numStr[numStr.length - 1] === 'M') {
        k = 1000000;
        numStr = numStr.slice(0, numStr.length - 1);
    } else if (numStr[numStr.length - 1] === 'B') {
        k = 1000000000;
        numStr = numStr.slice(0, numStr.length - 1);
    }
    if (!/^\d$/.test(numStr[0])) {
        symbol = numStr[0];
        numStr = numStr.slice(1);
    } else if (!/^\d$/.test(numStr[numStr.length - 1])) {
        symbol = numStr[numStr.length - 1];
        numStr = numStr.slice(0, numStr.length - 1);
    }
    const symbolsMap = {
        K: 1000,
        M: 1000000,
        B: 1000000000,
    };
    for (const sym in symbolsMap) {
        if (numStr[numStr.length - 1] === sym) {
            k = symbolsMap[sym];
            break;
        }
    }
    try {
        const num = Number.parseFloat(numStr);
        return [symbol, num * k, more];
    } catch (e) {
        console.log(e);
        return [null, null, null];
    }
}

// Get just numbers
function getUsualMetrics(el, thr = false) {
    const data = {};
    // Root elements (> div::first-child > div)
    const metrics_items = el?.children[0]?.children || [];
    for (const metric of metrics_items) {
        // Header element (> div::first-child)
        let key = metric?.children[0]?.innerText.trim();
        if (!key) {
            continue;
        }
        // Value element (> div::second-child)
        let value = metric?.children[1]?.querySelector('span')?.innerText.trim() || metric?.children[1]?.innerText.trim();
        let [symbol, parsedValue, plusSymbol] = parseNumber(value);
        // Check value
        if (parsedValue) {
            if (symbol) {
                key += ', ' + symbol;
            }
            if (plusSymbol) {
                parsedValue += '+';
            }
            data[key] = parsedValue;
        } else if (thr) {
            console.log(value);
            throw new Error('Not numeric value!');
        }
    }
    return data;
}

// Get numbers from diagrams
function getDiagrams(diagrams) {
    const data = {};
    for (const diagram of diagrams) {
        const diagram_items = diagram?.children[0]?.children;
        if (!diagram_items || typeof diagram_items !== 'object' || diagram_items.length < 2) {
            continue;
        }
        let key = diagram_items[0]?.innerText.trim() + ', %';
        if ((diagram_items[1]?.children?.length || 0) < 2) {
            data[key] = null;
            continue;
        }
        let [sub_keys, sub_values] = [...(diagram_items[1]?.children[1]?.children || [])].slice(1);
        sub_keys = sub_keys?.children;
        sub_values = sub_values?.children;
        if (!sub_keys || !sub_values) {
            data[key] = null;
            continue;
        }
        let sub_data = {};
        let tVal;
        for (let i = 0; i < Math.min(sub_keys.length, sub_values.length); ++i) {
            tVal = sub_values[i]?.innerText.trim();
            if (tVal) {
                tVal = tVal.slice(0, tVal.length - 1).replaceAll(',', '');
                if (/^[0-9.]+$/.test(tVal)) {
                    sub_data[sub_keys[i].innerText.trim()] = Number.parseFloat(tVal);
                }
            }
        }
        data[key] = sub_data;
    }
    return data;
}

async function parsePage() {
    let result = null;
    for (let i = 0; i < 10 && result === null; ++i) {
        await new Promise((r) => setTimeout(r, 1000 * (i > 0)));
        try {
            result = parser();
        } catch (e) {
            console.log(e);
        }
    }
    return result;
}

function parser() {
    let data = {url: document.location.href};
    // Get all divs
    const divs = document.querySelectorAll('main > div > div > div.arco-spin-children > div > div:nth-child(2) > div');
    // Group all divs. Example:
    // div, div, div, ..., div.sales_tab[EMPTY], div.sdadasda[DATA], div.followers[EMPTY], div.sadsfsdfsd[DATA]
    // Switch-current method
    let grouped_divs = {};
    let curr = null;
    for (const adiv of divs) {
        if (adiv.id) {
            curr = adiv.id;
        } else {
            grouped_divs[curr] = adiv;
        }
    }
    // Sales tab
    if (grouped_divs.sales_tab) {
        const items = grouped_divs.sales_tab.children;
        data['Sales period'] = items[1]?.innerText.trim();
        const sales_data = items[2];
        const [raw_data, diagrams_root] = sales_data?.children[0]?.children;

        // Metrics
        try {
            data = {...data, ...getUsualMetrics(raw_data, true)};  // Fail on non-numeric values
        } catch (e) {
            console.log(e);
            return null;  // If it was not numeric data - page is not loaded!
        }
        console.log(data);

        // Diagrams
        const diagrams = diagrams_root.children[0].children[0].children[0].children[0].children[0].children;
        data = {...data, ...getDiagrams(diagrams)};
    } else {  // If no main tab - return null
        console.log('err! no sales');
        return null;
    }

    // Collaboration metrics
    if (grouped_divs.collab_history) {
        const items = grouped_divs.collab_history.children;
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // Video tab
    if (grouped_divs.video_tab) {
        const items = grouped_divs.video_tab.children;
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // LIVE tab
    if (grouped_divs.live_tab) {
        const items = grouped_divs.live_tab.children;
        data['LIVE period'] = items[0]?.children[0]?.children[1]?.innerText.trim();
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // Followers tab
    if (grouped_divs.followers_tab) {
        const items = grouped_divs.followers_tab.children[1]?.children[0]?.children[0].children[0].children[0].children;

        // Diagrams
        const diagrams = items[0]?.children;
        data = {...data, ...getDiagrams(diagrams)};
    }

    return data;
}