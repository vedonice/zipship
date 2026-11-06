"""PDF generation service for invoices."""
import io
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


class PDFService:
    """Service for generating PDF invoices."""

    @staticmethod
    def generate_invoice_pdf(bill_data: dict) -> bytes:
        """Generate PDF invoice from bill data.

        Args:
            bill_data: Bill dict with items, totals, etc.

        Returns:
            PDF bytes
        """
        # Create in-memory PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Container for PDF elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#007bff'),
            spaceAfter=6,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333'),
            spaceAfter=6,
        )

        # Title
        elements.append(Paragraph(f"Invoice #{bill_data.get('bill_number', 'N/A')}", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Invoice details
        bill_date = bill_data.get('created_at', '')
        if bill_date:
            bill_date = datetime.fromisoformat(bill_date).strftime('%B %d, %Y')
        elements.append(Paragraph(f"<b>Date:</b> {bill_date}", styles['Normal']))
        elements.append(Paragraph(f"<b>Order ID:</b> {bill_data.get('order_id', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Items table
        elements.append(Paragraph("Items Ordered", heading_style))

        # Build items table
        items_data = [['Product', 'Qty', 'Unit Price', 'Subtotal']]
        items = bill_data.get('items', [])
        if isinstance(items, str):
            items = json.loads(items)

        for item in items:
            items_data.append([
                item.get('product_name', ''),
                str(item.get('quantity', 0)),
                f"${float(item.get('unit_price', 0)):.2f}",
                f"${float(item.get('subtotal', 0)):.2f}",
            ])

        items_table = Table(items_data)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9f9f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 0.2*inch))

        # Summary
        elements.append(Paragraph("Order Summary", heading_style))
        summary_data = [
            ['Subtotal:', f"${float(bill_data.get('subtotal', 0)):.2f}"],
            ['Shipping:', f"${float(bill_data.get('shipping_fee', 0)):.2f}"],
            ['Tax:', f"${float(bill_data.get('tax_amount', 0)):.2f}"],
            ['Total:', f"${float(bill_data.get('total', 0)):.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ]))
        elements.append(summary_table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
