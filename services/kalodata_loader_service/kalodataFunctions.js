async function getDaysConfig() {
    const allLastDaysResponse = await fetch('https://www.kalodata.com/api/allLastDay');
    const allLastDays = (await allLastDaysResponse.json())?.data || [];
    let dateConfig = {};
    for (let data of allLastDays) {
        if (data.country === 'US') {
            dateConfig.endDateStr = data.lastDay;
            dateConfig.endDate = new Date(data.lastDay);
            dateConfig.startDate = new Date(dateConfig.endDate);
            break;
        }
    }
    return dateConfig;
}

function getDateShift(date, shiftLeft, str = true) {
    const d = new Date(date);
    d.setDate(d.getDate() - shiftLeft);
    return str ? d.toISOString().split('T')[0] : d;
}
