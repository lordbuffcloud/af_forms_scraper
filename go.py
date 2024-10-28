from af_forms_scraper import AFFormsScraper
import logging

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting scraper...")
    
    base_urls = [
        "https://www.e-publishing.af.mil/Product-Index/#/?view=pubs&orgID=10141&catID=1&series=-1&modID=449&tabID=131",
        "https://www.e-publishing.af.mil/Product-Index/#/?view=form&orgID=10141&catID=8&low=-1&high=-1&modID=449&tabID=131",
        "https://www.e-publishing.af.mil/Product-Index/#/?view=cat&catID=14"
    ]
    
    try:
        scraper = AFFormsScraper(base_urls)
        scraper.run()
    except Exception as e:
        logger.error(f"Error running scraper: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
