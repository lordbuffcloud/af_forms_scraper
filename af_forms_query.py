import sqlite3

class AFFormsQuery:
    def __init__(self, db_name="af_forms.db"):
        self.db_name = db_name

    def search_forms(self, query):
        """Search forms by keyword in title, description, or form number"""
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
        """Get specific form by its number"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('SELECT * FROM forms WHERE form_number = ?', (form_number,))
        result = c.fetchone()
        conn.close()
        
        return self._format_result(result) if result else None

    def _format_result(self, row):
        """Format database row into dictionary"""
        return {
            'form_number': row[1],
            'title': row[2],
            'description': row[3],
            'category': row[4],
            'pdf_url': row[5],
            'last_updated': row[6]
        }
