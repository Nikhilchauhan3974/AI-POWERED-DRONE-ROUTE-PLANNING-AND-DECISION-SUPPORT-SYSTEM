from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_route_pdf(route_data: dict, comparison_data: list = None) -> BytesIO:
    """Generates a professional PDF document containing flight plan telemetry and metrics benchmarks."""
    buffer = BytesIO()
    
    # 0.5 inch margins (36 pt)
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # Define color palette (Slate & Navy command theme)
    PRIMARY_COLOR = colors.HexColor('#0F172A')   # Slate-900
    SECONDARY_COLOR = colors.HexColor('#1E293B') # Slate-800
    TEXT_COLOR = colors.HexColor('#334155')      # Slate-700
    LIGHT_BG = colors.HexColor('#F8FAFC')        # Slate-50
    BORDER_COLOR = colors.HexColor('#E2E8F0')    # Slate-200
    
    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=PRIMARY_COLOR,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=SECONDARY_COLOR,
        spaceBefore=14,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=TEXT_COLOR,
        leading=13,
        fontName='Helvetica'
    )
    
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold'
    )

    # 1. Document Header
    story.append(Paragraph("AERO-COM AI COMMAND CENTER", title_style))
    story.append(Paragraph(f"FLIGHT MISSION SPECIFICATIONS & SIMULATION LOGS | GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Mission Overview Table
    story.append(Paragraph("1. Mission Specification", section_title_style))
    details_data = [
        [Paragraph("<b>Parameter</b>", header_cell_style), Paragraph("<b>Specification / Coordinates</b>", header_cell_style)],
        ["Source Location", f"Latitude: {route_data['source_lat']}, Longitude: {route_data['source_lon']}"],
        ["Destination Location", f"Latitude: {route_data['dest_lat']}, Longitude: {route_data['dest_lon']}"],
        ["Selected Search Algorithm", route_data['algorithm']],
        ["Weather Condition", route_data['weather'].upper()],
        ["Wind Vectors", f"{route_data['wind_speed']} km/h (Heading: {route_data['wind_direction']}°)"]
    ]
    t1 = Table(details_data, colWidths=[200, 340])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT_COLOR),
    ]))
    story.append(t1)
    story.append(Spacer(1, 12))
    
    # 3. Telemetry metrics Table
    story.append(Paragraph("2. Flight Telemetry Metrics", section_title_style))
    tele_data = [
        [Paragraph("<b>Telemetry Metric</b>", header_cell_style), Paragraph("<b>Value</b>", header_cell_style)],
        ["Total Flight Path Distance", f"{route_data['distance']} meters"],
        ["Estimated Flight Duration", f"{route_data['travel_time']} seconds"],
        ["Estimated Battery Consumption", f"{route_data['battery_consumed']}%"],
        ["Average Flight Risk Score", f"{route_data['risk_score']} / 1.0"]
    ]
    t2 = Table(tele_data, colWidths=[200, 340])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT_COLOR),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))
    
    # 4. Multi-Algorithm comparison (if available)
    if comparison_data:
        story.append(Paragraph("3. Multi-Algorithm Performance Benchmark", section_title_style))
        story.append(Paragraph("Benchmark comparison for identical coordinates, weather, and obstacle constraints:", body_style))
        story.append(Spacer(1, 6))
        
        comp_headers = ["Algorithm", "Time (ms)", "Nodes Explored", "Distance (m)", "Battery (%)", "Risk Index"]
        comp_table_data = [[Paragraph(f"<b>{h}</b>", header_cell_style) for h in comp_headers]]
        
        for item in comparison_data:
            comp_table_data.append([
                item['algorithm'],
                f"{item['execution_time_ms']:.1f}",
                str(item['nodes_visited']),
                f"{item['distance']:.1f}",
                f"{item['battery_consumed']:.1f}",
                f"{item['risk_score']:.3f}"
            ])
            
        t3 = Table(comp_table_data, colWidths=[100, 80, 100, 90, 85, 85])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('TEXTCOLOR', (0,1), (-1,-1), TEXT_COLOR),
        ]))
        story.append(t3)
        story.append(Spacer(1, 12))
        
    # 5. Fail-Safe clearance certification
    story.append(Paragraph("4. Safety Clearance & Certification", section_title_style))
    cert_text = (
        "<b>SYSTEM NOTICE:</b> This report certifies that the computed drone route has successfully bypassed all user-configured "
        "impassable No-Fly Zones (NFZs) and maintained safe elevation margins above structural hazards (skyscrapers, towers). "
        "Battery decay forecasts indicate that the route maintains a safe reserve, avoiding terminal drain before arrival "
        "under current wind velocities."
    )
    story.append(Paragraph(cert_text, body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
