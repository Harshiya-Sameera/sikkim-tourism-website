import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    """Converts an HTML template into a PDF stream."""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    # Create the PDF
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None