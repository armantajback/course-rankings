import json
import csv
import os
import re
from datetime import datetime

def csv_to_js(csv_file, js_file):
    """Convert CSV to JavaScript file"""
    courses = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            if len(row) >= 14 and row[0].strip():
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
    
    with open(js_file, 'w') as file:
        file.write('const courseData = ')
        file.write(json.dumps(courses, indent=2))
        file.write(';')
    
    print(f"Converted {len(courses)} courses to {js_file}")
    return courses

def filter_recent_courses(courses):
    """Filter courses to only include the most recent 2 years"""
    # Extract years from course data
    term_years = set()
    for course in courses:
        term = course.get('term', '')
        if term:
            year_match = re.search(r'(\d{4})', term)
            if year_match:
                term_years.add(int(year_match.group(1)))
    
    # Get the 2 most recent years
    recent_years = sorted(term_years, reverse=True)[:2]
    print(f"Most recent years found: {recent_years}")
    
    # Filter courses to only include recent years
    recent_courses = []
    for course in courses:
        term = course.get('term', '')
        year_match = re.search(r'(\d{4})', term)
        if year_match and int(year_match.group(1)) in recent_years:
            recent_courses.append(course)
    
    return recent_courses

def get_course_bucket(course_title):
    """Determine which bucket a course belongs to"""
    flmbe_categories = {
        'Society': [
            'Social Entrepreneurship and Innovation',
            'Culture (And Why It Matters)',
            'The Legal Infrastructure of Business',
            'Business with Purpose',
            'Business, Politics, and Ethics',
            'Designing a Good Life',
            'Perspectives on Capitalism',
            'The Firm and the Non-Market Environment',
            'Impact Investing'
        ],
        'Economy': [
            'Macroeconomics and the Business Environment',
            'Money and Banking',
            'Business in Historical Perspective',
            'International Commercial Policy',
            'International Financial Policy',
            'The Wealth of Nations'
        ],
        'Strategy': [
            'Platforms and Market Design',
            'Competitive Strategy',
            'Technology Strategy',
            'Strategy Simulation: Creating Value in Complex and Ambiguous Settings',
            'Strategy and Structure: Markets and Organizations',
            'Game Theory'
        ],
        'People': [
            'Leadership Studio',
            'Managing in Organizations',
            'Managing the Workplace',
            'Power and Influence in Organizations',
            'Diversity in Organizations'
        ],
        'Decisions': [
            'Managerial Decision Modeling',
            'The Study of Behavioral Economics',
            'Internal Information for Strategic Decisions',
            'Advanced Decision Models with Python',
            'Managerial Decision Making'
        ],
        'Operations': [
            'Supply Chain Strategy and Practice',
            'Managing Service Operations',
            'Operations Management: Business Process Fundamentals',
            'Revenue Management'
        ],
        'Finance': [
            'Entrepreneurial Finance and Private Equity',
            'Asset Pricing I',
            'Investments',
            'Corporate Finance I',
            'Corporation Finance',
            'Cases in Financial Management',
            'Corporate Finance II',
            'Asset Pricing II',
            'Portfolio Management',
            'Advanced Investments',
            'Fixed Income Asset Pricing',
            'Debt, Distress, and Restructuring',
            'International Corporate Finance'
        ],
        'Marketing': [
            'Marketing Strategy',
            'Marketing Strategy (with Sustainability Simulation)',
            'Digital Marketing',
            'Data Science for Marketing Decision Making',
            'Consumer Behavior',
            'Digital Marketing Lab',
            'Lab in Developing New Products and Services',
            'New Products and Services',
            'Pricing Strategies',
            'Brand Management in a Digital Age',
            'Data-Driven Marketing',
            'Experimental Marketing'
        ]
    }
    
    for bucket, titles in flmbe_categories.items():
        if course_title in titles:
            return bucket
    
    return 'Other'

def bucket_courses(courses, output_dir):
    """Bucket courses by FLMBE categories"""
    buckets = {}
    categories = ['Society', 'Economy', 'Strategy', 'People', 'Decisions', 'Operations', 'Finance', 'Marketing']
    
    # Initialize buckets
    for category in categories:
        buckets[category] = []
    buckets['Other'] = []
    
    # Process each course
    for course in courses:
        bucket = get_course_bucket(course['title'])
        buckets[bucket].append(course)
    
    # Write bucket files
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for category, courses_list in buckets.items():
        if courses_list:
            filename = f"{category.lower().replace(' ', '_')}_courses.js"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write('const courseData = ')
                file.write(json.dumps(courses_list, indent=2))
                file.write(';')
            
            print(f"  {filename}: {len(courses_list)} courses")
    
    return buckets

