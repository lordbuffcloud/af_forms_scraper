# ⬡ CK42X · ck42x.com
# MODULE: read-only queries over the scraped af forms sqlite db
# gold on black. sting once.
"""reads the forms table written by af_forms_scraper.py; rows become plain dicts."""

import sqlite3

class AFFormsQuery:
    """read-only lookups over the forms table; returns dicts and never raises on no match."""
    def __init__(self, db_name="af_forms.db"):
        """db path defaults to af_forms.db, the file the scraper writes."""
        self.db_name = db_name

    def search_forms(self, query):
        """substring match on title, description, or form_number; returns a list of dicts, never None.

        TRAP: the query is interpolated into LIKE unescaped, so % and _ act as wildcards.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM forms 
                    WHERE title LIKE ? 
                    OR description LIKE ? 
                    OR form_number LIKE ?''',
                 (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = c.fetchall()
        conn.close()
        
        return [self._format_result(r) for r in results]

    def get_form_by_number(self, form_number):
        """exact form_number match; returns one dict or None."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('SELECT * FROM forms WHERE form_number = ?', (form_number,))
        result = c.fetchone()
        conn.close()
        
        return self._format_result(result) if result else None

    def _format_result(self, row):
        """map a forms row to a dict, dropping row[0] (the id).

        INVARIANT: positions 1..6 must match the forms column order in af_forms_scraper.py.
        """
        return {
            'form_number': row[1],
            'title': row[2],
            'description': row[3],
            'category': row[4],
            'pdf_url': row[5],
            'last_updated': row[6]
        }
