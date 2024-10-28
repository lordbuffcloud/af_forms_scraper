# AF Forms Scraper

I got tired of the bad search engine on EPUBS and made a web scraper for extracting Air Force forms from the e-Publishing website and storing them in a SQLite database.

Going to use it for my site [BePubs](https://bepubs.glxy.dev).

## Features

- Scrapes form data including form number, title, description, category, and PDF URL.
- Stores the data in a SQLite database.
- Uses Selenium for web scraping.

## Requirements

- Python 3.x
- Google Chrome
- ChromeDriver

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/af-forms-scraper.git
   cd af-forms-scraper
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have Google Chrome installed and the version matches the ChromeDriver.

## Usage

1. Run the scraper:

   ```bash
   python go.py
   ```

2. The forms will be saved to `af_forms.db`.

## Files

- `af_forms_scraper.py`: Contains the scraper class and logic.
- `af_forms_query.py`: Provides methods to query the SQLite database.
- `example_usage.py`: Example script showing how to use the scraper and query classes.
- `go.py`: Main script to run the scraper.

## Troubleshooting

- Ensure ChromeDriver is compatible with your installed version of Google Chrome.
- If you encounter issues with Selenium, check the documentation for troubleshooting tips.

## License

This project is licensed under the MIT License.