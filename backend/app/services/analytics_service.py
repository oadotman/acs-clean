from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta
import io
import base64
from app.models.ad_analysis import AdAnalysis
from app.models.user import User

# Optional imports for PDF generation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not available - PDF generation disabled")

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        # Get user's analyses
        analyses = self.db.query(AdAnalysis)\
                          .filter(AdAnalysis.user_id == user_id)\
                          .all()
        
        if not analyses:
            return {
                'total_analyses': 0,
                'avg_score_improvement': 0,
                'top_performing_platforms': [],
                'monthly_usage': {},
                'subscription_analytics': {}
            }
        
        # Calculate metrics
        total_analyses = len(analyses)
        avg_score = sum(a.overall_score for a in analyses) / total_analyses
        
        # Platform performance
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
        
        # Monthly usage (last 6 months)
        monthly_usage = self._get_monthly_usage(user_id)
        
        # Subscription analytics
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
        """Get monthly usage statistics for last 6 months"""
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        # Query monthly data
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
        # Get analyses
        analyses = self.db.query(AdAnalysis)\
                          .filter(
                              AdAnalysis.user_id == user_id,
                              AdAnalysis.id.in_(analysis_ids)
                          )\
                          .all()
        
        if not analyses:
            raise ValueError("No analyses found")
        
        # Calculate summary stats
        avg_score = sum(a.overall_score for a in analyses) / len(analyses)
        summary_text = f"""Report Generated: {datetime.utcnow().strftime('%B %d, %Y')}
Total Analyses: {len(analyses)}
Average Score: {avg_score:.1f}/100
"""
        
        # Check if ReportLab is available for PDF generation
        if not REPORTLAB_AVAILABLE:
            return {
                'message': 'PDF generation requires ReportLab package - providing summary instead',
                'summary': summary_text,
                'total_analyses': len(analyses),
                'average_score': round(avg_score, 1),
                'analyses_included': [{'id': str(a.id), 'headline': a.headline, 'score': a.overall_score} for a in analyses]
            }
        
        # Generate PDF with ReportLab
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("AdCopySurge Analysis Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Summary paragraph
            summary_para = Paragraph(summary_text.replace('\n', '<br/>'), styles['Normal'])
            story.append(summary_para)
            story.append(Spacer(1, 20))
            
            # Build and return PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return {
                'message': 'PDF report generated successfully',
                'pdf_data': base64.b64encode(pdf_data).decode('utf-8'),
                'total_analyses': len(analyses),
                'average_score': round(avg_score, 1)
            }
        except Exception as e:
            return {
                'message': f'PDF generation failed: {str(e)}',
                'summary': summary_text,
                'total_analyses': len(analyses),
                'average_score': round(avg_score, 1)
            }
    
    def get_platform_performance(self, user_id: int) -> Dict[str, Any]:
        """Get performance breakdown by platform"""
        platform_stats = self.db.query(
            AdAnalysis.platform,
            func.count(AdAnalysis.id).label('count'),
            func.avg(AdAnalysis.overall_score).label('avg_score'),
            func.max(AdAnalysis.overall_score).label('max_score')
        ).filter(
            AdAnalysis.user_id == user_id
        ).group_by(
            AdAnalysis.platform
        ).all()
        
        return [
            {
                'platform': row.platform,
                'total_analyses': row.count,
                'avg_score': round(float(row.avg_score), 1),
                'best_score': round(float(row.max_score), 1)
            }
            for row in platform_stats
        ]
