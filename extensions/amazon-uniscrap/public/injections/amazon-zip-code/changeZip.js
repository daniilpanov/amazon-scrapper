async function changeZipCode(zipCode) {
    try {
        await new Promise(r => setTimeout(r, 3000));
        document.getElementById('nav-global-location-popover-link').click();
        await new Promise(r => setTimeout(r, 1000));
        document.getElementById('GLUXZipUpdateInput').value = zipCode;
        document.getElementById('GLUXZipUpdate-announce').click();
        await new Promise(r => setTimeout(r, 1000));
        document.getElementById('GLUXConfirmClose').click();
        document.querySelector('[name=glowDoneButton]').click();
        return true;
    } catch (e) {
        return false;
    }
}
