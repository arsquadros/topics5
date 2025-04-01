import pdfkit


html = """
<html>
    <body>
        <h1>Test</h1>
    </body>
</html>
"""

pdfkit.from_string(html, f"app/tmp/test.pdf")