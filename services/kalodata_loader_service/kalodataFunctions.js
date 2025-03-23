async function getDaysConfig() {
    const allLastDaysResponse = await fetch('https://www.kalodata.com/api/allLastDay');
    const allLastDays = (await allLastDaysResponse.json())?.data || [];
    let dateConfig = {};
    for (let data of allLastDays) {
        if (data.country === 'US') {
            dateConfig.endDateStr = data.lastDay;
            dateConfig.endDate = new Date(data.lastDay);
            dateConfig.startDate = new Date(dateConfig.endDate);
            break;
        }
    }
    return dateConfig;
}

function getDateShift(date, shiftLeft, str = true) {
    const d = new Date(date);
    d.setDate(d.getDate() - shiftLeft);
    return str ? d.toISOString().split('T')[0]: d;
}

function convertAll(row) {
    const excludedCols = new Set(['duration', 'title']);
    const colsMapping = {};

    for (let key in row) {
        if (!row[key]) continue;
        if (typeof row[key] === 'string') {
            row[key] = row[key].trim() || null;
            if (!excludedCols.has(key) && /^\$?[0-9.]+[%kmb]?$/.test(row[key].toLowerCase()) && (row[key][0] === '$' || ['%', 'k', 'm', 'b'].includes(row[key][row[key].length - 1].toLowerCase()))) {
                const converted = convertNum(row[key]);
                if (converted[1] !== null) {
                    if (converted[0]) {
                        row[key + converted[0]] = converted[1];
                        delete row[key];
                        colsMapping[key] = key + converted[0];
                    } else {
                        row[key] = converted[1];
                    }
                }
            } else if (/^[0-9.]+$/.test(row[key])) {
                row[key] = Number(row[key]);
            }
        } else if (row[key].length) {
            const r = [];
            for (let i of row[key]) {
                if (typeof i === 'object') r.push(convertAll(i)[0]);
                else r.push(i)
            }
            row[key] = r;
        } else if (typeof row[key] === 'object') {
            row[key] = convertAll(row[key])[0];
        }
    }

    return [row,
        colsMapping];
}

function replaceKeys(arr, key, colsMapping) {
    const newData = [];
    for (let row of (key ? arr[key]: arr)) {
        for (const key in row) {
            if (key in colsMapping) {
                row[colsMapping[key]] = row[key];
                delete row[key];
            }
        }
        newData.push(row);
    }
    if (key) arr[key] = newData;
    else arr = newData;
}

async function paginate(func, args, pageData, pagesLimit = null) {
    pageData.pgsize = pageData.pgsize ?? 10;
    const count = await func(...args, true);
    for (let i = 0; i < count && (!pagesLimit || pageData.page < pagesLimit); i += pageData.pgsize, ++pageData.page) {
        const res = await func(...args);
        if (!res) break;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}

function convertNum(num) {
    let numberRange = num.split('-');
    if (numberRange.length > 2) {
        let parts = [];
        let symbol = null;
        for (let numPart of numberRange) {
            let res = convertNum(numPart);
            symbol = res[0] || symbol;
            parts.push(String(res[1]));
        }
        return [symbol,
            ...parts];
    }
    num = num.replace(',', '');
    // Config
    let k = 1;
    let symbolsMap = {
        'k': 1000,
        'm': 1000000,
        'b': 1000000000,
    };
    for (let sym in symbolsMap) {
        if (num.slice(num.length - 1).toLowerCase() === sym) {
            k = symbolsMap[sym];
            num = num.slice(0, num.length - 1);
            break;
        }
    }
    let symbol = null;
    if (!/[0-9]/.test(num[0])) {
        symbol = num[0];
        num = num.slice(1);
    } else if (!/[0-9]/.test(num.slice(num.length - 1))) {
        symbol = num.slice(num.length - 1);
        num = num.slice(0, num.length - 1);
    }
    try {
        num = parseFloat(num);
        return [symbol,
            num * k];
    } catch (e) {
        return [null,
            null];
    }
}
