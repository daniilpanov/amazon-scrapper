const base_url = window.location.protocol + '//' + window.location.hostname + ':8832';

$(document).ready(() => {
    $('form[action]').submit(function (e) {
        e.preventDefault()
        const data = {};
        for (const i of $(this).serializeArray()) {
            data[i.name] = i.value;
        }
        fetch(base_url + $(this).attr('action'), {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
        }).then(res => {
            if (res.status > 299) {
                res.text().then(txt => {
                    alert('Fail! ' + res.statusText + ' : ' + txt);
                });
            } else {
                alert('Task sent successful!');
            }
        });
    });
});
