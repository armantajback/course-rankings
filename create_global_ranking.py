import json
import os
from datetime import datetime

def load_course_data_from_js(file_path):
    """Load course data from JavaScript file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract the JSON array from the JavaScript file
    start = content.find('[')
    end = content.rfind(']') + 1
    json_str = content[start:end]
    
    return json.loads(json_str)

def calculate_course_score(course):
    """Calculate a composite score for ranking courses"""
    # Weight different metrics
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

def get_course_bucket(course_title):
    """Determine which bucket a course belongs to"""
    # Define FLMBE categories with their course titles
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
            'Digital Marketing',
            'Data Science for Marketing Decision Making',
            'Consumer Behavior',
            'Digital Marketing Lab',
            'Lab in Developing New Products and Services',
            'Pricing Strategies',
            'Brand Management in a Digital Age'
        ]
    }
    
    # Check which bucket the course belongs to
    for bucket, titles in flmbe_categories.items():
        if course_title in titles:
            return bucket
    
    return 'Other'

def generate_global_ranking_html(courses, output_file):
    """Generate HTML with both bucket-specific and global rankings"""
    
    # Calculate scores and add bucket information
    for course in courses:
        course['composite_score'] = calculate_course_score(course)
        course['bucket'] = get_course_bucket(course['title'])
    
    # Sort by composite score for global ranking
    global_ranked = sorted(courses, key=lambda x: x['composite_score'], reverse=True)
    
    # Get top 10 global
    top_10_global = global_ranked[:10]
    
    # Get top 15 from each bucket
    bucket_rankings = {}
    for bucket in ['Society', 'Economy', 'Strategy', 'People', 'Decisions', 'Operations', 'Finance', 'Marketing']:
        bucket_courses = [c for c in courses if c['bucket'] == bucket]
        bucket_ranked = sorted(bucket_courses, key=lambda x: x['composite_score'], reverse=True)
        bucket_rankings[bucket] = bucket_ranked[:15]
    
    # Get top course for each unique course name
    course_name_rankings = {}
    for course in courses:
        course_name = course['title']
        if course_name not in course_name_rankings:
            course_name_rankings[course_name] = course
        elif course['composite_score'] > course_name_rankings[course_name]['composite_score']:
            course_name_rankings[course_name] = course
    
    # Sort by composite score and get top 10
    top_course_names = sorted(course_name_rankings.values(), key=lambda x: x['composite_score'], reverse=True)[:10]
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLMBE Course Rankings - Global & Bucket Views</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .main-content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
        }}

        .section-title {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.6rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }}

        .course-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 12px;
        }}

        .course-card {{
            background: white;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border-left: 3px solid #667eea;
            min-height: 200px;
        }}

        .course-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }}

        .course-rank {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }}

        .course-bucket {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 8px;
        }}

        .course-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 6px;
        }}

        .course-id {{
            color: #667eea;
            font-weight: 500;
            margin-bottom: 4px;
            font-size: 0.9rem;
        }}

        .course-instructor {{
            color: #6c757d;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }}

        .course-term {{
            color: #6c757d;
            font-size: 0.8rem;
            margin-bottom: 10px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            margin-bottom: 10px;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.8rem;
        }}

        .metric-label {{
            font-size: 0.8rem;
            color: #6c757d;
        }}

        .metric-value {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.8rem;
        }}

        .composite-score {{
            background: linear-gradient(135deg, #dc3545, #fd7e14);
            color: white;
            padding: 6px 10px;
            border-radius: 4px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}

        @media (max-width: 768px) {{
            .course-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FLMBE Course Rankings</h1>
            <p>Global & Bucket-Specific Top 10 Rankings</p>
        </div>
        
        <div class="main-content">
            <!-- FLMBE Options Section -->
            <div class="section">
                <h2 class="section-title">📋 FLMBE Course Options</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
"""

    # Add FLMBE options
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
            'Digital Marketing',
            'Data Science for Marketing Decision Making',
            'Consumer Behavior',
            'Digital Marketing Lab',
            'Lab in Developing New Products and Services',
            'Pricing Strategies',
            'Brand Management in a Digital Age'
        ]
    }

    for bucket, titles in flmbe_categories.items():
        html_content += f"""
                    <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h3 style="color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 8px;">{bucket}</h3>
                        <ul style="list-style: none; padding: 0;">
"""
        for title in titles:
            html_content += f"""
                            <li style="padding: 8px 0; border-bottom: 1px solid #f1f3f4; color: #6c757d;">• {title}</li>
"""
        html_content += """
                        </ul>
                    </div>
"""

    html_content += """
                </div>
            </div>

            <!-- Top Course Names Section -->
            <div class="section">
                <h2 class="section-title">🏆 Top 10 Course Names (Best Instance)</h2>
                <div class="course-grid">
"""

    # Add top course names
    for i, course in enumerate(top_course_names, 1):
        html_content += f"""
                    <div class="course-card">
                        <div>
                            <span class="course-rank">{i}</span>
                            <span class="course-bucket">{course['bucket']}</span>
                        </div>
                        <div class="course-title">{course['title']}</div>
                        <div class="course-id">{course['id']}</div>
                        <div class="course-instructor">{course['instructor']}</div>
                        <div class="course-term">{course['term']}</div>
                        
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Overall</span>
                                <span class="metric-value">{course['overall']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Recommend</span>
                                <span class="metric-value">{course['recommendation']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Clarity</span>
                                <span class="metric-value">{course['clarity']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Interest</span>
                                <span class="metric-value">{course['interest']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Usefulness</span>
                                <span class="metric-value">{course['usefulness']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Hours/Week</span>
                                <span class="metric-value">{course['hoursPerWeek']}</span>
                            </div>
                        </div>
                        
                        <div class="composite-score">
                            Best Instance Score: {course['composite_score']:.2f}
                        </div>
                    </div>
"""

    html_content += """
                </div>
            </div>

            <!-- Global Top 10 Section -->
            <div class="section">
                <h2 class="section-title">🌍 Global Top 10 Courses (All Instances)</h2>
                <div class="course-grid">
"""

    # Add global top 10
    for i, course in enumerate(top_10_global, 1):
        html_content += f"""
                    <div class="course-card">
                        <div>
                            <span class="course-rank">{i}</span>
                            <span class="course-bucket">{course['bucket']}</span>
                        </div>
                        <div class="course-title">{course['title']}</div>
                        <div class="course-id">{course['id']}</div>
                        <div class="course-instructor">{course['instructor']}</div>
                        <div class="course-term">{course['term']}</div>
                        
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Overall</span>
                                <span class="metric-value">{course['overall']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Recommend</span>
                                <span class="metric-value">{course['recommendation']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Clarity</span>
                                <span class="metric-value">{course['clarity']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Interest</span>
                                <span class="metric-value">{course['interest']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Usefulness</span>
                                <span class="metric-value">{course['usefulness']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Hours/Week</span>
                                <span class="metric-value">{course['hoursPerWeek']}</span>
                            </div>
                        </div>
                        
                        <div class="composite-score">
                            Global Score: {course['composite_score']:.2f}
                        </div>
                    </div>
"""

    html_content += """
                </div>
            </div>
"""

    # Add bucket-specific sections
    for bucket in ['Society', 'Economy', 'Strategy', 'People', 'Decisions', 'Operations', 'Finance', 'Marketing']:
        if bucket_rankings[bucket]:  # Only show buckets with courses
            html_content += f"""
            <div class="section">
                <h2 class="section-title">📚 {bucket} Top 15</h2>
                <div class="course-grid">
"""
            
            for i, course in enumerate(bucket_rankings[bucket], 1):
                html_content += f"""
                    <div class="course-card">
                        <div>
                            <span class="course-rank">{i}</span>
                            <span class="course-bucket">{bucket}</span>
                        </div>
                        <div class="course-title">{course['title']}</div>
                        <div class="course-id">{course['id']}</div>
                        <div class="course-instructor">{course['instructor']}</div>
                        <div class="course-term">{course['term']}</div>
                        
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Overall</span>
                                <span class="metric-value">{course['overall']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Recommend</span>
                                <span class="metric-value">{course['recommendation']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Clarity</span>
                                <span class="metric-value">{course['clarity']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Interest</span>
                                <span class="metric-value">{course['interest']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Usefulness</span>
                                <span class="metric-value">{course['usefulness']}/5</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Hours/Week</span>
                                <span class="metric-value">{course['hoursPerWeek']}</span>
                            </div>
                        </div>
                        
                        <div class="composite-score">
                            {bucket} Score: {course['composite_score']:.2f}
                        </div>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""

    # Add footer
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Based on student evaluations from Autumn 2023, Autumn 2024, Spring 2024, and Spring 2025</p>
        </div>
    </div>
</body>
</html>
"""

    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    input_file = 'cleaned_course_data.js'
    output_file = 'global_flmbe_rankings.html'
    
    try:
        print(f"Loading course data from {input_file}...")
        courses = load_course_data_from_js(input_file)
        print(f"Found {len(courses)} courses")
        
        print("Generating global and bucket-specific rankings...")
        generate_global_ranking_html(courses, output_file)
        
        print(f"✅ HTML report generated: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        print("Make sure cleaned_course_data.js exists in the current directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 