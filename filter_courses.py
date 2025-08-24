import json
import re

def extract_course_data_from_js(file_path):
    """Extract course data from the JavaScript file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the courseData array in the JavaScript file
    match = re.search(r'const courseData = (\[.*?\]);', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    else:
        raise ValueError("Could not find courseData array in the JavaScript file")

def filter_courses_by_term(courses, target_terms):
    """Filter courses by specific terms"""
    filtered_courses = []
    
    for course in courses:
        term = course.get('term', '').strip()
        if term in target_terms:
            filtered_courses.append(course)
    
    return filtered_courses

def write_cleaned_course_data(courses, output_file):
    """Write filtered courses to a new JavaScript file"""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('const courseData = ')
        file.write(json.dumps(courses, indent=2))
        file.write(';')
    
    print(f"Filtered {len(courses)} courses written to {output_file}")

def main():
    # Target terms to filter for
    target_terms = [
        "Spring 2024",
        "Spring 2025", 
        "Autumn 2024",
        "Autumn 2023"
    ]
    
    input_file = 'course_data.js'
    output_file = 'cleaned_course_data.js'
    
    try:
        # Extract course data from the JavaScript file
        print(f"Reading course data from {input_file}...")
        all_courses = extract_course_data_from_js(input_file)
        print(f"Found {len(all_courses)} total courses")
        
        # Filter courses by term
        print(f"Filtering for terms: {', '.join(target_terms)}")
        filtered_courses = filter_courses_by_term(all_courses, target_terms)
        print(f"Found {len(filtered_courses)} courses matching the criteria")
        
        # Show breakdown by term
        term_counts = {}
        for course in filtered_courses:
            term = course.get('term', 'Unknown')
            term_counts[term] = term_counts.get(term, 0) + 1
        
        print("\nBreakdown by term:")
        for term, count in sorted(term_counts.items()):
            print(f"  {term}: {count} courses")
        
        # Write filtered data to output file
        write_cleaned_course_data(filtered_courses, output_file)
        
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        print("Make sure course_data.js exists in the current directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 