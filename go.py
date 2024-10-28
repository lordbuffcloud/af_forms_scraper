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
    
    try:
        scraper = AFFormsScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Error running scraper: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
