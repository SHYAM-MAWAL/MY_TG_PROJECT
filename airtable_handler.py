import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable credentials
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE = os.getenv('AIRTABLE_TABLE')


class AirtableHandler:
    def __init__(self):
        """Initialize Airtable API connection"""
        if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE]):
            raise ValueError("Missing Airtable credentials in .env file")
        
        try:
            from pyairtable import Api
            self.api = Api(AIRTABLE_TOKEN)
        except ImportError:
            raise ImportError("pyairtable is not installed. Install it with: pip install pyairtable")
        
        # Parse base and table from AIRTABLE_BASE_ID if it contains table
        if '/' in AIRTABLE_BASE_ID:
            base_id, table_id = AIRTABLE_BASE_ID.split('/')
            self.base_id = base_id
            self.table_name = AIRTABLE_TABLE
        else:
            self.base_id = AIRTABLE_BASE_ID
            self.table_name = AIRTABLE_TABLE
        
        self.table = self.api.table(self.base_id, self.table_name)
    
    def check_if_exists(self, target_url):
        """Check if a course with the given URL already exists in Airtable"""
        try:
            # Escape single quotes in URL for formula
            escaped_url = target_url.replace("'", "\\'")
            # Search for records with matching target URL
            records = self.table.all(formula=f"{{target_url}}='{escaped_url}'")
            return len(records) > 0
        except Exception as e:
            print(f"  ⚠ Error checking Airtable: {str(e)}")
            # Return False on error to allow processing (fail-safe)
            return False
    
    def insert_course(self, title, target_url, image_base64=None):
        """Insert a new course into Airtable (with compressed image)"""
        try:
            from datetime import datetime
            
            # Prepare the record data
            fields = {
                'course_title': str(title)[:100000] if title else "No title",
                'target_url': str(target_url)[:1000] if target_url else "",
                'created_at': datetime.now().isoformat(),
                # Default status for new records
                'Status': 'Pending'
            }
            
            # Add image as base64 if provided — Airtable text field limit is ~100K chars
            if image_base64:
                if not image_base64.startswith('data:image'):
                    image_base64 = f"data:image/jpeg;base64,{image_base64}"
                if len(image_base64) <= 100000:
                    fields['image'] = image_base64
                    print(f"  ✓ Image added to Airtable ({len(image_base64)} chars)")
                else:
                    print(f"  ⚠ Image too large for Airtable ({len(image_base64)} chars), skipping image")
            
            # Create the record
            record = self.table.create(fields)
            
            print(f"  ✓ Inserted into Airtable (Record ID: {record['id']})")
            return True
            
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if 'INVALID_VALUE_FOR_COLUMN' in error_msg:
                print(f"  ✗ Airtable insert error: Field validation failed (check field types)")
            elif '422' in error_msg:
                print(f"  ✗ Airtable insert error: Invalid data format")
            else:
                print(f"  ✗ Airtable insert error: {error_msg}")
            return False
    
    def get_all_courses(self):
        """Get all courses from Airtable"""
        try:
            records = self.table.all()
            courses = []
            for record in records:
                courses.append({
                    'id': record['id'],
                    'fields': record['fields']
                })
            return courses
        except Exception as e:
            print(f"  ✗ Error fetching from Airtable: {str(e)}")
            return []
    
    def delete_course(self, record_id):
        """Delete a course from Airtable by record ID"""
        try:
            self.table.delete(record_id)
            print(f"  ✓ Deleted from Airtable (Record ID: {record_id})")
            return True
        except Exception as e:
            print(f"  ✗ Error deleting from Airtable: {str(e)}")
            return False


# Test function
if __name__ == "__main__":
    print("Testing Airtable Connection...\n")
    
    try:
        handler = AirtableHandler()
        print(f"✓ Connected to Airtable")
        print(f"  Base ID: {handler.base_id}")
        print(f"  Table: {handler.table_name}\n")
        
        # Test: Get all records
        print("Fetching all records...")
        courses = handler.get_all_courses()
        print(f"✓ Found {len(courses)} records\n")
        
        if courses:
            print("Sample record:")
            print(f"  ID: {courses[0]['id']}")
            print(f"  Fields: {courses[0]['fields']}")
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
