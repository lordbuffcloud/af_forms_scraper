import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urljoin
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class AFFormsScraper:
    def __init__(self, base_urls):
        self.base_urls = base_urls
        self.db_name = "af_forms.db"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup Selenium with webdriver_manager
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument("--disable-web-security")  # May help with CORS issues
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Add experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        # Set window size
        self.driver.set_window_size(1920, 1080)

    def setup_database(self):
        """Create SQLite database and tables"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS forms
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     form_number TEXT,
                     title TEXT,
                     description TEXT, 
                     category TEXT,
                     pdf_url TEXT,
                     last_updated TEXT)''')
        
        conn.commit()
        conn.close()

    def get_form_links(self):
        """Scrape all form links from the website using Selenium"""
        try:
            self.logger.info(f"Fetching page: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for the page to load
            wait = WebDriverWait(self.driver, 30)
            
            # Wait for table to load
            self.logger.info("Waiting for table to load...")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(3)  # Give JavaScript time to fully load
            
            forms = []
            current_page = 1
            total_pages = 179  # From the screenshot
            
            while current_page <= total_pages:
                self.logger.info(f"Processing page {current_page} of {total_pages}")
                
                # Get all rows in the table
                rows = self.driver.find_elements(By.TAG_NAME, "tr")
                self.logger.info(f"Found {len(rows)} rows on page {current_page}")
                
                # Process each row
                for row in rows:
                    try:
                        # Find PDF link in the row
                        pdf_links = row.find_elements(By.CSS_SELECTOR, "a[href*='.pdf'], a[href*='/publication/']")
                        
                        for link in pdf_links:
                            href = link.get_attribute('href')
                            
                            # Get all cells in the row
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) < 3:  # Skip header rows
                                continue
                                
                            form_info = {
                                'form_number': cells[0].text.strip(),  # First column
                                'title': cells[1].text.strip(),        # Second column
                                'pdf_url': href,
                                'category': "Air Force Forms",         # Default category
                                'description': f"Last Updated: {cells[2].text.strip()}"  # Using date as description
                            }
                            
                            if form_info['form_number']:
                                forms.append(form_info)
                                self.logger.info(f"Added form: {form_info['form_number']}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing row: {str(e)}")
                        continue
                
                # Go to next page if not on last page
                if current_page < total_pages:
                    try:
                        # Try to find and click the next page number
                        next_page = current_page + 1
                        next_page_element = self.driver.find_element(
                            By.XPATH, 
                            f"//a[contains(@class, 'paginate_button') and text()='{next_page}']"
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page_element)
                        time.sleep(1)
                        next_page_element.click()
                        time.sleep(3)  # Wait for new page to load
                        current_page = next_page
                    except Exception as e:
                        self.logger.error(f"Error navigating to next page: {str(e)}")
                        break
                else:
                    break
            
            return forms
            
        except Exception as e:
            self.logger.error(f"Error scraping forms: {str(e)}", exc_info=True)
            return []
        finally:
            self.driver.quit()

    def extract_form_number(self, text):
        """Extract form number from text using regex"""
        patterns = [
            r'(AF\s*\d+-\d+)',
            r'(AFTO\s*\d+-\d+)',
            r'(DD\s*\d+-\d+)',
            r'(SF\s*\d+-\d+)',
            r'(IMT\s*\d+-\d+)',
            r'(AF\s*FORM\s*\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return ''

    def get_category_selenium(self, element):
        """Get category using Selenium"""
        try:
            # Try to find the closest parent div with a heading
            parent = element.find_element(By.XPATH, "./ancestor::div[.//h2 or .//h3 or .//h4][1]")
            header = parent.find_element(By.XPATH, ".//h2 | .//h3 | .//h4")
            return header.text.strip()
        except:
            return "Uncategorized"

    def get_description_selenium(self, element):
        """Get description using Selenium"""
        try:
            # Try to find a description paragraph near the link
            desc = element.find_element(By.XPATH, "following::p[1]")
            return desc.text.strip()
        except:
            return ""

    def save_to_database(self, forms):
        """Save scraped form information to SQLite database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        for form in forms:
            # Check if the form already exists
            c.execute('SELECT id FROM forms WHERE form_number = ?', (form['form_number'],))
            if c.fetchone() is None:
                # Insert the form if it doesn't exist
                c.execute('''INSERT INTO forms 
                            (form_number, title, description, category, pdf_url, last_updated)
                            VALUES (?, ?, ?, ?, ?, datetime('now'))''',
                         (form['form_number'], form['title'], form['description'],
                          form['category'], form['pdf_url']))
        
        conn.commit()
        conn.close()

    def run(self):
        """Main execution method"""
        try:
            print("Setting up database...")
            self.setup_database()
            
            for url in self.base_urls:
                print(f"Scraping forms from {url}...")
                self.base_url = url
                forms = self.get_form_links()
                
                print(f"Found {len(forms)} forms")
                if forms:
                    self.save_to_database(forms)
                    print("Forms saved to database")
                else:
                    print("No forms found to save")
                
        except Exception as e:
            self.logger.error(f"Error in run method: {str(e)}", exc_info=True)
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

    def get_tab_title(self, tab_element):
        """Get the title/text of a tab"""
        try:
            return tab_element.get_attribute('title') or tab_element.text.strip() or "Uncategorized"
        except:
            return "Uncategorized"

    def process_links(self, links, tab=None):
        """Process a list of links and extract form information"""
        forms = []
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if not href or not text:
                    continue
                
                # Check if it's a PDF link or publication link
                if href and ('.pdf' in href.lower() or '/publication/' in href.lower()):
                    self.logger.info(f"Processing link: {text[:50]}...")
                    
                    form_info = {
                        'form_number': self.extract_form_number(text),
                        'title': text,
                        'pdf_url': href,
                        'category': self.get_tab_title(tab) if tab else "Uncategorized",
                        'description': self.get_description_selenium(link)
                    }
                    
                    if form_info['form_number']:
                        forms.append(form_info)
                        self.logger.info(f"Added form: {form_info['form_number']}")
            
            except Exception as e:
                self.logger.error(f"Error processing link: {str(e)}")
                continue
        
        return forms

def navigate_to_next_page(driver):
    try:
        # Wait for the next page link to be present
        next_page_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'page-link') and text()='2']"))
        )
        next_page_link.click()
    except Exception as e:
        print(f"Error navigating to next page: {e}")
        # Optionally, log the error or take a screenshot for debugging
        # driver.save_screenshot('error_screenshot.png')

# Example usage
if __name__ == "__main__":
    base_urls = [
        "https://www.e-publishing.af.mil/Product-Index/#/?view=pubs&orgID=10141&catID=1&series=-1&modID=449&tabID=131",
        "https://www.e-publishing.af.mil/Product-Index/#/?view=form&orgID=10141&catID=8&low=-1&high=-1&modID=449&tabID=131",
        "https://www.e-publishing.af.mil/Product-Index/#/?view=cat&catID=14"
    ]
    
    scraper = AFFormsScraper(base_urls)
    scraper.run()
