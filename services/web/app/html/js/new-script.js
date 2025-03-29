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
                    showNotification('Fail! ' + res.statusText + ' : ' + txt);
                });
            } else {
                showNotification('Task sent successful!');
            }
        });
    });
});

function showNotification(message) {
    const notification = document.getElementById('notifications');
    const toastEl = document.createElement('div');
    toastEl.className = 'toast';
    toastEl.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
    notification.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    setTimeout(function() {
        toast.hide();
        toastEl.parentNode.removeChild(toastEl);
    }, 5000);
}
