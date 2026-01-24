
import os
import datetime
import markdown
from xhtml2pdf import pisa
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotebookLogger")

NOTEBOOK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Notebook'))

def ensure_notebook_dir():
    if not os.path.exists(NOTEBOOK_DIR):
        os.makedirs(NOTEBOOK_DIR)
        logger.info(f"Created Notebook directory at {NOTEBOOK_DIR}")

def convert_markdown_to_pdf(markdown_content, output_path):
    """
    Converts markdown text to a PDF file.
    """
    # 1. Start with a basic HTML template with CSS for styling
    html_template = """
    <html>
    <head>
    <style>
        body { font-family: Helvetica, sans-serif; font-size: 12px; line-height: 1.5; color: #333; }
        h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-top: 20px; }
        h2 { color: #34495e; margin-top: 15px; border-bottom: 1px solid #eee; }
        h3 { color: #7f8c8d; }
        code { background-color: #f8f8f8; padding: 2px 4px; border-radius: 3px; font-family: "Courier New", Courier, monospace; }
        pre { background-color: #f8f8f8; padding: 10px; border: 1px solid #ddd; border-radius: 5px; white-space: pre-wrap; }
        blockquote { border-left: 4px solid #ddd; padding-left: 10px; color: #777; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    {{content}}
    </body>
    </html>
    """

    # 2. Convert Markdown to HTML
    # Enable extensions for tables and fenced code blocks
    html_body = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
    
    # 3. Inject into template
    full_html = html_template.replace("{{content}}", html_body)

    # 4. Write to PDF
    with open(output_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(src=full_html, dest=pdf_file)

    if pisa_status.err:
        logger.error("PDF generation failed.")
        return False
    
    return True

def log_to_notebook(title, markdown_content):
    """
    Logs an entry to the notebook.
    title: Short string for filename (e.g. "Status_Update")
    markdown_content: The actual text content
    """
    ensure_notebook_dir()
    
    # Generate Filename: YYYY-MM-DD_HHMM_Title.pdf
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    safe_title = "".join([c if c.isalnum() else "_" for c in title])
    filename = f"{timestamp}_{safe_title}.pdf"
    output_path = os.path.join(NOTEBOOK_DIR, filename)
    
    logger.info(f"Generating PDF report: {output_path}")
    
    success = convert_markdown_to_pdf(markdown_content, output_path)
    
    if success:
        logger.info("Successfully created Notebook entry.")
        return output_path
    else:
        logger.error("Failed to create Notebook entry.")
        return None

if __name__ == "__main__":
    # Test run
    test_md = "# Test Entry\n\nThis is a **test** entry for the notebook logger.\n\n- Item 1\n- Item 2"
    log_to_notebook("Test_Entry", test_md)
