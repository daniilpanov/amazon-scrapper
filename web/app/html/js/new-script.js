const base_url = window.location.protocol + '//' + window.location.hostname + ':8832';

$(document).ready(() => {
    $('form[action="/cmd/alias/products/collect"]').submit((e) => {
        e.preventDefault();
        let data = {};
        for (const i of $('form[action="/cmd/alias/products/collect"]').serializeArray()) {
            data[i.name] = i.value;
        }
        fetch(base_url + '/cmd/alias/products/collect', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
        });
    });
    $('form[action="/cmd/alias/get_all"]').submit((e) => {
        e.preventDefault();
        let data = {};
        for (const i of $(e.target).serializeArray()) {
            data[i.name] = i.value;
        }
        fetch(base_url + '/cmd/alias/bsr/collect', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
        });
    });
});
