import csv
import json

# Read the CSV file
courses = []
with open('booth_course_evals.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    
    for row in reader:
        if len(row) >= 14 and row[0].strip():  # Check if row has enough columns and first column is not empty
            try:
                course = {
                    'id': row[0].strip(),
                    'title': row[1].strip(),
                    'instructor': f"{row[2].strip()} {row[3].strip()}",
                    'term': row[4].strip(),
                    'hoursPerWeek': float(row[8]) if row[8] and row[8] != '' else 0,
                    'clarity': float(row[9]) if row[9] and row[9] != '' else 0,
                    'interest': float(row[10]) if row[10] and row[10] != '' else 0,
                    'usefulness': float(row[11]) if row[11] and row[11] != '' else 0,
                    'overall': float(row[12]) if row[12] and row[12] != '' else 0,
                    'recommendation': float(row[13]) if row[13] and row[13] != '' else 0
                }
                courses.append(course)
            except (ValueError, IndexError) as e:
                print(f"Skipping row due to error: {e}")
                continue

# Write to JavaScript file
with open('course_data.js', 'w') as file:
    file.write('const courseData = ')
    file.write(json.dumps(courses, indent=2))
    file.write(';')

print(f"Converted {len(courses)} courses to JavaScript format") 