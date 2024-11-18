// const base_url = 'http://195.201.194.213:8830';
// const base_url = 'http://localhost:8830';
const base_url = '';

function add_task(script, task_alias, data, callback = null) {
    let url = base_url + '/tasks/add/' + script;
    data.alias = task_alias;
    $.post(url, JSON.stringify(data)).done(function (data, status, jqXhr) {
        const new_element = $('<li>');
        new_element.prop('data-bs-task-id', data['id']).appendTo('#tasks');
        if (callback) {
            callback(data);
        }
    });
}

function delete_task(task_id) {
    $.ajax({
        url: base_url + '/tasks/delete/' + String(task_id),
        type: 'DELETE',
    }).done(function () {
        $('#tasks li[data-bs-task-id="' + String(task_id) + '"]').remove();
    });
}

function set_task_content(data) {
    if (data.success === null) {
        data.script = 'waiting';
    }
    const tab = $(`.tab[data-bs-script="${data.script}"]`);

    if (data.success !== null && data.result) {
        if (data.script === 'collect_departments') {
            data.result['asins-links'] = '';
            for (let i = 0; i < data.result.asins.length; ++i) {
                data.result['asins-links'] += `<tr><td>${data.result.asins[i]}</td><td><a href="${data.result.links[i]}">${data.result.links[i]}</a></td></tr>`;
            }
        } else if (data.script === 'collect_reviews') {
            data.result['asins-count'] = '';
            for (let i = 0; i < data.result.asins.length; ++i) {
                data.result['asins-count'] += `<tr><td>${data.result.asins[i]}</td><td>${data.result.count[i]}</td></tr>`;
            }
        } else if (data.script === 'collect_products') {
            const asins_list = data.result['asins'];
            data.result['asins'] = '';
            for (let i = 0; i < asins_list.length; ++i) {
                data.result['asins'] += `<li>${asins_list[i]}</li>`;
            }
            const media_list = data.result['media'];
            data.result['media'] = '';
            for (let i = 0; i < media_list[0].length; ++i) {
                data.result['media'] += `<img src="${media_list[0][i]}"}>`;
            }
            for (let i = 0; i < media_list[1].length; ++i) {
                data.result['media'] += `<video src="${media_list[0][i]}"}></video>`;
            }
        }
        let item;
        for (let key in data.result) {
            item = tab.find(`[data-bs-key=${key}]`);
            if (item) {
                item.html(data.result[key]);
                if (typeof item.attr('href') !== 'undefined') {
                    item.attr('href', data.result[key]);
                }
            }
        }
    }

    $(`.tab:not([data-bs-script="${data.script}"])`).removeClass('active');
    tab.addClass('active');

    $('.nav-link').removeClass('active').attr('aria-selected', false);
    $('.tab-pane').removeClass('show').removeClass('active');
    $('#task-content').addClass('show').addClass('active');
}

