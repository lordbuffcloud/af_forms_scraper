# Run the scraper
scraper = AFFormsScraper()
scraper.run()

# Query the database
query = AFFormsQuery()

# Search for a form
results = query.search_forms("evaluation")
for result in results:
    print(f"Form {result['form_number']}: {result['title']}")
    print(f"URL: {result['pdf_url']}\n")

# Get specific form
form = query.get_form_by_number("AF910")
if form:
    print(f"Found form: {form['title']}")
    print(f"URL: {form['pdf_url']}")
