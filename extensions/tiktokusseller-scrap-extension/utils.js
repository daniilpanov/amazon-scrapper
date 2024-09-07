async function scrollToTheEnd() {
    const rootEl = document.getElementsByClassName('arco-table-body');
    if (!rootEl || !rootEl.length) {
        return false;
    }

    const all_rows = [...rootEl[0].getElementsByTagName('tr')];
    if (!all_rows || !all_rows.length) {
        return false;
    }

    all_rows[all_rows.length - 1].scrollIntoView();

    return new Promise(async (resolve, reject) => {
        for (let i = 0; i < 100; ++i) {
            if (document.querySelectorAll('.arco-table-body table tr').length > all_rows.length) {
                return resolve();
            }
            await new Promise((r) => setTimeout(r, 100));
        }
        reject();
    });
}

// Функция для скачивания CSV файла
function downloadCSV(csvString, filename) {
    // Создание Blob из CSV строки
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });

    // Создание URL для Blob
    const url = URL.createObjectURL(blob);

    // Создание временной ссылки для скачивания
    const a = document.createElement('a');
    a.href = url;
    a.setAttribute('download', filename);

    // Добавление ссылки в документ
    document.body.appendChild(a);

    // Клик по ссылке для инициирования загрузки
    a.click();

    // Удаление ссылки из документа
    document.body.removeChild(a);

    // Освобождение URL объекта
    URL.revokeObjectURL(url);
}

