import datetime

from models import ProductFull, AmazonRequest

dirname = datetime.datetime.now().strftime('%Y-%m-%d')

product = 'https://www.amazon.com/Sugarbear-Vitamin-Gummies-Chewable-Supplement/dp/B019ZZB3O2/ref=sr_1_8?crid=1A032JAVNFCZ4&keywords=hair+gummies&qid=1680186819&sprefix=hair+gummies%2Caps%2C146&sr=8-8'
browser_inst = AmazonRequest(url=product)
ProductFull(url=product, browser=browser_inst)
browser_inst.browser.quit()
