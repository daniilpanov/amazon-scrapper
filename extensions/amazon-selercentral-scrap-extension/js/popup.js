import Scraper from "./scraper.js";
import Parser from "./parser.js";

const scraper = new Scraper();
const parser = new Parser();

const amazonUrl = 'https://sellercentral.amazon.com/';
const endpoint = 'http://195.201.194.213:8832/sellercentral/add';
const scrapeButton = document.getElementById('toParseButton');
const pagesCounter = document.getElementById('pagesCounter');
const totalPagesCount = document.getElementById('totalPagesCount');

scrapeButton.addEventListener('click', async (event) => {
    scrapeButton.disabled = true;
    scrapeButton.innerHTML = 'Wait...';
    pagesCounter.innerHTML = '0';
    let totalPages = 0;

    try {
        const tabs = await chrome.tabs.query({ currentWindow: true, active: true }); // получаю открытые вкладки
        const activeTabUrl = tabs[0].url;
        const activeTabId = tabs[0].id;

        if (activeTabUrl.includes(amazonUrl)) {
            let HTML = await scraper.getTabHTML(activeTabId);
            let DOM = await parser.parseDOM(HTML);

            const courseBoxes = DOM.querySelectorAll('.a-row.a-expander-container.a-expander-section-container.a-section-expander-container')
            const moduleBoxes = DOM.querySelectorAll('.module-box');
            const coursesData = {}; // здесь будут храниться элементы вида "ключ" (courseId): ["значение1", "значение2" ...] (массив состоящий из всех moduleId принадлежащих к этому курсу)"

            moduleBoxes.forEach(box => {
                const courseId = box.dataset.courseid;
                const moduleId = box.dataset.moduleid;

                // создаю массив для отдельного courseId, если его еще нет в объекте
                if (!coursesData[courseId]) {
                    coursesData[courseId] = [];
                }

                coursesData[courseId].push(moduleId);
                totalPages++;
            });

            totalPagesCount.innerHTML = totalPages;

            courseBoxes.forEach(box => {
                const courseId = box.id;
                const courseTitle = box.getAttribute('data-a-expander-name');
                coursesData[courseId].push(courseTitle);
            });

            await parseCoursesData(coursesData);
        } else {
            alert(`Wrong URL! It must starts with\n${amazonUrl}*`);
        }
    } catch (error) {
        console.error(error);
    } finally {
        scrapeButton.disabled = false;
        scrapeButton.innerHTML = 'Scrape';
    }
});

////

async function parseCoursesData(coursesData) {
    let counter = 0;
    for (const currCourse of Object.keys(coursesData)) {
        const courseTitle = coursesData[currCourse].at(-1);
        for (const currModule of coursesData[currCourse].slice(0, -1)) {
            const url = `https://sellercentral.amazon.com/learn/courses?ref_=su_course_accordion&moduleId=${currModule}&courseId=${currCourse}&modLanguage=English`;
            const newTab = await chrome.tabs.create({ url: url, active: false, /*autoDiscardable: false*/ });
            const pageHTML = await scraper.getTabHTML(newTab.id);
            const pageDOM = await parser.parseDOM(pageHTML);

            const moduleResultObject = {
                "media_link": "",
                "media_type": "",
                "course_name": courseTitle,
                "module_name": "",
                "course_id": currCourse,
                "module_id": currModule,
            };
            moduleResultObject.module_name = pageDOM.querySelector('#module-page-container > div.module-details > div:nth-child(1) > div.a-column.a-span8 > h2')?.textContent;

            const moduleYouTube = pageDOM.querySelector('#module-video')?.getAttribute('data-src-english');
            const moduleInternalVideo = pageDOM.querySelector('#airy-module-video')?.getAttribute('data-src-english');
            const moduleDocument = pageDOM.querySelector('#module-document')?.getAttribute('data-src-english');

            if (moduleYouTube) {
                moduleResultObject.media_link = moduleYouTube;
                moduleResultObject.media_type = "yt";
            }
            else if (moduleInternalVideo) {
                moduleResultObject.media_link = moduleInternalVideo;
                moduleResultObject.media_type = "int_video";
            }
            else if (moduleDocument) {
                moduleResultObject.media_link = moduleDocument;
                moduleResultObject.media_type = "pdf";
            }

            await sendData(moduleResultObject);

            // не стал убирать логи, может кому-то понадобятся. 
            // Посмотреть можно щелкнув ПКМ на значок расширения и выбрав "Inspect popup" внизу
            console.log("Медиа ссылка: ", moduleResultObject.media_link);
            console.log("Тип медиа: ", moduleResultObject.media_type);
            console.log("Курс: ", moduleResultObject.course_name);
            console.log("Модуль: ", moduleResultObject.module_name);
            console.log("ID курса: ", moduleResultObject.course_id);
            console.log("ID модуля: ", moduleResultObject.module_id);
            console.log("----------------");

            await chrome.tabs.remove(newTab.id);

            counter += 1;
            pagesCounter.innerHTML = counter;

            // задержку добавил чтобы не грузить систему и безошибочно вытаскивать html
            await new Promise(resolve => setTimeout(resolve, 25));
        }
    }
}

async function sendData(data) {
    const sendDelay = 500;
    const maxAttemptsCount = 50;
    let attempts = 0;

    while (attempts < maxAttemptsCount) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok && response.status === 201) {
                console.log('Данные отправлены успешно, статус код: ', response.status);
                return;
            } else {
                throw new Error('Получен статус код: ', response.status)
            }
        } catch (error) {
            attempts++;
            console.log(`Ошибка при отправке данных, новая попытка через: ${sendDelay}ms...`);
            await new Promise(resolve => setTimeout(resolve, sendDelay));
        }
    }

    console.log(`Совершено ${attempts} попыток отправки, что является максимальным количеством.`);
}
