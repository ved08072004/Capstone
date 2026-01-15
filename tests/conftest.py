"""
pytest configuration and custom HTML report styling
"""

import pytest
from datetime import datetime


def pytest_html_report_title(report):
    """Customize the HTML report title"""
    report.title = "ESG Question Answering System - Test Report"


def pytest_configure(config):
    """Configure pytest with custom metadata"""
    config._metadata = {
        "Project": "ESG Question Answering System",
        "Test Environment": "Development",
        "Tester": "Automated Test Suite",
        "Test Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def pytest_html_results_table_header(cells):
    """Customize table headers"""
    cells.insert(2, '<th>Description</th>')


def pytest_html_results_table_row(report, cells):
    """Add description column to results table"""
    cells.insert(2, f'<td>{getattr(report, "description", "")}</td>')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add test description to report"""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__ or "")


def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary section"""
    prefix.extend([
        '<div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); '
        'padding: 20px; border-radius: 10px; margin: 20px 0; color: white;">'
        '<h2 style="color: white; margin: 0;">🌱 ESG Question Answering System</h2>'
        '<p style="margin: 10px 0 0 0;">Automated Test Suite Results</p>'
        '</div>'
    ])


# Custom CSS for the HTML report
def pytest_html_results_table_html(report, data):
    """Inject custom CSS into the HTML report"""
    if report.when == 'call':
        # This will be called for each test result
        pass


# Add custom CSS styling
css = """
<style>
/* Modern ESG-themed styling */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    color: #1f2937;
}

h1, h2, h3 {
    color: #065f46;
    font-weight: 600;
}

/* Main header styling */
#title {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
    margin-bottom: 30px;
}

/* Summary section */
.summary {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 20px 0;
}

/* Environment table */
#environment {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

#environment td {
    padding: 12px;
    border: 1px solid #e5e7eb;
}

#environment tr:nth-child(odd) {
    background-color: #f9fafb;
}

/* Results table */
#results-table {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-top: 20px;
}

#results-table th {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 15px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}

#results-table td {
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}

#results-table tr:hover {
    background-color: #f0fdf4;
    transition: background-color 0.3s ease;
}

/* Test result colors */
.passed {
    color: #059669;
    font-weight: 600;
}

.failed {
    color: #dc2626;
    font-weight: 600;
}

.skipped {
    color: #f59e0b;
    font-weight: 600;
}

.passed .col-result {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-left: 4px solid #10b981;
}

.failed .col-result {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border-left: 4px solid #dc2626;
}

.skipped .col-result {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 4px solid #f59e0b;
}

/* Filter section */
.controls {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

input[type="checkbox"] {
    margin-right: 8px;
    cursor: pointer;
}

/* Buttons */
button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Log wrapper */
.logwrapper {
    background: #1e293b;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
}

.log {
    background: #0f172a;
    color: #e2e8f0;
    font-family: 'Courier New', Courier, monospace;
    padding: 15px;
    border-radius: 6px;
}

/* Collapsible sections */
.collapsible {
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.collapsible:hover {
    background-color: #f0fdf4;
}

/* Summary stats */
.run-count {
    font-size: 18px;
    font-weight: 600;
    color: #059669;
    margin: 15px 0;
}

/* Success badge */
span.passed::before {
    content: "✅ ";
}

span.failed::before {
    content: "❌ ";
}

span.skipped::before {
    content: "⏭️ ";
}

/* Extras row */
.extras-row {
    background: #f9fafb;
}

/* Filter labels */
.filter span {
    margin-right: 15px;
    padding: 5px 10px;
    border-radius: 5px;
    font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
    #title {
        padding: 20px;
        font-size: 20px;
    }
    
    #results-table {
        font-size: 11px;
    }
    
    .summary {
        padding: 15px;
    }
}

/* Animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

#results-table tbody {
    animation: fadeIn 0.5s ease;
}
</style>
"""


def pytest_html_report_title(report):
    """Set custom report title and inject CSS"""
    report.title = "ESG Question Answering System - Test Report"