function formatTime(ms) {
    // Получение часов, минут и секунд из миллисекунд
    let seconds = Math.floor(ms / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(minutes / 60);

    // Обеспечение, что остаток деления используется для минут и секунд
    seconds = seconds % 60;
    minutes = minutes % 60;

    // Добавление ведущего нуля, если число меньше 10
    hours = hours.toString().padStart(2, '0');
    minutes = minutes.toString().padStart(2, '0');
    seconds = seconds.toString().padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
}

function update() {
    $.get(base_url + '/tasks/get').done(function (data) {
        $('ul#tasks').html(' ');
        for (let i = 0; i < data.length; ++i) {
            let taskPanel = $('#tasks');
            let taskTemplate = $(document.getElementById('task-template').firstElementChild.cloneNode(true));
            $(taskTemplate.find('a')[0]).attr('data-bs-task-id', data[i]['id']).click(function () {
                $.get(base_url + '/tasks/get/' + $(this).attr('data-bs-task-id')).done(set_task_content);
            });
            $(taskTemplate.find('.task-content')[0]).text(data[i]['alias']);
            $(taskTemplate.find('.task-progress-text')[0]).text(String(data[i]['progress'] ?? 0) + '%');
            $(taskTemplate.find('.task-progress')[0]).css('width', String(data[i]['progress'] ?? 0) + '%');
            $(taskTemplate.find('.task-remove')[0]).attr('data-bs-task-id', data[i]['id']).click(function (e) {
                e.preventDefault();
                delete_task($(this).attr('data-bs-task-id'));
            })
            let time = (data[i]['ended_at'] ? (new Date(data[i]['ended_at'])) : Date.now()) - (new Date(data[i]['started_at']))
            if (time) {
                $(taskTemplate.find('.task-time')).text(formatTime(time));
            }
            if (data[i]['progress'] >= 100) {
                $(taskTemplate).addClass(data[i]['success'] ? 'success' : 'error');
            } else {
                $(taskTemplate).removeClass('success').removeClass('error');
            }
            taskPanel.append(taskTemplate);

            /*const root = $('<li>').attr('data-bs-task-id', data[i]['id']).appendTo('#tasks');
            const lnk = $('<a>').attr('href', '#').attr('data-bs-task-id', data[i]['id']).click(function () {
                $.get(base_url + '/tasks/get/' + $(this).attr('data-bs-task-id')).done(set_task_content);
            }).text(data[i]['alias']).appendTo(root);
            $('<span>').addClass('text-progress').html('&emsp;' + String(data[i]['progress'] ?? 0) + '%').appendTo(lnk);
            $('<button>').addClass('close').html('&times;').attr('data-bs-task-id', data[i]['id']).click(function () {
                delete_task($(this).attr('data-bs-task-id'));
            }).appendTo(root);
            $('<div>').addClass('progress').css('width', String(data[i]['progress'] ?? .5) + '%').appendTo(root);
            if (data[i]['progress'] >= 100) {
                root.addClass(data[i]['success'] ? 'success' : 'error');
            } else {
                root.removeClass('success').removeClass('error');
            }*/
        }
    }).fail(function (jqXhr) {
    });
}

let interval_update = setInterval(update, 5000);

$(document).ready(function () {
    $('form[action]:not([data-bs-special])').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        const url = base_url + $(this).attr('action');
        $.post(url, JSON.stringify(data));
        return false;
    });

    function wait(req, success, delay = 1000) {
        return function (data) {
            if (!data || data['success'] === null) {
                return setTimeout(function () {
                    return req().done(wait(req, success, delay))
                }, delay);
            }
            success(data);
        }
    }

    //
    $('form[action="/cmd/alias/get_all"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        const limit = Boolean(Number(data.limit));
        const unique_brands = Boolean(Number(data.unique_brands));
        const amazon_aspects = Boolean(Number(data.amazon_aspects));
        const task_name = data.alias;
        const category = data.category;
        const client_alias = data.client_alias;
        const bsr_link = data.bsr_link;
        const target_asin = data.target_asin;
        const count = Boolean(Number(data.only_top5)) ? 5 : 30;
        add_task('collect_departments', (task_name ?? 'Get all') + '#bsr', {
            bsr: bsr_link,
            limit: limit,
            unique_brands: unique_brands,
            count: count,
        }, function (data) {
            wait(function () {
                return $.get(base_url + '/tasks/get/' + data)
            }, function (data) {
                let usual_asins = [];
                let target_found = false;
                for (let i in data['result']['asins']) {
                    if (data['result']['asins'][i] === target_asin) {
                        target_found = true;
                        continue;
                    }
                    usual_asins.push(data['result']['asins'][i]);
                }
                if (!target_found) {
                    data['result']['asins'].push(target_asin);
                }
                add_task('collect_products', (task_name ?? 'Get all') + '#products', {
                    asins: usual_asins,
                    collect_aspects: amazon_aspects,
                });
                if (target_asin) {
                    add_task('collect_products', (task_name ?? 'Get all') + '#target', {
                        asins: [target_asin],
                        collect_aspects: amazon_aspects,
                        need_collect_media: true,
                    });
                }
                add_task('collect_reviews', (task_name ?? 'Get all') + '#reviews', {
                    asins: data['result']['asins'],
                    current_format: true,
                });
                $.post(base_url + '/cmd/category/set', JSON.stringify({
                    cat_name: category,
                    client_name: client_alias,
                    asins: data['result']['asins'],
                    top5_asins: data['result']['asins'].slice(0, 5),
                    target: target_asin || null,
                }))
            })();
        });
    });
    $('form[action="/cmd/alias/collect_all_info"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        const amazon_aspects = Boolean(Number(data.amazon_aspects));
        const task_name = data.alias;
        const category = data.category;
        const client_alias = data.client_alias;
        const asins = [...data.asins.matchAll(/B0[A-Z0-9]{8}/g)];
        const target_asin = data.target_asin;

        let all_asins = [];
        let usual_asins = [];
        let target_found = false;
        for (let i in asins) {
            if (asins[i][0] === target_asin) {
                target_found = true;
                continue;
            }
            usual_asins.push(asins[i][0]);
            all_asins.push(asins[i][0]);
        }
        if (!target_found) {
            all_asins.push(target_asin);
        }

        add_task('collect_products', (task_name ?? 'Get info') + '#prods', {
            asins: usual_asins,
            collect_aspects: amazon_aspects,
        });
        if (target_asin) {
            add_task('collect_products', (task_name ?? 'Get info') + '#target', {
                asins: [target_asin],
                collect_aspects: amazon_aspects,
                need_collect_media: true,
            });
        }
        add_task('collect_reviews', (task_name ?? 'Get info') + '#revs', {
            asins: all_asins,
            current_format: true,
        });
        $.post(base_url + '/cmd/category/set', JSON.stringify({
            cat_name: category,
            client_name: client_alias,
            asins: all_asins,
            top5_asins: [],
            target: target_asin || null,
        }));
    });
    $('form[action="/cmd/alias/collect_target"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }

        const amazon_aspects = Boolean(Number(data.amazon_aspects));
        const task_name = data.alias;
        const target_asin = data.target_asin;

        if (target_asin) {
            add_task('collect_products', (task_name ?? 'Get target'), {
                asins: [target_asin],
                collect_aspects: amazon_aspects,
                need_collect_media: true,
            });
        }
    });
    $('form[action="/cmd/alias/get_bsr"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        const limit = Boolean(Number(data.limit));
        const unique_brands = Boolean(Number(data.unique_brands));
        const task_name = data.alias;
        const bsr_link = data.bsr_link;
        const count = Boolean(Number(data.only_top5)) ? 5 : 30;
        add_task('collect_departments', (task_name ?? 'Get all'), {
            bsr: bsr_link,
            limit: limit,
            unique_brands: unique_brands,
            count: count,
        });
    });
    //
    $('form[action="/cmd/reviews/count"]').submit(function (e) {
        e.preventDefault();
        $.get(base_url + '/cmd/reviews/count', $(this).serialize()).done(function (data) {
            $('#count-reviews-result').text(data[2] + ': ' + data[0] + '/' + data[1])
        });
    });
    //
    $('form[action="/cmd/products/get"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        $.get(base_url + '/cmd/products/get/' + data['asin']).done(function (data) {
            $('#product-info > .data-table > tbody > tr').each(function (i, el) {
                const all_cells = $(el).find('td');
                let key = all_cells.get(0).innerText;
                const note_item = $(el).find('td > span').get(0);
                if (note_item) {
                    key = key.split(note_item.innerText || '').join('').trim();
                }
                let data_cell = all_cells.eq(1);
                if (data_cell.find('div.readmoreable').length > 0) {
                    data_cell = data_cell.find('div.readmoreable');
                }
                data_cell = data_cell.get(0);
                if (data[key] instanceof Array) {
                    data[key] = data[key].join(' | ');
                } else if (typeof data[key] === 'object') {
                    data_cell.innerHTML = '<ul>';
                    for (let item in data[key]) {
                        data_cell.innerHTML += '<li>' + item + ': ' + data[key][item] + '</li>';
                    }
                    if (data_cell.innerHTML.length > 9) {
                        data_cell.innerHTML += '</ul>';
                    } else {
                        data_cell.innerHTML = ' - ';
                    }
                    return;
                }
                if (typeof data[key] === 'undefined' || !data[key]) {
                    data_cell.innerText = ' - ';
                    return;
                }
                data_cell.innerText = data[key];
            });
            $('.readmoreable').readmore({
                maxHeight: 100,
                moreLink: '<a href="#">Развернуть</a>',
                lessLink: '<a href="#">Свернуть</a>',
            });
        }).fail(function () {
            alert('This asin is not in database!')
            $('#product-info > .data-table > tbody > tr').each(function (i, el) {
                const all_cells = $(el).find('td');
                let data_cell = all_cells.eq(1);
                if (data_cell.find('div.readmoreable').length > 0) {
                    data_cell = data_cell.find('div.readmoreable');
                }
                data_cell = data_cell.get(0);
                data_cell.innerHTML = '';
            });
            $('.readmoreable').readmore({
                maxHeight: 100,
                moreLink: '<a href="#">Развернуть</a>',
                lessLink: '<a href="#">Свернуть</a>',
            });
        });
    });
    //
    $('form[action="/cmd/category/set"]').submit(function (e) {
        e.preventDefault();
        const raw_data = $(this).serializeArray();
        let data = {};
        for (let i in raw_data) {
            data[raw_data[i].name] = raw_data[i].value;
        }
        $.post(base_url + '/cmd/category/set', JSON.stringify({
            cat_name: data['category'],
            client_name: data['alias-client'],
            asins: data.asins,
            top5_asins: [],
        })).done(function (data) {
        });
    });

})