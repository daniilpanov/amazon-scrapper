const scrap_process_table = document.getElementById('scrap-process');

document.querySelector('form[action="/scrap"]').addEventListener('submit', (ev) => {
    ev.preventDefault();
    const url = ev.target.getElementsByTagName('input')[0].value;
    if (!url.startsWith('https://sellercentral.amazon.com/')) {
        alert('Wrong URL! It must starts with "https://sellercentral.amazon.com/"!');
    } else {
        ev.target.reset();
        sellerCentralTask(url);
    }
});

function wait(key, func, apply = false, default_value = '[]') {
    if (localStorage.getItem(key + 'Lock') === 'true') {
        return setTimeout(wait, 500, key, func);
    }
    localStorage.setItem(key + 'Lock', 'true');
    const data = JSON.parse(localStorage.getItem(key) || default_value);
    const res = func(data);
    if (apply && res) {
        localStorage.setItem(key, JSON.stringify(res));
    }
    localStorage.setItem(key + 'Lock', 'false');
    return res;
}

function manageTasks() {
    wait('tasks', (tasks) => {
        for (const i in tasks) {
            if (tasks[i].status === 'pending') {
                tasks[i].status = 'started';
                localStorage.setItem('tasks', JSON.stringify(tasks));
                chrome.tabs.create({
                    url: tasks[i].url,
                    active: false,
                }, (tab) => {
                    chrome.scripting.executeScript({
                        target: {tabId: tab.id},
                        func: () => {
                            // Wait for element by the CSS Selector using setTimeout
                            function waitForElement(path_to_element, callback, stop_callback, counter = 0) {
                                const el = document.querySelectorAll(path_to_element);
                                if (!el || (typeof el.length !== 'undefined' && !el.length)) {
                                    if (!stop_callback || !stop_callback(counter++)) {
                                        return setTimeout(waitForElement, 250, path_to_element, callback);
                                    }
                                }
                                else {
                                    return callback(el);
                                }
                            }
                            chrome.runtime.onMessage.addListener((task_id, sender, sendResponse) => {
                                sendResponse('OK');
                                let task = null, key = null;
                                const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
                                for (const i in tasks) {
                                    if (tasks[i].id === task_id) {
                                        task = tasks[i];
                                        key = i;
                                        break;
                                    }
                                }
                                if (!task || !key) {
                                    tasks[key].status = 'nodata';
                                    return;
                                }
                                // TODO: body
                                const list_courses = document.querySelector('#courselisting-expander > div');
                                if (!list_courses) {
                                    tasks[key].status = 'nodata';
                                    return;
                                }
                                const data = [];
                                let row, curr_row;
                                for (const course of list_courses) {
                                    row = {
                                        'course_name': course.getAttribute('data-a-expander-name'),
                                        'course_id': course.getAttribute('id'),
                                    };
                                    for (const module of course.children[1].children) {
                                        curr_row = {...row};
                                        curr_row['module_name'] = module.innerText;
                                        curr_row['module_id'] = module.getAttribute('data-module-id');
                                        data.push(curr_row);
                                    }
                                }
                                let url;
                                for (const item of data) {
                                    url = `https://sellercentral.amazon.com/learn/courses?ref_=su_course_accordion&moduleId=${item.module_id}&courseId=${item.course_id}&modLanguage=English`;

                                }
                                // end body
                                tasks[key].status = 'done';
                                localStorage.setItem('tasks', JSON.stringify(tasks));
                            });
                        },
                    });
                });
            }
        }
    });
}

function sellerCentralTask(url) {
    const id = scrap_process_table.getElementsByTagName('tr').length;
    const row = document.createElement('tr');
    const col_url = document.createElement('td');
    const col_status = document.createElement('td');
    row.appendChild(col_url);
    row.appendChild(col_status);
    row.id = '' + id;
    scrap_process_table.appendChild(row);
    col_url.innerText = url;
    col_status.innerText = 'pending';

    wait('tasks', (tasks) => {
        return tasks.push({'id': id, 'url': url, 'status': 'pending'});
    }, true);
}

function sendMessageToTab(tabId, message, retryDelay = 500, maxRetries = 100) {
    let attempts = 0;

    function sendMessage() {
        ++attempts;
        chrome.tabs.sendMessage(tabId, message, function(response) {
            if (chrome.runtime.lastError) {
                if (attempts < maxRetries) {
                    // console.error(`Ошибка при отправке сообщения: ${chrome.runtime.lastError.message}. Повторная попытка ${attempts} из ${maxRetries}...`);
                    setTimeout(sendMessage, retryDelay);
                } else {
                    console.error(`Не удалось отправить сообщение после ${maxRetries} попыток.`);
                }
            } else {
                // console.log('Сообщение отправлено успешно:', response);
            }
        });
    }

    sendMessage();
}
