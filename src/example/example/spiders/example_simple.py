from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

class Spider(Spider): 
    name = "my_spider"
    allowed_domain = []
    start_urls = ["https://example.com"]

    cookies = [
        {"name": "cookie_name_1", "value":"cookie_value_1","domain": "https://example.com" ,"path": "/" },
        {"name": "cookie_name_2", "value":"cookie_value_2","domain": "https://example.com" ,"path": "/" },
    ]

    def should_abort_request(request):
        return (
            request.resource_type == "image"
            or "google" in request.url
            or ".jpg" in request.url 
            or ".png" in request.url 
            or ".css" in request.url # careful with this option
        )

    custom_settings={
        'PLAYWRIGHT_ABORT_REQUEST' : should_abort_request,
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS' : None,
        'PLAYWRIGHT_CONTEXTS': {
            'context_cookies':{
                'storage_state': {
                        'cookies': cookies,
                },
            },
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                meta={
                    "playwright" : True,
                    "playwright_include_page" : True,
                    "playwright_context": "context_cookies",
                },
                callback=self.parse,
                errback=self.errback
            )
    
    async def parse(self):
        # get the page from the response
        page = response.meta["playwright_page"]

        # see if cookies were received
        storage_state = await page.context.storage_state()
        print('Page cookies: ', storage_state['cookies'])
        
        # some wait method to wait for 
        # the desired load state 
        await page.wait_for_load_state()

        # get page content
        content = await page.content()
        # transform into a Selector
        selector = Selector(text=content)
        # extract some data
        data1 = selector.xpath('.//a[@class="data"]/text()')
        
        # extract same data using Playwright
        data2 = await page.locator(".data").inner_text()
        
        # get a Locator
        button = page.get_by_role("button")
        # make an action
        await button.click()
        # wait method
        await page.wait_for_timeout(3*1000)

        ##################
        # do other stuff #
        ##################
        
        # some other dynamic actions
        await page.go_back()
        await page.wait_for_timeout(3*1000)

        # close the page and the context
        
        await page.close()
        await page.context.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
    


