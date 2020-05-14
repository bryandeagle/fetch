SPIDER_SETTINGS = [
    {
        'endpoint': 'dmoz',
        'location': 'spider',
        'spider': 'DmozSpider',
        'scrapy_settings': {
            'ITEM_PIPELINES': {
                'pipelines.AddTablePipeline': 500
            }
        }
    }
]