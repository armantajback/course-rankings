# Chicago Booth Course Planner

A beautiful, interactive web application for planning your Chicago Booth MBA courses using course evaluation data.

## Features

- **Desired Courses**: Add courses you really want to take with time slot preferences
- **Required Courses by Category**: Organize required courses by requirement type (Finance, Marketing, Core, etc.)
- **Course Search**: Search through all Booth courses with real-time filtering
- **Course Evaluations**: View instructor ratings, hours per week, and student recommendations
- **Statistics Dashboard**: Track total courses and weekly time commitment
- **Persistent Storage**: Your course selections are saved locally in your browser

## How to Use

1. **Open the Application**: Simply open `index.html` in your web browser
2. **Add Desired Courses**:
   - Search for courses you want to take
   - Select a time slot preference
   - Click "Add Course"
3. **Add Required Courses**:
   - Enter a requirement category (e.g., "Finance", "Marketing", "Core")
   - Search for required courses
   - Select time slot and add to the category
4. **Manage Your Plan**:
   - Remove courses you no longer want
   - View statistics about your course load
   - All changes are automatically saved

## Data Source

The application uses the `booth_course_evals.csv` file containing:
- Course evaluations from multiple terms
- Instructor ratings and student feedback
- Hours per week estimates
- Overall course ratings and recommendations

## Technical Details

- **Pure HTML/CSS/JavaScript**: No external dependencies required
- **Local Storage**: Your data persists between browser sessions
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Beautiful gradient design with smooth animations

## Getting Started

1. Make sure both `index.html` and `booth_course_evals.csv` are in the same folder
2. Open `index.html` in your web browser
3. Start planning your Booth MBA journey!

The application will automatically load the course data and restore any previously saved course selections. 