from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

class Spider(Spider): 
    name = "example_quotes"
    allowed_domain = []
    start_urls = ["https://quotes.toscrape.com/page/1/"]
    page_num = 1

    custom_settings={
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS' : None,
    }

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            meta={
                "playwright" : True,
                "playwright_include_page" : True,
            },
            callback=self.parse,
            errback=self.errback
        )
    
    async def parse(self, response):
        # get the page from the response
        page = response.meta["playwright_page"]
        
        # some wait method to wait for 
        # the desired load state 
        await page.wait_for_load_state()

        # get page content
        content = await page.content()
        # transform into a Selector
        selector = Selector(text=content)

        # extract some data
        quotes = await page.locator('div.quote').all()
        for quote in quotes:
            # get a Locator
            button = quote.get_by_text('(about)')
            # make an action
            await button.click()
            # wait method
            await page.wait_for_timeout(3*1000)

            # extract some data
            born_date = await page.locator('.author-born-date').inner_text()
            print('\n ######################################################\n',
                'The author of this quote was born on: ', born_date, '\n',
                '######################################################\n')

            # go back to main page
            await page.go_back()
            await page.wait_for_timeout(3*1000)

        # get next url from the content
        next_url = selector.xpath('.//li[@class="next"]//@href').get()

        if next_url :
            # yield a new Request using the same page
            next_url = "https://quotes.toscrape.com" + next_url
            yield Request(
                url= next_url,
                meta={
                    "playwright" : True,
                    "playwright_include_page" : True,
                    "playwright_page": page,
                    },
                callback=self.parse,
                errback=self.errback
            )
        else:
            # close the page at the end
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
    


