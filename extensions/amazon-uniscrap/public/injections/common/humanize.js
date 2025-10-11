async function simulateRealisticInput(inputElement, text) {
    // Устанавливаем фокус
    inputElement.focus();

    // Создаем событие paste
    const pasteEvent = new Event('paste', {
        bubbles: true,
        cancelable: true,
        composed: true
    });

    // Добавляем данные в буфер обмена
    pasteEvent.clipboardData = {
        getData: () => text
    };

    // Триггерим события в правильном порядке
    inputElement.dispatchEvent(pasteEvent);

    // Обновляем значение поля
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        HTMLInputElement.prototype,
        'value'
    ).set;

    nativeInputValueSetter.call(inputElement, text);

    // Триггерим все необходимые события
    inputElement.dispatchEvent(new Event('input', { bubbles: true }));
    inputElement.dispatchEvent(new Event('change', { bubbles: true }));

    // Добавляем небольшую задержку для правдоподобности
    await new Promise(r => setTimeout(r, 200));
}

async function humanScroll(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest'
    });
}

async function humanClick(element, { x = 0, y = 0, spread = 3 } = {}) {
    const rect = element.getBoundingClientRect();
    const baseX = rect.left + rect.width/2 + x;
    const baseY = rect.top + rect.height/2 + y;

    // Имитация "дрожания" руки
    const randomOffset = (max) => (Math.random() * max * 2) - max;

    // Генерируем цепочку событий
    const events = [
        { type: 'mouseover', delay: 100 },
        { type: 'mousemove', coordinates: [baseX, baseY], delay: 50 },
        { type: 'mousedown', coordinates: [baseX + randomOffset(spread), baseY + randomOffset(spread)] },
        { type: 'mouseup', coordinates: [baseX + randomOffset(spread), baseY + randomOffset(spread)], delay: 150 },
        { type: 'click', coordinates: [baseX, baseY], delay: 50 }
    ];

    for (const event of events) {
        await new Promise(resolve => {
            setTimeout(() => {
                const [clientX, clientY] = event.coordinates || [baseX, baseY];

                element.dispatchEvent(new MouseEvent(event.type, {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX,
                    clientY,
                    buttons: event.type === 'mousedown' ? 1 : 0
                }));

                resolve();
            }, event.delay || 0);
        });
    }

    element.dispatchEvent(new Event('transitionend', { bubbles: true }));
}