def calculate_course_score(course):
    """Calculate a composite score for ranking courses"""
    weights = {
        'overall': 0.3,
        'recommendation': 0.25,
        'clarity': 0.2,
        'interest': 0.15,
        'usefulness': 0.1
    }
    
    score = 0
    for metric, weight in weights.items():
        value = course.get(metric, 0)
        if isinstance(value, (int, float)) and value > 0:
            score += value * weight
    
    return score

def generate_html_rankings(buckets, output_file, title, subtitle):
    """Generate HTML rankings from bucketed data"""
    
    # Calculate scores for all courses
    all_courses = []
    for category, courses in buckets.items():
        if category != 'Other':
            for course in courses:
                course['composite_score'] = calculate_course_score(course)
                course['bucket'] = category
                all_courses.append(course)
    
    # Get top 15 from each bucket
    bucket_rankings = {}
    for bucket in ['Society', 'Economy', 'Strategy', 'People', 'Decisions', 'Operations', 'Finance', 'Marketing']:
        bucket_courses = [c for c in all_courses if c['bucket'] == bucket]
        bucket_ranked = sorted(bucket_courses, key=lambda x: x['composite_score'], reverse=True)
        bucket_rankings[bucket] = bucket_ranked[:15]
    
    # Get all FLMBE course titles for the overview
    flmbe_course_titles = {
        'Society': [
            'Social Entrepreneurship and Innovation',
            'Culture (And Why It Matters)',
            'The Legal Infrastructure of Business',
            'Business with Purpose',
            'Business, Politics, and Ethics',
            'Designing a Good Life',
            'Perspectives on Capitalism',
            'The Firm and the Non-Market Environment',
            'Impact Investing'
        ],
        'Economy': [
            'Macroeconomics and the Business Environment',
            'Money and Banking',
            'Business in Historical Perspective',
            'International Commercial Policy',
            'International Financial Policy',
            'The Wealth of Nations',
            'Managing the Firm in the Global Economy'
        ],
        'Strategy': [
            'Platforms and Market Design',
            'Competitive Strategy',
            'Technology Strategy',
            'Strategy Simulation: Creating Value in Complex and Ambiguous Settings',
            'Strategy and Structure: Markets and Organizations',
            'Game Theory'
        ],
        'People': [
            'Leadership Studio',
            'Managing in Organizations',
            'Managing the Workplace',
            'Power and Influence in Organizations',
            'Diversity in Organizations'
        ],
        'Decisions': [
            'Managerial Decision Modeling',
            'The Study of Behavioral Economics',
            'Internal Information for Strategic Decisions',
            'Advanced Decision Models with Python',
            'Managerial Decision Making'
        ],
        'Operations': [
            'Supply Chain Strategy and Practice',
            'Managing Service Operations',
            'Operations Management: Business Process Fundamentals',
            'Revenue Management'
        ],
        'Finance': [
            'Entrepreneurial Finance and Private Equity',
            'Asset Pricing I',
            'Investments',
            'Corporate Finance I',
            'Corporation Finance',
            'Cases in Financial Management',
            'Corporate Finance II',
            'Asset Pricing II',
            'Portfolio Management',
            'Advanced Investments',
            'Fixed Income Asset Pricing',
            'Debt, Distress, and Restructuring',
            'International Corporate Finance'
        ],
        'Marketing': [
            'Marketing Strategy',
            'Marketing Strategy (with Sustainability Simulation)',
            'Digital Marketing',
            'Data Science for Marketing Decision Making',
            'Consumer Behavior',
            'Digital Marketing Lab',
            'Lab in Developing New Products and Services',
            'New Products and Services',
            'Pricing Strategies',
            'Brand Management in a Digital Age',
            'Data-Driven Marketing',
            'Experimental Marketing'
        ]
    }
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #87CEEB 0%, #98FB98 50%, #F0E68C 100%);
            color: #2F4F4F;
            line-height: 1.6;
            font-size: 14px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.3);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            color: #FFF;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.1rem;
            color: #FFF;
            opacity: 0.9;
        }}

        .section {{
            margin-bottom: 40px;
            background: rgba(255, 255, 255, 0.9);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.2);
        }}

        .section-title {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            border-bottom: 3px solid #FF6B35;
            padding-bottom: 10px;
            color: #8B4513;
        }}

        .flmbe-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .bucket-overview {{
            background: linear-gradient(135deg, #FFE4B5 0%, #F5DEB3 100%);
            border: 2px solid #D2691E;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(210, 105, 30, 0.2);
        }}

        .bucket-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-transform: uppercase;
            color: #8B4513;
            text-align: center;
            padding: 8px;
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            border-radius: 8px;
        }}

        .course-list {{
            list-style: none;
        }}

        .course-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #D2691E;
            color: #2F4F4F;
            font-weight: 500;
        }}

        .course-list li:last-child {{
            border-bottom: none;
        }}

        .table-wrapper {{
            overflow-x: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .rankings-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            min-width: 800px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .rankings-table th {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: bold;
            text-transform: uppercase;
            border: 1px solid #D2691E;
        }}

        .rankings-table td {{
            padding: 12px 10px;
            border: 1px solid #D2691E;
            vertical-align: top;
            color: #2F4F4F;
        }}

        .rankings-table tr:nth-child(even) {{
            background: #FFF8DC;
        }}

        .rankings-table tr:hover {{
            background: #FFE4B5;
        }}

        .rank {{
            font-weight: bold;
            color: #FF6B35;
            text-align: center;
            font-size: 1.1rem;
        }}

        .course-title {{
            font-weight: bold;
            color: #8B4513;
        }}

        .course-id {{
            color: #D2691E;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .course-instructor {{
            color: #2F4F4F;
            font-size: 0.9rem;
        }}

        .course-term {{
            color: #D2691E;
            font-size: 0.8rem;
            font-weight: 500;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            font-size: 0.8rem;
        }}

        .metric {{
            text-align: center;
            padding: 2px;
            background: #111;
            border: 1px solid #333;
        }}

        .metric-label {{
            color: #888;
            font-size: 0.7rem;
        }}

        .metric-value {{
            color: #00ff00;
            font-weight: bold;
        }}

        .composite-score {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            font-size: 0.9rem;
            border-radius: 5px;
        }}

        .love-header {{
            background: linear-gradient(135deg, #D4AF37 0%, #FFD700 50%, #B8860B 100%);
            border: 4px solid #8B4513;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 12px 24px rgba(139, 69, 19, 0.4);
            position: relative;
            overflow: hidden;
        }}

        .love-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="40" fill="rgba(255,255,255,0.4)">❤</text></svg>') repeat;
            opacity: 0.6;
        }}

        .love-text {{
            font-family: 'Brush Script MT', 'Lucida Handwriting', cursive;
            font-size: 2.2rem;
            font-weight: bold;
            color: #8B4513;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
            margin: 0;
            position: relative;
            z-index: 1;
            letter-spacing: 2px;
        }}

        .love-subtitle {{
            font-family: 'Georgia', serif;
            font-size: 1.1rem;
            color: #8B4513;
            margin-top: 10px;
            font-style: italic;
            position: relative;
            z-index: 1;
        }}

        .footer {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-top: 30px;
            color: white;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.3);
        }}

        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                padding: 15px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .main-content {{
                padding: 15px;
            }}
            
            .flmbe-overview {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .bucket-overview {{
                padding: 15px;
            }}
            
            .rankings-table {{
                font-size: 10px;
                overflow-x: auto;
                display: block;
            }}
            
            .rankings-table th,
            .rankings-table td {{
                padding: 8px 6px;
                min-width: 60px;
            }}
            
            .rankings-table th:nth-child(2),
            .rankings-table td:nth-child(2) {{
                min-width: 120px;
            }}
            
            .metrics {{
                grid-template-columns: repeat(2, 1fr);
                gap: 3px;
            }}

            .love-text {{
                font-size: 1.5rem;
            }}
            
            .love-header {{
                padding: 20px;
                margin-bottom: 20px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .container {{
                margin: 5px;
                padding: 10px;
            }}
            
            .header {{
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
            
            .main-content {{
                padding: 10px;
            }}
            
            .flmbe-overview {{
                gap: 10px;
            }}
            
            .bucket-overview {{
                padding: 10px;
            }}
            
            .rankings-table {{
                font-size: 9px;
            }}
            
            .rankings-table th,
            .rankings-table td {{
                padding: 6px 4px;
                min-width: 50px;
            }}
            
            .rankings-table th:nth-child(2),
            .rankings-table td:nth-child(2) {{
                min-width: 100px;
            }}
            
            .love-text {{
                font-size: 1.3rem;
            }}
            
            .love-header {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        
        <!-- Love Declaration Header -->
        <div class="love-header">
            <p class="love-text">By using this you acknowledge you LOVE Arman Tajback</p>
            <p class="love-subtitle">With deepest affection and eternal devotion</p>
        </div>
        
        <!-- FLMBE Course Overview Section -->
        <div class="section">
            <h2 class="section-title">📚 FLMBE Course Categories & Available Courses</h2>
            <div class="flmbe-overview">
"""

    # Add FLMBE course overview in specified order
    bucket_order = ['Finance', 'Marketing', 'Operations', 'Decisions', 'People', 'Strategy', 'Economy', 'Society']
    for bucket in bucket_order:
        titles = flmbe_course_titles[bucket]
        html_content += f"""
                <div class="bucket-overview">
                    <div class="bucket-title">{bucket}</div>
                    <ul class="course-list">
"""
        for title in titles:
            html_content += f"""
                        <li>{title}</li>
"""
        html_content += """
                    </ul>
                </div>
"""

    html_content += """
            </div>
        </div>
"""

    # Add bucket-specific rankings
    for bucket in ['Finance', 'Marketing', 'Operations', 'Decisions', 'People', 'Strategy', 'Economy', 'Society']:
        if bucket_rankings[bucket]:  # Only show buckets with courses
            html_content += f"""
        <div class="section">
            <h2 class="section-title">🏆 {bucket} Top 15 Rankings</h2>
            <div class="table-wrapper">
                <table class="rankings-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Course Title</th>
                        <th>Course ID</th>
                        <th>Instructor</th>
                        <th>Term</th>
                        <th>Overall</th>
                        <th>Recommend</th>
                        <th>Clarity</th>
                        <th>Interest</th>
                        <th>Useful</th>
                        <th>Hours</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for i, course in enumerate(bucket_rankings[bucket], 1):
                html_content += f"""
                    <tr>
                        <td class="rank">{i}</td>
                        <td>
                            <div class="course-title">{course['title']}</div>
                        </td>
                        <td class="course-id">{course['id']}</td>
                        <td class="course-instructor">{course['instructor']}</td>
                        <td class="course-term">{course['term']}</td>
                        <td class="metric-value">{course['overall']}/5</td>
                        <td class="metric-value">{course['recommendation']}/5</td>
                        <td class="metric-value">{course['clarity']}/5</td>
                        <td class="metric-value">{course['interest']}/5</td>
                        <td class="metric-value">{course['usefulness']}/5</td>
                        <td class="metric-value">{course['hoursPerWeek']}</td>
                        <td class="composite-score">{course['composite_score']:.2f}</td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
            </div>
        </div>
"""

    # Add footer
    html_content += f"""
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>{subtitle}</p>
        </div>
    </div>
</body>
</html>
"""

    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

def generate_index_page():
    """Generate the main index page with navigation to both data sets"""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLMBE Course Rankings - Home</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #87CEEB 0%, #98FB98 50%, #F0E68C 100%);
            color: #2F4F4F;
            line-height: 1.6;
            font-size: 14px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.3);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            color: #FFF;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.1rem;
            color: #FFF;
            opacity: 0.9;
        }}

        .love-header {{
            background: linear-gradient(135deg, #D4AF37 0%, #FFD700 50%, #B8860B 100%);
            border: 4px solid #8B4513;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 12px 24px rgba(139, 69, 19, 0.4);
            position: relative;
            overflow: hidden;
        }}

        .love-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="40" fill="rgba(255,255,255,0.4)">❤</text></svg>') repeat;
            opacity: 0.6;
        }}

        .love-text {{
            font-family: 'Brush Script MT', 'Lucida Handwriting', cursive;
            font-size: 2.2rem;
            font-weight: bold;
            color: #8B4513;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
            margin: 0;
            position: relative;
            z-index: 1;
            letter-spacing: 2px;
        }}

        .love-subtitle {{
            font-family: 'Georgia', serif;
            font-size: 1.1rem;
            color: #8B4513;
            margin-top: 10px;
            font-style: italic;
            position: relative;
            z-index: 1;
        }}

        .navigation-section {{
            background: rgba(255, 255, 255, 0.9);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.2);
        }}

        .navigation-title {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 30px;
            text-transform: uppercase;
            border-bottom: 3px solid #FF6B35;
            padding-bottom: 10px;
            color: #8B4513;
            text-align: center;
        }}

        .nav-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}

        .nav-card {{
            background: linear-gradient(135deg, #FFE4B5 0%, #F5DEB3 100%);
            border: 2px solid #D2691E;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(210, 105, 30, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}

        .nav-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(210, 105, 30, 0.3);
        }}

        .nav-card h3 {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #8B4513;
            text-transform: uppercase;
        }}

        .nav-card p {{
            color: #2F4F4F;
            margin-bottom: 20px;
            font-size: 1rem;
        }}

        .nav-button {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: transform 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }}

        .nav-button:hover {{
            transform: translateY(-2px);
        }}

        .footer {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-top: 30px;
            color: white;
            box-shadow: 0 8px 16px rgba(139, 69, 19, 0.3);
        }}

        @media (max-width: 768px) {{
            .nav-cards {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .love-text {{
                font-size: 1.8rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FLMBE Course Rankings</h1>
            <p>Booth School of Business Course Evaluation Rankings</p>
        </div>
        
        <!-- Love Declaration Header -->
        <div class="love-header">
            <p class="love-text">By using this you acknowledge you LOVE Arman Tajback</p>
            <p class="love-subtitle">With deepest affection and eternal devotion</p>
        </div>
        
        <!-- Navigation Section -->
        <div class="navigation-section">
            <h2 class="navigation-title">📚 Choose Your Data Set</h2>
            <div class="nav-cards">
                <div class="nav-card">
                    <h3>Recent Course Data</h3>
                    <p>View rankings based on student evaluations from the most recent 2 years (2024-2025). This provides the most current insights into course performance and student satisfaction.</p>
                    <a href="recent.html" class="nav-button">View Recent Rankings</a>
                </div>
                
                <div class="nav-card">
                    <h3>All Course Data</h3>
                    <p>View comprehensive rankings based on ALL student evaluations from the complete dataset. This gives you the full historical perspective on course performance.</p>
                    <a href="all.html" class="nav-button">View All Rankings</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Booth School of Business Course Rankings</p>
        </div>
    </div>
</body>
</html>"""

    # Write the index HTML file
    with open('docs/index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    print("🚀 Starting complete FLMBE workflow...")
    
    # Step 1: Convert CSV to course_data.js
    print("\n📊 Step 1: Converting CSV to course_data.js...")
    all_courses = csv_to_js('booth_course_evals.csv', 'course_data.js')
    
    # Step 2: Create cleaned_course_data.js (recent data)
    print("\n📊 Step 2: Creating cleaned_course_data.js (recent data)...")
    recent_courses = filter_recent_courses(all_courses)
    
    with open('cleaned_course_data.js', 'w') as file:
        file.write('const courseData = ')
        file.write(json.dumps(recent_courses, indent=2))
        file.write(';')
    
    print(f"Created cleaned_course_data.js with {len(recent_courses)} recent courses")
    
    # Step 3: Bucket all data
    print("\n📊 Step 3: Bucketing all data...")
    all_buckets = bucket_courses(all_courses, 'buckets_all')
    
    # Step 4: Bucket recent data
    print("\n📊 Step 4: Bucketing recent data...")
    recent_buckets = bucket_courses(recent_courses, 'buckets_recent')
    
    # Step 5: Generate HTML for all data
    print("\n📊 Step 5: Generating HTML for all data...")
    generate_html_rankings(all_buckets, 'docs/all.html', 
                          'FLMBE Course Rankings - All Data', 
                          'Based on ALL student evaluations from the complete dataset')
    
    # Step 6: Generate HTML for recent data
    print("\n📊 Step 6: Generating HTML for recent data...")
    generate_html_rankings(recent_buckets, 'docs/recent.html', 
                          'FLMBE Course Rankings - Recent Data', 
                          'Based on student evaluations from the most recent 2 years')
    
    # Step 7: Generate index page with navigation
    print("\n📊 Step 7: Generating index page with navigation...")
    generate_index_page()
    
    print("\n✅ Complete workflow finished!")
    print("\n📁 Generated files:")
    print("  - course_data.js (all data)")
    print("  - cleaned_course_data.js (recent data)")
    print("  - buckets_all/ (all data buckets)")
    print("  - buckets_recent/ (recent data buckets)")
    print("  - docs/index.html (navigation page)")
    print("  - docs/all.html (all data rankings)")
    print("  - docs/recent.html (recent data rankings)")

if __name__ == "__main__":
    main() 