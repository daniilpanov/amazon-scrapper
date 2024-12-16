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
        'http://195.201.194.213:8832/tasks/acquire/bsr/' + task.header_id + '/' + task.task_id,
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
        let result = await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            args: [task.target],
            func: async target => {
                const bsr_collector = new BSRChildrenParser();
                await bsr_collector.waitLoading();
                bsr_collector.appendFunctions([bsr_collector.getProductsInfo, bsr_collector.getTree, bsr_collector.getCurrent]);
                let res = bsr_collector.applyAsyncFunctions();
                delete res.tree;
                let found = false;
                for (const { asin } of res.products) {
                    if (asin === target) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    res.products = [...res.products, { asin: target }];
                }
                return res;
            },
        });
        result = result[0]?.result;
        const depsFlatTree = findDepartmentPath({ group: result.tree }, result.currentBSR);
        // load data
        if (Object.keys(result || {}).length) {
            const resLoadBSR = await fetch(await endp(':8839/v1/bsr/load/bsr'), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(depsFlatTree),
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

            if (task.stage < 0) {
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
            return [ { bsrName: department.bsrName, bsrLink: department.bsrLink } ];
        }

        // Если у департамента есть подгруппы, ищем в них
        if (department.group && department.group.length > 0) {
            for (let subDepartment of department.group) {
                const result = search(subDepartment);
                if (result) {
                    // Если нашли, добавляем текущий департамент в путь
                    return [ { bsrName: department.bsrName, bsrLink: department.bsrLink }, ...result ];
                }
            }
        }

        return null; // Если не нашли, возвращаем null
    }

    // Запускаем поиск с верхнего уровня
    const path = search(departmentTree);

    // Убираем первый элемент (департамент 0 уровня)
    if (path && path.length > 1) {
        return path.slice(1);
    }

    return []; // Если путь не найден, возвращаем пустой массив
}
