function checkRegisterAbility() {
    const check1 = (resolve, reject, limit, count = 0) => {
        if (!document.querySelector('#wwpp-container-inner > svg')) {
            return setTimeout(check2, 250, resolve, reject, limit);
        }
        if (count < limit) setTimeout(check1, 100, resolve, reject, limit, count + 1);
        else reject();
    };
    const check2 = (resolve, reject, limit, count = 0) => {
        const h1 = document.getElementsByTagName('h1');
        for (const h1Element of h1) {
            if (h1Element.textContent.includes('Server error')) reject('Unknown error: server error');
            if (h1Element.textContent.includes('Registration is closed at the moment')) reject('Error: registration is closed');
            if (h1Element.textContent.includes('Welcome')) return setTimeout(resolve, 200, 0);
            if (h1Element.textContent.includes('Enter your details')) return setTimeout(resolve, 200, 1);
        }
        if (count < limit) setTimeout(check2, 100, resolve, reject, limit, count + 1);
        else reject('Unknown error: no h1 tag foun');
    };

    return new Promise((resolve, reject) => {
        check1(resolve, reject, 30);
    });
}

function checkRegisterErrors() {
    const errorMessages = document.querySelectorAll('[data-cy="error-message"]');
    if (errorMessages.length) throw new Error('Error: ' + errorMessages[0].textContent.trim());
}

async function insertDataAndSubmit(firstName, lastName, phoneNumber, email) {
    const data = {
        form_phone: phoneNumber,
        form_firstName: firstName,
        form_lastName: lastName,
        form_email: email,
    };

    const [select] = document.getElementsByTagName('select');
    if (!select) throw new Error('Unknown error: no select found');

    const options = select.getElementsByTagName('option');
    let found = false;
    for (const option of options) {
        if (option.value === 'US') {
            option.selected = true;
            found = true;
            break;
        }
    }
    if (!found) throw new Error('Unknown error: no US select found');

    const inputs = document.getElementsByTagName('input');
    let written = false;
    for (let i = 0; i < 100 && !written; ++i) {
        for (const input of inputs) {
            if (data[input.id]) await simulateRealisticInput(input, data[input.id]);
            else if (data[input.name]) await simulateRealisticInput(input, data[input.name]);
            else if (input.type === 'email') await simulateRealisticInput(input, email);
            else if (input.id.indexOf('full') > -1 || input.name?.indexOf('full') > -1)
                await simulateRealisticInput(input, firstName + ' ' + lastName);
            else if (input.id.indexOf('name') > -1 || input.name?.indexOf('name') > -1)
                await simulateRealisticInput(input, firstName);
            await new Promise(r => setTimeout(r, 25));
            written = Boolean(input.value);
        }
        await new Promise(r => setTimeout(r, 50));
    }

    await pressJoinButton();
}

async function pressJoinButton() {
    const buttons = document.getElementsByTagName('button');
    if (!buttons || !buttons.length || !buttons[0]) return false;
    await humanClick(buttons[0]);
    return true;
}

async function getRegistrationStatus(firstName, lastName, phoneNumber, email) {
    console.log('start!');
    const stage = await checkRegisterAbility();
    console.log(stage);
    checkRegisterErrors();
    console.log('OK!');
    if (stage) await insertDataAndSubmit(firstName, lastName, phoneNumber, email);
    else if (!await pressJoinButton()) throw new Error('Unknown error: can not press joinButton');
    console.log('OK2');
    return { success: true, stage: stage };
}