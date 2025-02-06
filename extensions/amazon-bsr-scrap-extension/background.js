AbortSignal.timeout ??= function timeout(ms) {
    const ctrl = new AbortController();
    setTimeout(() => ctrl.abort(), ms);
    return ctrl.signal;
};

let lastUpdate = Date.now();
const urlList = [
    'https://localhost',
    'http://localhost',
    'https://cp.nyle.ai',
    'http://cp.nyle.ai',
    'https://195.201.194.213',
    'http://195.201.194.213',
];
let currentUrl = urlList[0];

const URL_EXPIRATION_TIME = 5 * 60 * 1000;

async function endp(uri, force = false) {
    if (!force && Date.now() - lastUpdate < URL_EXPIRATION_TIME) {
        return currentUrl + uri;
    }

    for (const url of urlList) {
        try {
            const response = await fetch(url + ':8832/ping', { method: 'GET', signal: AbortSignal.timeout(5000) });
            console.log(response.ok);
            if (response.ok) {
                currentUrl = new URL(url).origin;
                lastUpdate = Date.now();
                return currentUrl + uri;
            }
        } catch (error) {
            console.log(error);
        }
    }

    return null;
}


endp(':8832/ping', true).then(res => {
    console.log('URL:', res);
    if (!res) {
        console.log('Error! No endpoints found!');
        return;
    }
    chrome.tabs.query({
        url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
    }, tabs => {
        if (!tabs || !tabs.length) {
            chrome.tabs.create({
                url: 'html/control_panel.html',
            }, tab => {
                chrome.tabs.update(tab.id, { autoDiscardable: false });
            });
        }
    });

    chrome.runtime.onMessageExternal.addListener(run);
    chrome.runtime.onMessage.addListener(run);
});

