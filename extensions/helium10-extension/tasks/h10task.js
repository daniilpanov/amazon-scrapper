console.log('Hello! This tab is under the UniScrap control!');
// Get the Bearer Auth token :)
const bearers = JSON.parse(localStorage.getItem('CORE_BEARER_TOKEN'));
const my_bearer = bearers['1545531519'];

// JSON -> CSV
function convertToCSV(arr) {
    // Взять заголовки из ключей первого объекта
    const csvRows = [];
    let row0 = null, last_header = null;
    for (const row of arr) {
        // Учитываем два варианта отображения позиции:
        // 1) в виде объекта {asin: <>, position: <>}
        if (row.positionsRange && row.positionsRange.length) {
            row0 = {...row};
            break;
        } else {  // 2) в виде отдельного столбца
            for (const key in row) {
                if (key.length === 10 && key.startsWith('B0')) {
                    row0 = {...row};
                    last_header = row[key];
                    break;
                }
            }
        }
    }
    // Снова определяем разницу между отображениями
    let range = null;
    if (!row0) {
        row0 = {...arr[0]};
    } else if (row0.positionsRange) {
        range = row0.positionsRange;
        row0[range[0].asin] = range[0].position;
        last_header = range[0].asin;
    }
    // Удаляем всё ненужное
    delete row0.matchType;
    delete row0.resultsNumberUpdatedAt;
    delete row0.resultsNumberOver;
    delete row0.headlineAsins;
    delete row0.newCprBroad;
    delete row0.searchFrequencyRank;
    delete row0.positionsRange;
    // Переименовываем колонки
    let headers_map = {
        "phrase": "Keyword Phrase",
        "resultsNumber": "Competing Products",
        "impressionExact30": "Search Volume",
        "exactTitleMatchProductsCount": "Title Density",
        "iq": "Cerebro IQ Score",
        "sponsoredAsins": "Sponsored ASINs",
        "searchVolumeTrend": "Search Volume Trend",
        "newCprExact": "CPR",
        "relativeRank": "Relative Rank",
        /*"positionsRange": [
        {
            "asin": "B086XYZDLH",
            "position": 1
        }
        ], -- AA -- {{ASIN}}*/
        "competitiveAvg": "Competitor Rank (avg)",
        "rankingCompetitors": "Ranking Competitors (count)",
        "amzSuggestedAvg": "Amazon Recommended Rank (avg)",
        "amzSuggestedCount": "Amazon Recommended Rank (count)",
        "sponsoredAvg": "Sponsored Rank (avg)",
        "sponsoredCount": "Sponsored Rank (count)",
        "competitorPerformanceScore": "Competitor Performance Score",
        "rank": "Position (Rank)",
        "monthlySales": "Keyword Sales",
        "clickShareRate": "ABA Total Click Share",
        "conversionShareRate": "ABA Total Conv. Share",
        "cpc": "H10 PPC Sugg. Bid",
        "highCpc": "H10 PPC Sugg. Max Bid",
        "lowCpc": "H10 PPC Sugg. Min Bid",
    };
    let headers = Object.keys(headers_map);
    if (last_header) {
        headers_map[last_header] = last_header;
        headers.push(last_header);
    }
    csvRows.push(headers.map(header => {
        return headers_map[header]
    }).join(','));

    // Преобразовать каждый объект в строку CSV
    for (let row of arr) {
        row = {...row};
        // Добавляем последний столбец
        if (last_header) {
            const range = row.positionsRange;
            row[last_header] = range && range.length ? range[0].position : '';
        }
        // Удаляем ненужное
        delete row.matchType;
        delete row.resultsNumberUpdatedAt;
        delete row.resultsNumberOver;
        delete row.headlineAsins;
        delete row.newCprBroad;
        delete row.searchFrequencyRank;
        delete row.positionsRange;
        // Округляем
        row.sponsoredAvg = Math.round(row.sponsoredAvg);
        row.iq = Math.round(row.iq);
        row.newCprExact = Math.round(row.newCprExact);
        // Приводим к нужному виду, доли
        row.cpc = row.cpc / 100;
        row.highCpc = row.highCpc / 100;
        row.lowCpc = row.lowCpc / 100;
        // Форматируем
        row.phrase = `"${row.phrase.replace(/["\\]/g, '')}"`;
        // Приводим к строке
        let values = headers.map(header => {
            const item = row[header] ?? '';
            return '' + item;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}

// Wait ready state
function waitStatus(id, bearer, callback) {
    fetch(`https://research-tools.helium10.com/api/cerebro/v1/amazon/search/multiple/${id}/status?accountId=1545531519`, {
        'headers': {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + bearer,
            'Content-Type': 'application/json',
        },
        'method': 'GET',
    }).then(data => {
        data.json().then(data => {
            if (data.data.status < 1) {
                setTimeout(waitStatus, 500, id, bearer, callback);
            } else {
                callback(data);
            }
        })
    });
}

// Wait data
function runH10Task(task) {
    const {asins} = task;
    // Wait for loading base form
    waitForElement('div[name=asins] input', (els) => {
        // Removing ASINs if exist
        cycleRemove('[data-testid=remove-button]');
        // After it,
        setTimeout(() => {
            // send the first query -- get-previous-search
            fetch('https://research-tools.helium10.com/api/cerebro/v1/search/multiple/previous-searches?accountId=1545531519&marketplace=ATVPDKIKX0DER&productIds%5B%5D=' + asins.join('&productIds%5B%5D='), {
                "headers": {
                    "Accept": "application/json",
                    "Authorization": "Bearer " + my_bearer,
                    "Content-Type": "application/json",
                },
                "method": "GET",
            }).then(data => {
                // [ignore response]
                data.json().then(data => {
                    main(task.task_id, asins);
                }).catch(reason => {
                    main(task.task_id, asins, reason);
                });
            }).catch(reason => {
                main(task.task_id, asins, reason);
            });
        }, 500);
    }, (counter) => {
        return counter >= 500
    });
}

function main(task_id, asins, _) {
    // The second query -- create-multiple-search
    fetch("https://research-tools.helium10.com/api/cerebro/v1/amazon/search/multiple?accountId=1545531519", {
        "headers": {
            "Accept": "application/json",
            "Authorization": "Bearer " + my_bearer,
            "Content-Type": "application/json",
        },
        "body": `{"marketplace":"ATVPDKIKX0DER","mainProductId":"${asins[0]}","productIds":${JSON.stringify(asins)},"adminSearch":false,"exactProduct":false}`,
        "method": "POST",
    }).then(res => {
        if (res.status >= 300) {
            res.json().then(d => {
                chrome.runtime.sendMessage(
                    {
                        fetch: [
                            'http://195.201.194.213:8832/tasks/report/' + task_id,
                            {
                                headers: {
                                    // 'Content-Encoding': 'gzip',
                                    'Content-Type': 'application/json',
                                },
                                method: 'PATCH',
                                body: JSON.stringify({
                                    confirm: true,
                                    errors: [
                                        ['Error when try to create cerebro task', d],
                                    ],
                                    stop: true,
                                }),
                            },
                        ]
                    },
                    (response) => {
                        // Close the window!!!
                        window.close();
                    },
                );
            });
            return;
        }
        res.json().then(data => {
            const id = data.data.id;
            // The third query (collection of queries) -- wait for ready state
            waitStatus(id, my_bearer, (data) => {
                if (data.data.status !== 1) {
                    chrome.runtime.sendMessage(
                        {
                            fetch: [
                                'http://195.201.194.213:8832/tasks/report/' + task_id,
                                {
                                    headers: {
                                        // 'Content-Encoding': 'gzip',
                                        'Content-Type': 'application/json',
                                    },
                                    method: 'PATCH',
                                    body: JSON.stringify({
                                        confirm: true,
                                        errors: [
                                            'Invalid ASINs!',
                                        ],
                                        stop: true,
                                    }),
                                },
                            ]
                        },
                        (response) => {
                            // Close the window!!!
                            window.close();
                        },
                    );
                    return;
                }
                // The fourth query -- get-end-task-body
                fetch(`https://research-tools.helium10.com/api/cerebro/v1/amazon/search/multiple/${id}?accountId=1545531519`, {
                    "headers": {
                        "Accept": "application/json",
                        "Authorization": "Bearer " + my_bearer,
                        "Content-Type": "application/json",
                    },
                    "method": "GET",
                }).then(data => {
                    data.json().then(data => {
                        // [ignore response]
                        // The fifth query -- get additional data about ASINs
                        fetch(`https://research-tools.helium10.com/api/cerebro/v1/amazon/search/multiple/${id}/data?accountId=1545531519&include-all=0&include-any=1&page=1&per_page=50&sort=default`, {
                            "headers": {
                                "Accept": "application/json",
                                "Authorization": "Bearer " + my_bearer,
                                "Content-Type": "application/json",
                            },
                            "method": "GET",
                        }).then(data => {
                            data.json().then(data => {
                                if (!data.data.productDetails) {
                                    chrome.runtime.sendMessage(
                                        {
                                            fetch: [
                                                'http://195.201.194.213:8832/tasks/report/' + task_id,
                                                {
                                                    headers: {
                                                        // 'Content-Encoding': 'gzip',
                                                        'Content-Type': 'application/json',
                                                    },
                                                    method: 'PATCH',
                                                    body: JSON.stringify({
                                                        confirm: true,
                                                        errors: [
                                                            'No data received from Helium10!',
                                                        ],
                                                        stop: true,
                                                    }),
                                                },
                                            ]
                                        },
                                        (response) => {
                                        },
                                    );
                                    return;
                                }
                                // Get only titles
                                let result = {'titles': {}, 'image_urls': {}, 'export': []};
                                for (const details of data.data.productDetails) {
                                    result.titles[details.asin] = details.title;
                                    result.image_urls[details.asin] = details.imageUrl;
                                }
                                // The sixth query -- export-data
                                fetch(`https://research-tools.helium10.com/api/cerebro/v1/amazon/search/multiple/${id}/exported-data?accountId=1545531519&include-all=0&include-any=1&sort=default`, {
                                    "headers": {
                                        "Accept": "application/json",
                                        "Authorization": "Bearer " + my_bearer,
                                        "Content-Type": "application/json",
                                    },
                                    "method": "GET",
                                }).then(data => {
                                    data.json().then(data => {
                                        // Make the CSV
                                        result.export = convertToCSV(data.data);
                                        // The last (seventh) query -- track-event
                                        fetch("https://research-tools.helium10.com/api/site/track-event?accountId=1545531519", {
                                            "headers": {
                                                "Accept": "application/json",
                                                "Authorization": "Bearer " + my_bearer,
                                                "Content-Type": "application/json",
                                            },
                                            "body": "{\"eventName\":\"Cerebro Export\",\"eventProperties\":{\"marketplace\":\"ATVPDKIKX0DER\",\"format\":\"csv\"}}",
                                            "method": "POST",
                                        }).then(data => {
                                            // HURRAY! All requests done!
                                            chrome.runtime.sendMessage(
                                                {
                                                    fetch: [
                                                        'http://195.201.194.213:8832/helium/set/' + task_id,
                                                        {
                                                            headers: {
                                                                // 'Content-Encoding': 'gzip',
                                                                'Content-Type': 'application/json',
                                                            },
                                                            method: 'POST',
                                                            body: JSON.stringify(result),
                                                        },
                                                    ]
                                                },
                                                (response) => {
                                                    // Close the window!!!
                                                    window.close();
                                                },
                                            );
                                        });
                                    })
                                });
                            })
                        });
                    })
                });
            });
        });
    }).catch(reason => {
        chrome.runtime.sendMessage(
            {
                fetch: [
                    'http://195.201.194.213:8832/tasks/report/' + task_id,
                    {
                        headers: {
                            // 'Content-Encoding': 'gzip',
                            'Content-Type': 'application/json',
                        },
                        method: 'PATCH',
                        body: JSON.stringify({
                            confirm: false,
                            errors: [
                                ['Error when try to create cerebro task', reason],
                            ],
                            stop: false,
                        }),
                    },
                ]
            },
            (response) => {
                chrome.runtime.sendMessage(
                    {fetch: ['http://195.201.194.213:8832/tasks/release/' + task_id, {method: 'POST'}]},
                    (response) => {
                        // Close the window!!!
                        window.close();
                    },
                );
            },
        );
    });
}
