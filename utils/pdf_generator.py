"""PDF generation utility using ReportLab."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List


class RFPAnalysisGenerator:
    """Generate formatted PDF analysis report from RFP data."""
    
    def __init__(self):
        """Initialize PDF generator with custom styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Bullet text style
        self.styles.add(ParagraphStyle(
            name='BulletText',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8,
            leading=14
        ))
        
        # Metadata style
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def generate_analysis_pdf(self, analysis: Dict[str, Any], 
                             rfp_filename: str = "RFP") -> BytesIO:
        """
        Generate analysis PDF from structured data.
        
        Args:
            analysis: Dictionary with analysis results from Claude
            rfp_filename: Original RFP filename for reference
        
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title page
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("RFP Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"Source: {rfp_filename}",
            self.styles['Metadata']
        ))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Metadata']
        ))
        story.append(PageBreak())
        
        # Section 1: Client Problems
        story.extend(self._create_bullet_section(
            "Client Problems & Challenges",
            analysis.get("client_problems", []),
            "Key issues and challenges the client is trying to resolve:"
        ))
        
        # Section 2: Requirements
        story.extend(self._create_bullet_section(
            "Specific Requirements",
            analysis.get("requirements", []),
            "Must-have requirements, deliverables, and constraints:"
        ))
        
        # Section 3: Gotchas
        story.extend(self._create_bullet_section(
            "Gotchas & Ambiguities",
            analysis.get("gotchas", []),
            "Red-flag items that need clarification:"
        ))
        
        # Section 4: Timeline
        story.extend(self._create_timeline_section(
            analysis.get("timeline", [])
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_bullet_section(self, title: str, items: List[str], 
                               intro: str = None) -> List:
        """
        Create a section with header and bullet points.
        
        Args:
            title: Section title
            items: List of bullet point strings
            intro: Optional introductory text
        
        Returns:
            List of reportlab flowables
        """
        elements = []
        
        # Section header
        elements.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Intro text if provided
        if intro:
            elements.append(Paragraph(intro, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Bullet points
        if items:
            for item in items:
                # Clean and format text
                item_text = str(item).strip()
                elements.append(Paragraph(
                    f"• {item_text}",
                    self.styles['BulletText']
                ))
        else:
            elements.append(Paragraph(
                "No items identified.",
                self.styles['Normal']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_timeline_section(self, timeline: List[Dict[str, str]]) -> List:
        """
        Create timeline section with formatted table.
        
        Args:
            timeline: List of dicts with 'event' and 'date' keys
        
        Returns:
            List of reportlab flowables
        """
        elements = []
        
        # Section header
        elements.append(Paragraph("Timeline & Key Dates", 
                                 self.styles['SectionHeader']))
        elements.append(Paragraph(
            "Important milestones and deadlines:",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 12))
        
        if timeline and len(timeline) > 0:
            # Prepare table data
            table_data = [["Event", "Date"]]
            
            for item in timeline:
                event = item.get("event", "Unknown Event")
                date = item.get("date", "TBD")
                table_data.append([event, date])
            
            # Create table
            table = Table(table_data, colWidths=[4*inch, 2*inch])
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Body styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                 [colors.white, colors.HexColor('#f3f4f6')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph(
                "No timeline information available.",
                self.styles['Normal']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
