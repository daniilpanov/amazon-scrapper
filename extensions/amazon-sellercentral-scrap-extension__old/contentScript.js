/// THERE IS INTERESTING ///

// я хотел сделать, чтобы можно было с этой вкладки ввести URL на курсы, но теперь понимаю, что лучше сделать так,
// чтобы пользователь сам зашёл на нужную страницу, нажал на расширение, нажал на кнопочку collect и всё запускалось
// Тогда можно обойтись вообще без этой страницы, о чём я и говорил в background.js
const scrap_process_table = document.getElementById('scrap-process');
const repeat_urls = [];

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
// здесь я допустил ошибку: нужно использовать не localStorage, а chrome.local.storage. погугли про это, кучу гайдов найдёшь
function wait(key, func, apply = false, default_value = '[]') {
    // Создание задач может показаться странным, но эта архитектура удобна при разнообразии фич. Что-то наподобие микросервисов, ожидающих новых задач
    if ((new Date()).getTime() - (new Date(Number(localStorage.getItem(key + 'Lock') || 0))).getTime() > 20 * 60 * 1000) {
        localStorage.setItem(key + 'Lock', '');  // разблокируем задачи, которые очень долго заблокированы
    }
    if (localStorage.getItem(key + 'Lock') !== '') {
        return setTimeout(wait, 500, key, func); // если все задачи заблоканы -- ждём дальше
    }
    // иначе блокируем список, получаем задачу, устанавливаем статус и разблокируем
    localStorage.setItem(key + 'Lock', String((new Date()).getTime()));
    const data = JSON.parse(localStorage.getItem(key) || default_value);
    const res = func(data);
    if (apply && res) {
        localStorage.setItem(key, JSON.stringify(res));
    }
    localStorage.setItem(key + 'Lock', '');
    return res;
}

// здесь я допустил ошибку: нужно использовать не localStorage, а chrome.local.storage. погугли про это, кучу гайдов найдёшь
function manageTasks() {
    wait('tasks', (tasks) => {
        for (const i in tasks) {
            const repeat_url_index = repeat_urls.indexOf(tasks[i].url)
            if (tasks[i].status === 'pending' || repeat_url_index + 1) {
                if (tasks[i].status === 'pending') {
                    tasks[i].status = 'started';
                    localStorage.setItem('tasks', JSON.stringify(tasks));
                } else {
                    delete repeat_urls[repeat_url_index];
                }
                chrome.tabs.create({
                    url: tasks[i].url,
                    active: false,
                }, (tab) => {
                    chrome.scripting.executeScript({
                        target: {tabId: tab.id},
                        func: () => {
                            // Тут уже начинается магия скрейпинга через chrome extensions. эта функция уже будет в другой вкладке, и к глобальным переменным этого скрипта доступа больше не будет
                            // Её можно вынести в отдельный файл
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
                            // Получаем задачу (ведь доступа к глобальным переменным больше нет)
                            chrome.runtime.onMessage.addListener((task_id, sender, sendResponse) => {
                                sendResponse('OK');
                                console.log(task_id);
                                let task = null, key = null;
                                const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
                                for (const i in tasks) {
                                    if (tasks[i].id === task_id) {
                                        task = tasks[i];
                                        key = i;
                                        break;
                                    }
                                }
                                // И пошёл скрейпинг
                                // Помни! Нужно заменить localStorage на chrome.local.storage
                                console.log('ok1');
                                if (!task || !key) {
                                    tasks[key].status = 'nodata';
                                    return;
                                }
                                console.log('ok2', task, key);
                                const list_courses = document.querySelector('#courselisting-expander > div');
                                if (!list_courses) {
                                    tasks[key].status = 'nodata';
                                    return;
                                }
                                console.log('ok3');
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
                                console.log('ok4', data);
                                let url;
                                for (const item of data) {
                                    url = `https://sellercentral.amazon.com/learn/courses?ref_=su_course_accordion&moduleId=${item.module_id}&courseId=${item.course_id}&modLanguage=English`;
                                    const f = () => {
                                        chrome.tabs.query({}, (tabs) => {
                                            console.log('ok5', tabs);
                                            // ограничитель на количество вкладок
                                            if (tabs.length > 12) {
                                                return setTimeout(f, 1000);
                                            }
                                            // открываем вкладку для каждого модуля каждого курса
                                            chrome.tabs.create({
                                                url: url,
                                                active: false,
                                            }, (tab) => {
                                                chrome.scripting.executeScript({
                                                    target: {tabId: tab.id},
                                                    func: () => {
                                                        function getRandomInt(min, max) {
                                                            const minCeiled = Math.ceil(min);
                                                            const maxFloored = Math.floor(max);
                                                            return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled); // The maximum is exclusive and the minimum is inclusive
                                                        }
                                                        // parsing page body with data
                                                        const f = (i = 0) => {
                                                            const yt_video = document.querySelector('iframe#module-video');
                                                            const internal_video = document.querySelector('div#module-video > .airy > .airy-renderer-container > video');
                                                            let pdf_document = document.querySelector('div#module-document');
                                                            const details = document.querySelector('div.module-details.a-grid-top');
                                                            if (!yt_video && !internal_video && !pdf_document && !details) {
                                                                return setTimeout(f, 1000, ++i);
                                                            }
                                                            let data = {};
                                                            if (yt_video) {
                                                                data.yt_video = yt_video.getAttribute('src');
                                                            }
                                                            if (internal_video) {
                                                                data.video = internal_video.getAttribute('src');
                                                            }
                                                            if (pdf_document) {
                                                                data.document = pdf_document.getAttribute('data-src-english');
                                                            } else if ((pdf_document = document.querySelector('object#doc-preview'))) {
                                                                data.document = pdf_document.getAttribute('data');
                                                            }
                                                            if (details) {
                                                                data.details = details.innerText.trim();
                                                            }
                                                            // а вот и отправка на эндпоинт (возможно пока будет работать некорректно, я давно проверял)
                                                            fetch('http://195.201.194.213:8832/sellercentral/add', {
                                                                method: 'PUT',
                                                                body: JSON.stringify(data),
                                                            }).then(res => {res.json().then(data => {
                                                                console.log(data);
                                                            })}).catch(reason => {
                                                                console.log(reason);
                                                            });
                                                        };
                                                        setTimeout(f, getRandomInt(9, 999));
                                                    },
                                                });
                                            });
                                        });
                                    };
                                    f();
                                }
                                // end body
                                tasks[key].status = 'done';
                                localStorage.setItem('tasks', JSON.stringify(tasks));
                            });
                        },
                    });
                    sendMessageToTab(tab.id, tasks[i].id, 500, 1000);
                });
            }
        }
        setTimeout(manageTasks, 1000);
    }, false);
}

