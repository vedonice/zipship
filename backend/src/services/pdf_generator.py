"""PDF generator for invoice creation."""
import logging
from io import BytesIO
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF invoices from bill data."""

    def __init__(self):
        """Initialize PDFGenerator."""
        # In production, would import reportlab or weasyprint:
        # try:
        #     from reportlab.lib.pagesizes import letter
        #     from reportlab.lib import colors
        #     from reportlab.lib.styles import getSampleStyleSheet
        #     from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        # except ImportError:
        #     logger.warning("reportlab not installed, PDF generation will be limited")
        pass

    def generate_invoice_pdf(
        self,
        bill_number: str,
        order_id: str,
        user_email: str,
        items: list,
        subtotal: Decimal,
        shipping_fee: Decimal,
        tax_amount: Decimal,
        total: Decimal,
        created_at: datetime = None,
    ) -> bytes:
        """Generate PDF invoice.

        Args:
            bill_number: Bill number (e.g., INV-2026-abc123)
            order_id: Order ID
            user_email: Customer email
            items: List of order items (each with product_name, quantity, unit_price, subtotal)
            subtotal: Items subtotal
            shipping_fee: Shipping fee
            tax_amount: Tax amount
            total: Grand total
            created_at: Invoice creation date (defaults to now)

        Returns:
            PDF bytes

        Raises:
            Exception: If PDF generation fails
        """
        try:
            if created_at is None:
                created_at = datetime.utcnow()

            logger.info(f"Generating PDF invoice: {bill_number}")

            # In production, this would generate a real PDF using reportlab:
            # from reportlab.lib.pagesizes import letter
            # from reportlab.lib import colors
            # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            # from reportlab.lib.units import inch
            #
            # buffer = BytesIO()
            # doc = SimpleDocTemplate(buffer, pagesize=letter)
            # elements = []
            #
            # # Add header
            # styles = getSampleStyleSheet()
            # elements.append(Paragraph(f"Invoice {bill_number}", styles['Heading1']))
            # elements.append(Spacer(1, 0.3 * inch))
            #
            # # Add invoice details
            # details = [
            #     ['Bill Number:', bill_number],
            #     ['Order ID:', order_id],
            #     ['Customer Email:', user_email],
            #     ['Date:', created_at.strftime('%Y-%m-%d %H:%M:%S')],
            # ]
            # details_table = Table(details)
            # elements.append(details_table)
            # elements.append(Spacer(1, 0.3 * inch))
            #
            # # Add line items
            # line_items = [['Product', 'Qty', 'Unit Price', 'Subtotal']]
            # for item in items:
            #     line_items.append([
            #         item['product_name'],
            #         str(item['quantity']),
            #         f"${item['unit_price']}",
            #         f"${item['subtotal']}"
            #     ])
            #
            # items_table = Table(line_items)
            # items_table.setStyle(TableStyle([
            #     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            #     ('FONTSIZE', (0, 0), (-1, 0), 14),
            #     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            #     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # ]))
            # elements.append(items_table)
            # elements.append(Spacer(1, 0.3 * inch))
            #
            # # Add totals
            # totals = [
            #     ['Subtotal:', f"${subtotal}"],
            #     ['Shipping:', f"${shipping_fee}"],
            #     ['Tax:', f"${tax_amount}"],
            #     ['Total:', f"${total}"],
            # ]
            # totals_table = Table(totals)
            # elements.append(totals_table)
            #
            # doc.build(elements)
            # buffer.seek(0)
            # return buffer.getvalue()

            # MVP: Generate simple HTML-like content as plain text (for testing)
            # In a real app, this would convert to PDF
            invoice_content = self._generate_invoice_html(
                bill_number=bill_number,
                order_id=order_id,
                user_email=user_email,
                items=items,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                tax_amount=tax_amount,
                total=total,
                created_at=created_at,
            )

            logger.info(f"PDF invoice generated: {bill_number}")
            return invoice_content.encode("utf-8")

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise

    def _generate_invoice_html(
        self,
        bill_number: str,
        order_id: str,
        user_email: str,
        items: list,
        subtotal: Decimal,
        shipping_fee: Decimal,
        tax_amount: Decimal,
        total: Decimal,
        created_at: datetime,
    ) -> str:
        """Generate HTML invoice representation (for MVP/testing).

        Args:
            bill_number: Bill number
            order_id: Order ID
            user_email: Customer email
            items: List of order items
            subtotal: Items subtotal
            shipping_fee: Shipping fee
            tax_amount: Tax amount
            total: Grand total
            created_at: Invoice creation date

        Returns:
            HTML string
        """
        date_str = created_at.strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice {bill_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .details {{ margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .totals {{ text-align: right; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>INVOICE</h1>
                <p><strong>{bill_number}</strong></p>
            </div>

            <div class="details">
                <p><strong>Bill Number:</strong> {bill_number}</p>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>Customer Email:</strong> {user_email}</p>
                <p><strong>Date:</strong> {date_str}</p>
            </div>

            <h2>Line Items</h2>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in items:
            html += f"""
                    <tr>
                        <td>{item['product_name']}</td>
                        <td>{item['quantity']}</td>
                        <td>${item['unit_price']}</td>
                        <td>${item['subtotal']}</td>
                    </tr>
            """

        html += f"""
                </tbody>
            </table>

            <div class="totals">
                <p><strong>Subtotal:</strong> ${subtotal}</p>
                <p><strong>Shipping:</strong> ${shipping_fee}</p>
                <p><strong>Tax:</strong> ${tax_amount}</p>
                <h3><strong>Total:</strong> ${total}</h3>
            </div>

            <p style="margin-top: 50px; font-size: 0.9em; color: #666;">
                Thank you for your purchase. Keep this invoice for your records.
            </p>
        </body>
        </html>
        """

        return html
