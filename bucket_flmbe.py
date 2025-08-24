# import json
# import re
# import os

# def extract_course_data_from_js(file_path):
#     """Extract course data from the JavaScript file"""
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
    
#     # Find the courseData array in the JavaScript file
#     match = re.search(r'const courseData = (\[.*?\]);', content, re.DOTALL)
#     if match:
#         json_str = match.group(1)
#         return json.loads(json_str)
#     else:
#         raise ValueError("Could not find courseData array in the JavaScript file")

# def normalize_title(title):
#     """Normalize title for comparison (lowercase, no whitespace)"""
#     return re.sub(r'\s+', '', title.lower())

# def validate_and_bucket_courses(courses):
#     """Validate course titles and bucket them into FLMBE categories"""
    
#     # Define FLMBE categories with their course titles
#     flmbe_categories = {
#         'Society': [
#             'Social Entrepreneurship and Innovation',
#             'Culture (And Why It Matters)',
#             'The Legal Infrastructure of Business',
#             'Business with Purpose',
#             'Business, Politics, and Ethics',
#             'Designing a Good Life',
#             'Perspectives on Capitalism',
#             'The Firm and the Non-Market Environment',
#             'Impact Investing'
#         ],
#         'Economy': [
#             'Macroeconomics and the Business Environment',
#             'Money and Banking',
#             'Business in Historical Perspective',
#             'International Commercial Policy',
#             'International Financial Policy',
#             'The Wealth of Nations',
#             'Managing the Firm in the Global Economy'
#         ],
#         'Strategy': [
#             'Platforms and Market Design',
#             'Competitive Strategy',
#             'Technology Strategy',
#             'Strategy Simulation: Creating Value in Complex and Ambiguous Settings',
#             'Strategy and Structure: Markets and Organizations',
#             'Game Theory'
#         ],
#         'People': [
#             'Leadership Studio',
#             'Managing in Organizations',
#             'Managing the Workplace',
#             'Power and Influence in Organizations',
#             'Diversity in Organizations'
#         ],
#         'Decisions': [
#             'Managerial Decision Modeling',
#             'The Study of Behavioral Economics',
#             'Internal Information for Strategic Decisions',
#             'Advanced Decision Models with Python',
#             'Managerial Decision Making'
#         ],
#         'Operations': [
#             'Supply Chain Strategy and Practice',
#             'Managing Service Operations',
#             'Operations Management: Business Process Fundamentals',
#             'Revenue Management'
#         ],
#         'Finance': [
#             'Entrepreneurial Finance and Private Equity',
#             'Asset Pricing I',
#             'Investments',
#             'Corporate Finance I',
#             'Corporation Finance',
#             'Cases in Financial Management',
#             'Corporate Finance II',
#             'Asset Pricing II',
#             'Portfolio Management',
#             'Advanced Investments',
#             'Fixed Income Asset Pricing',
#             'Debt, Distress, and Restructuring',
#             'International Corporate Finance'
#         ],
#         'Marketing': [
#             'Marketing Strategy',
#             'Digital Marketing',
#             'Data Science for Marketing Decision Making',
#             'Consumer Behavior',
#             'Digital Marketing Lab',
#             'Lab in Developing New Products and Services',
#             'Pricing Strategies',
#             'Brand Management in a Digital Age'
#         ]
#     }
    
#     # Create normalized versions for matching
#     normalized_categories = {}
#     for category, titles in flmbe_categories.items():
#         normalized_categories[category] = [normalize_title(title) for title in titles]
    
#     # Initialize buckets
#     buckets = {category: [] for category in flmbe_categories.keys()}
#     buckets['Unmatched'] = []
    
#     # Track matches for validation
#     found_titles = set()
    
#     # Process each course
#     for course in courses:
#         course_title = course.get('title', '')
#         normalized_course_title = normalize_title(course_title)
        
#         matched = False
        
#         # Check each category
#         for category, normalized_titles in normalized_categories.items():
#             if normalized_course_title in normalized_titles:
#                 buckets[category].append(course)
#                 found_titles.add(normalized_course_title)
#                 matched = True
#                 break
        
#         if not matched:
#             buckets['Unmatched'].append(course)
    
#     # Validate that all expected titles were found
#     all_expected_titles = set()
#     for titles in normalized_categories.values():
#         all_expected_titles.update(titles)
    
#     missing_titles = all_expected_titles - found_titles
#     extra_titles = found_titles - all_expected_titles
    
#     return buckets, missing_titles, extra_titles

# def write_category_files(buckets, output_dir):
#     """Write each category to a separate file"""
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     for category, courses in buckets.items():
#         if courses:  # Only create files for non-empty categories
#             filename = f"{category.lower().replace(' ', '_')}_courses.js"
#             filepath = os.path.join(output_dir, filename)
            
#             with open(filepath, 'w', encoding='utf-8') as file:
#                 file.write('const courseData = ')
#                 file.write(json.dumps(courses, indent=2))
#                 file.write(';')
            
#             print(f"  {filename}: {len(courses)} courses")

# def main():
#     input_file = 'course_data.js'
#     output_dir = 'flmbe_buckets'
    
#     try:
#         # Extract course data
#         print(f"Reading course data from {input_file}...")
#         courses = extract_course_data_from_js(input_file)
#         print(f"Found {len(courses)} courses")
        
#         # Validate and bucket courses
#         print("Validating and bucketing courses...")
#         buckets, missing_titles, extra_titles = validate_and_bucket_courses(courses)
        
#         # Report results
#         print(f"\nBucketing Results:")
#         print(f"  Total courses processed: {len(courses)}")
        
#         for category, courses_list in buckets.items():
#             if courses_list:
#                 print(f"  {category}: {len(courses_list)} courses")
        
#         # Report validation results
#         if missing_titles:
#             print(f"\n⚠️  Missing expected titles ({len(missing_titles)}):")
#             for title in sorted(missing_titles):
#                 print(f"    - {title}")
        
#         if extra_titles:
#             print(f"\n⚠️  Found unexpected matches ({len(extra_titles)}):")
#             for title in sorted(extra_titles):
#                 print(f"    - {title}")
        
#         if not missing_titles and not extra_titles:
#             print("\n✅ All expected titles found and no unexpected matches!")
        
#         # Write category files
#         print(f"\nWriting category files to {output_dir}/...")
#         write_category_files(buckets, output_dir)
        
#         print(f"\nDone! Category files written to {output_dir}/ directory")
        
#     except FileNotFoundError:
#         print(f"Error: Could not find {input_file}")
#         print("Make sure cleaned_course_data.js exists in the current directory")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     main() 