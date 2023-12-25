import asyncio
import os.path

from pyppeteer import launch


async def main():
    browser = await launch({'headless': False})
    page = await browser.newPage()

    dimensions = await page.evaluate('''() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }''')

    print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    # await page.goto('https://nowsecure.nl')
    # await asyncio.sleep(20)
    # await page.screenshot(path=os.path.abspath('./test.png'), type='png')
    await page.goto('https://junglescout.com')
    await asyncio.sleep(100)
    inputs = await page.querySelectorAll('[role="form"] input')
    await asyncio.sleep(.2)
    await inputs[0].type('ilgar.talibov@gmail.com')
    await asyncio.sleep(.2)
    await inputs[1].type('02081991')
    await asyncio.sleep(.2)
    await page.click('[role="form"] button')
    await asyncio.sleep(20)
    await page.screenshot(path=os.path.abspath('./test.png'), type='png')
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