async function run(task, sender, sendResponse) {
    let acq = await fetch(
        await endp(':8832/tasks/acquire/bsr/' + task.header_id + '/' + task.task_id),
        { method: 'post' },
    );
    if (acq.status !== 200) {
        if (acq.status === 409) {
            sendResponse('busy');
        } else {
            sendResponse('fail');
            console.error('Error when try to acquire task:', acq.statusText);
        }
        return;
    }
    sendResponse('OK');
    if (task.bsr.startsWith('http://')) {
        task.bsr = task.bsr.slice(7);
    } else if (task.bsr.startsWith('https://')) {
        task.bsr = task.bsr.slice(8);
    }
    if (task.bsr.startsWith(task.domain)) {
        task.bsr = task.bsr.slice(task.domain.length + 1);
    } else if (task.bsr.startsWith('www.' + task.domain)) {
        task.bsr = task.bsr.slice(task.domain.length + 5);
    }
    let needle_tab = await chrome.tabs.create({
        url: 'https://www.' + task.domain + '/' + task.bsr,
        active: false,
        windowId: task.windowId,
    });
    chrome.tabs.update(needle_tab.id, { autoDiscardable: false });

    const date = new Date();
    try {
        // BSR lib
        await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            files: ['./includesInTab/parser.js', './includesInTab/bsrchildren.js'],
        });
        console.log('bsr imported');
        // BSR result
        let response = await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            func: async () => {
                const bsr_collector = new BSRChildrenParser();
                await bsr_collector.waitLoading();
                bsr_collector.appendFunctions([bsr_collector.getProductsInfo, bsr_collector.getTree, bsr_collector.getCurrent]);

                return {
                    result: await bsr_collector.applyAsyncFunctions(),
                    newPage: bsr_collector.clickNextPage(),
                };
            },
        });

        const asins = new Set();
        const { result, newPage } = response[0]?.result;

        if (!result) {
            throw new Error('Unknown error: empty result from the tab');
        }

        let found = false;
        for (const { asin } of result.products) {
            if (asin === task.target) {
                found = true;
            }
            asins.add(asin);
        }

        if (newPage) {
            await new Promise(r => setTimeout(r, 1000, r));
            // BSR lib
            await chrome.scripting.executeScript({
                target: { tabId: needle_tab.id },
                files: ['./includesInTab/parser.js', './includesInTab/bsrchildren.js'],
            });
            response = await chrome.scripting.executeScript({
                target: { tabId: needle_tab.id },
                func: async () => {
                    const bsr_collector = new BSRChildrenParser();
                    await bsr_collector.waitLoading();
                    bsr_collector.offset = 50;

                    return await bsr_collector.getProductsInfo();  // Call the parsing function directly
                },
            });

            const newResult = response[0]?.result;
            if (newResult && newResult.products?.length) {
                for (const product of newResult.products) {
                    if (product.asin === task.target) {
                        found = true;
                    }
                    if (asins.has(product.asin)) continue;
                    result.products.push(product);
                }
            }
        }

        if (!found) {
            result.products.push({ asin: task.target });
        }
        const depsFlatTree = findDepartmentPath({ group: result.tree }, result.currentBSR);
        // load data
        if (Object.keys(result || {}).length) {
            const resLoadBSR = await fetch(await endp(':8839/v1/bsr/load/bsr'), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify({ departments_flat_tree: depsFlatTree }),
            });
            if (!resLoadBSR.ok || resLoadBSR.status > 299) {
                throw new Error('Error on loading result (load/bsr): ' + resLoadBSR.statusText + ' [' + await resLoadBSR.text() + ']');
            }
            let { bsr_id } = await resLoadBSR.json();
            if (!bsr_id) {
                throw new Error('Invalid data received! No bsr_id!');
            }
            const resLoadProducts = await fetch(await endp(':8839/v1/bsr/load/asins'), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify({
                    bsr_id,
                    asins: result.products,
                }),
            });
            if (!resLoadProducts.ok || resLoadProducts.status > 299) {
                throw new Error('Error on loading result (load/asins): ' + resLoadProducts.statusText + ' [' + await resLoadProducts.text() + ']');
            }
            const resData = await resLoadProducts.json();
            if (typeof resData.bsr_url === 'undefined' || typeof resData.bsr_id === 'undefined' || typeof resData.nodata_asins === 'undefined') {
                throw new Error('Invalid data received! ' + JSON.stringify(resData));
            }

            // Finish
            const yieldTask = await fetch(await endp(':8832/tasks/stage/' + task.task_id), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    release: (task.stage > 0),
                    stage: task.stage + (task.stage > 0),  // Increase stage if not 0
                    result: resData,
                }),
            });
            if (!yieldTask.ok || yieldTask.status > 299) {
                throw new Error('Can\'t yield task! ' + yieldTask.status + ' ' + yieldTask.statusText + ' [' + await yieldTask.text() + ']');
            }

            if (!task.stage) {
                const finishTask = await fetch(await endp(':8832/tasks/finish/' + task.task_id), {
                    method: 'PATCH',
                });
                if (!finishTask.ok || finishTask.status > 299) {
                    throw new Error('Can\'t finish task! ' + finishTask.status + ' ' + finishTask.statusText + ' [' + await finishTask.text() + ']');
                }
                fetch(await endp(':8832/tasks/release/' + task.task_id), { method: 'POST' });
            }
        }
    } catch (e) {
        console.log(e);
        fetch(await endp(':8832/tasks/report/' + task.task_id), {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'PATCH',
            body: JSON.stringify({
                confirm: true,
                errors: [
                    date.toISOString() + ' [bsr] Error: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        await chrome.tabs.remove(needle_tab.id);
    }
}


function findDepartmentPath(departmentTree, currentDepartment) {
    // Функция для поиска департамента
    function search(department) {
        // Проверяем, совпадает ли текущий департамент с искомым
        if (department.bsrName === currentDepartment.bsrName && department.bsrLink === currentDepartment.bsrLink) {
            return { [department.bsrName]: department.bsrLink };
        }

        // Если у департамента есть подгруппы, ищем в них
        if (department.group && department.group.length > 0) {
            for (let subDepartment of department.group) {
                const result = search(subDepartment);
                if (result) {
                    // Если нашли, добавляем текущий департамент в путь (если уровень текущего не нулевой)
                    if (department.level > 0) {
                        return { [department.bsrName]: department.bsrLink, ...result };
                    }
                    // Иначе просто возвращаем результат
                    return result;
                }
            }
        }

        return null; // Если не нашли, возвращаем null
    }

    // Запускаем поиск с верхнего уровня
    const path = search(departmentTree);

    // Убираем первый элемент (департамент 0 уровня)
    if (path && Object.keys(path).length > 1) {
        return path;
    }

    return null; // Если путь не найден, возвращаем пустой массив
}