// Эьто я хотел сделать табличку с текущими скрейпингами, но на текущем этапе это необязательно
function sellerCentralTask(url, status = 'pending', write = true) {
    const id = scrap_process_table.getElementsByTagName('tr').length;
    const row = document.createElement('tr');
    const col_url = document.createElement('td');
    const col_status = document.createElement('td');
    row.appendChild(col_url);
    row.appendChild(col_status);
    row.id = '' + id;
    scrap_process_table.appendChild(row);
    col_url.innerText = url;
    col_status.innerText = status;
    if (write) {
        wait('tasks', (tasks) => {
            tasks.push({'id': id, 'url': url, 'status': 'pending'});
            return tasks;
        }, true);
    }
}

function sendMessageToTab(tabId, message, retryDelay = 500, maxRetries = 100) {
    let attempts = 0;

    function sendMessage() {
        ++attempts;
        chrome.tabs.sendMessage(tabId, message, function(response) {
            if (chrome.runtime.lastError) {
                if (attempts < maxRetries) {
                    console.error(`Ошибка при отправке сообщения: ${chrome.runtime.lastError.message}. Повторная попытка ${attempts} из ${maxRetries}...`);
                    setTimeout(sendMessage, retryDelay);
                } else {
                    console.error(`Не удалось отправить сообщение после ${maxRetries} попыток.`);
                }
            } else {
                console.log('Сообщение отправлено успешно:', response);
            }
        });
    }

    sendMessage();
}
// Заменить на chrome.local.storage!!!
if (typeof JSON.parse(localStorage.getItem('tasks')).length === 'undefined') {
    localStorage.setItem('tasks', '[]');
}
for (const item of JSON.parse(localStorage.getItem('tasks') || '[]')) {
    sellerCentralTask(item.url, item.status, false);
    chrome.tabs.query({url: item.url}, (tabs) => {
        if (!tabs.length) {
            repeat_urls.push(item.url);
        }
    });
}

manageTasks();
