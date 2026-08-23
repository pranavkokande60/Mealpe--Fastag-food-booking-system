import os
import io
import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from config import Config
from database.db import query_db

class PDFService:
    """
    Generates professional digital order receipts and executive admin reports in PDF format.
    """

    def generate_order_receipt_pdf(self, order_id: int) -> io.BytesIO:
        """
        Generates a modern digital invoice PDF receipt for a specific order.
        """
        order = query_db("""
            SELECT o.*, u.name as student_name, u.student_id as student_id_code, u.email as student_email, u.phone as student_phone
            FROM orders o
            JOIN users u ON o.student_id = u.id
            WHERE o.id = %s
        """, (order_id,), one=True)

        if not order:
            raise ValueError(f"Order #{order_id} not found.")

        items = query_db("""
            SELECT oi.*, f.name as food_name, f.calories
            FROM order_items oi
            JOIN food_items f ON oi.food_id = f.id
            WHERE oi.order_id = %s
        """, (order_id,)) or []

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#E23744'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'ReceiptSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            alignment=TA_LEFT
        )

        right_style = ParagraphStyle(
            'RightText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            alignment=TA_RIGHT
        )

        bold_label = ParagraphStyle(
            'BoldLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica-Bold'
        )

        elements = []

        # 1. Header Section
        header_data = [
            [
                Paragraph("<b>SMART CANTEEN</b><br/><font size=9 color='#64748B'>AI-Powered Campus Dining</font>", title_style),
                Paragraph(f"<b>TAX INVOICE / RECEIPT</b><br/>Invoice #: <b>{order['order_number']}</b><br/>Date: {order['created_at'].split()[0]}", right_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[280, 240])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E23744'), spaceAfter=15))

        # 2. Customer & Pickup Info
        cust_info = [
            [
                Paragraph(f"<b>Customer Details:</b><br/>Name: {order['student_name']}<br/>Student ID: {order['student_id_code'] or 'N/A'}<br/>Email: {order['student_email']}", subtitle_style),
                Paragraph(f"<b>Order Details:</b><br/>Status: <b>{order['order_status']}</b><br/>Payment: {order['payment_method'].upper()} ({order['payment_status']})<br/>Estimated Ready: <b>{order['pickup_time'] or 'Asap'}</b>", right_style)
            ]
        ]
        cust_table = Table(cust_info, colWidths=[280, 240])
        cust_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(cust_table)
        elements.append(Spacer(1, 20))

        # 3. Itemized Table
        table_data = [
            [
                Paragraph("<b>Item Description</b>", bold_label),
                Paragraph("<b>Qty</b>", bold_label),
                Paragraph("<b>Unit Price</b>", bold_label),
                Paragraph("<b>Subtotal</b>", right_style)
            ]
        ]

        for it in items:
            table_data.append([
                Paragraph(f"<b>{it['food_name']}</b><br/><font size=8 color='#64748B'>{it.get('calories', 250)} kcal</font>", subtitle_style),
                Paragraph(str(it['quantity']), subtitle_style),
                Paragraph(f"₹{it['unit_price']:.2f}", subtitle_style),
                Paragraph(f"₹{it['subtotal']:.2f}", right_style)
            ])

        # Financial breakdown rows
        table_data.append([
            "", "", Paragraph("<b>Subtotal:</b>", bold_label),
            Paragraph(f"₹{order['total_amount']:.2f}", right_style)
        ])
        if float(order.get('discount_amount', 0)) > 0:
            table_data.append([
                "", "", Paragraph("<b>Discount:</b>", bold_label),
                Paragraph(f"- ₹{order['discount_amount']:.2f}", right_style)
            ])
        table_data.append([
            "", "", Paragraph("<b>GST (5%):</b>", bold_label),
            Paragraph(f"₹{order['tax_amount']:.2f}", right_style)
        ])
        table_data.append([
            "", "", Paragraph("<b>GRAND TOTAL:</b>", title_style),
            Paragraph(f"<b>₹{order['final_amount']:.2f}</b>", title_style)
        ])

        items_table = Table(table_data, colWidths=[240, 50, 110, 120])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1, len(items)), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('LINEABOVE', (2, len(items)+1), (3, -1), 1, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 30))

        # 4. Footer Note
        elements.append(Paragraph("<b>Thank you for dining with Smart Canteen!</b>", ParagraphStyle('FooterBold', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#1E293B'))))
        elements.append(Paragraph("Please present this digital receipt or your Order ID at the pickup counter.", ParagraphStyle('FooterNote', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.HexColor('#64748B'))))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_admin_report_pdf(self, report_type: str = 'sales') -> io.BytesIO:
        """
        Generates executive admin summary reports for sales, demand, inventory, and wastage.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        elements = []

        title_text = {
            'sales': "CANTEEN EXECUTIVE SALES & REVENUE REPORT",
            'inventory': "SMART INVENTORY & STOCK VALUATION REPORT",
            'wastage': "FOOD WASTE ANALYSIS & PREVENTION REPORT",
            'demand': "AI DEMAND FORECAST & KITCHEN PRODUCTION PLAN"
        }.get(report_type, "CANTEEN EXECUTIVE MANAGEMENT REPORT")

        elements.append(Paragraph(f"<b>{title_text}</b>", ParagraphStyle('RepTitle', fontSize=18, leading=22, textColor=colors.HexColor('#E23744'), fontName='Helvetica-Bold')))
        elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Smart Canteen AI Platform", styles['Normal']))
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        if report_type == 'sales':
            orders = query_db("""
                SELECT o.order_number, u.name as student, o.final_amount, o.payment_method, o.order_status, o.created_at
                FROM orders o
                JOIN users u ON o.student_id = u.id
                ORDER BY o.created_at DESC LIMIT 25
            """) or []

            table_data = [["Order #", "Student", "Amount", "Payment", "Status", "Date/Time"]]
            for o in orders:
                table_data.append([
                    o['order_number'], o['student'], f"₹{o['final_amount']:.2f}",
                    o['payment_method'].upper(), o['order_status'], o['created_at']
                ])

            t = Table(table_data, colWidths=[80, 110, 70, 80, 80, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E23744')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 6),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            elements.append(t)

        elif report_type == 'inventory':
            items = query_db("SELECT * FROM inventory ORDER BY current_stock ASC") or []
            table_data = [["Item Name", "Category", "Current Stock", "Unit", "Min Reorder", "Status"]]
            for it in items:
                table_data.append([
                    it['item_name'], it['category'], str(it['current_stock']),
                    it['unit'], str(it['min_threshold']), it['status']
                ])
            t = Table(table_data, colWidths=[140, 90, 80, 60, 70, 80])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 6),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            elements.append(t)

        doc.build(elements)
        buffer.seek(0)
        return buffer

# Singleton instance
pdf_service = PDFService()
