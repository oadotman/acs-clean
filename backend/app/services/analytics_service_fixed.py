from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import base64
from app.models.ad_analysis import AdAnalysis
from app.models.user import User

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        analyses = self.db.query(AdAnalysis).filter(AdAnalysis.user_id == user_id).all()
        
        if not analyses:
            return {
                'total_analyses': 0,
                'avg_score_improvement': 0,
                'top_performing_platforms': [],
                'monthly_usage': {},
                'subscription_analytics': {}
            }
        
        total_analyses = len(analyses)
        avg_score = sum(a.overall_score for a in analyses) / total_analyses
        
        platform_stats = {}
        for analysis in analyses:
            platform = analysis.platform
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'total_score': 0}
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['total_score'] += analysis.overall_score
        
        top_performing_platforms = [
            {
                'platform': platform,
                'avg_score': stats['total_score'] / stats['count'],
                'count': stats['count']
            }
            for platform, stats in platform_stats.items()
        ]
        top_performing_platforms.sort(key=lambda x: x['avg_score'], reverse=True)
        
        monthly_usage = self._get_monthly_usage(user_id)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        subscription_analytics = {
            'current_tier': user.subscription_tier.value if user else 'free',
            'monthly_analyses': user.monthly_analyses if user else 0,
            'account_age_days': (datetime.utcnow() - user.created_at).days if user else 0
        }
        
        return {
            'total_analyses': total_analyses,
            'avg_score_improvement': round(avg_score, 1),
            'top_performing_platforms': top_performing_platforms,
            'monthly_usage': monthly_usage,
            'subscription_analytics': subscription_analytics
        }
    
    def _get_monthly_usage(self, user_id: int) -> List[Dict]:
        """Get monthly usage statistics"""
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        monthly_data = self.db.query(
            func.date_trunc('month', AdAnalysis.created_at).label('month'),
            func.count(AdAnalysis.id).label('analyses'),
            func.avg(AdAnalysis.overall_score).label('avg_score')
        ).filter(
            AdAnalysis.user_id == user_id,
            AdAnalysis.created_at >= six_months_ago
        ).group_by(
            func.date_trunc('month', AdAnalysis.created_at)
        ).order_by(
            func.date_trunc('month', AdAnalysis.created_at)
        ).all()
        
        return [
            {
                'month': row.month.strftime('%b %Y'),
                'analyses': row.analyses,
                'avg_score': round(float(row.avg_score), 1) if row.avg_score else 0
            }
            for row in monthly_data
        ]
    
    async def generate_pdf_report(self, user_id: int, analysis_ids: List[str]) -> Dict[str, str]:
        """Generate PDF report for selected analyses"""
        analyses = self.db.query(AdAnalysis).filter(
            AdAnalysis.user_id == user_id,
            AdAnalysis.id.in_(analysis_ids)
        ).all()
        
        if not analyses:
            raise ValueError("No analyses found")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        title = Paragraph("AdCopySurge Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        avg_score = sum(a.overall_score for a in analyses) / len(analyses)
        summary_text = f"""Report Generated: {datetime.utcnow().strftime('%B %d, %Y')}<br/>
        Total Analyses: {len(analyses)}<br/>
        Average Score: {avg_score:.1f}/100<br/>"""
        
        summary = Paragraph(summary_text, styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 20))
        
        for i, analysis in enumerate(analyses, 1):
            header = Paragraph(f"Analysis #{i}: {analysis.headline}", styles['Heading2'])
            story.append(header)
            
            scores_data = [
                ['Metric', 'Score'],
                ['Overall Score', f"{analysis.overall_score:.1f}/100"],
                ['Clarity', f"{analysis.clarity_score:.1f}/100"],
                ['Persuasion', f"{analysis.persuasion_score:.1f}/100"],
                ['Emotion', f"{analysis.emotion_score:.1f}/100"],
                ['CTA Strength', f"{analysis.cta_strength_score:.1f}/100"],
                ['Platform Fit', f"{analysis.platform_fit_score:.1f}/100"],
            ]
            
            scores_table = Table(scores_data)
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(scores_table)
            story.append(Spacer(1, 20))
            
            content_text = f"""<br/>
            <b>Platform:</b> {analysis.platform}<br/>
            <b>Headline:</b> {analysis.headline}<br/>
            <b>Body:</b> {analysis.body_text}<br/>
            <b>CTA:</b> {analysis.cta}<br/>"""
            
            content = Paragraph(content_text, styles['Normal'])
            story.append(content)
            story.append(Spacer(1, 30))
        
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return {
            'url': f"data:application/pdf;base64,{pdf_base64}",
            'download_link': f"report_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        }
