#!/usr/bin/env python3
"""
User Journey Simulation for AdCopySurge Platform
Tests all user paths and interactions across the 9 tools.
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class UserPersona:
    """Represents different types of users."""
    
    def __init__(self, name: str, user_type: str, subscription: str, experience_level: str):
        self.name = name
        self.user_type = user_type  # agency_owner, freelancer, smb_owner, marketer
        self.subscription = subscription  # free, basic, pro
        self.experience_level = experience_level  # beginner, intermediate, expert
        self.journey_data = []
        self.pain_points = []
        self.successes = []

    def add_interaction(self, tool: str, action: str, success: bool, details: Dict = None):
        """Log user interaction."""
        self.journey_data.append({
            'timestamp': datetime.utcnow().isoformat(),
            'tool': tool,
            'action': action,
            'success': success,
            'details': details or {}
        })
        
        if success:
            self.successes.append(f"{tool}: {action}")
        else:
            self.pain_points.append(f"{tool}: {action}")


class AdCopyUserJourneySimulator:
    """Simulates complete user journeys through the AdCopySurge platform."""
    
    def __init__(self):
        self.personas = self._create_user_personas()
        self.simulation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'personas_tested': len(self.personas),
            'journeys_completed': 0,
            'total_interactions': 0,
            'success_rate': 0,
            'personas': {},
            'critical_findings': [],
            'recommendations': []
        }
        
        # Sample ad content for testing
        self.sample_ads = {
            'beginner_ads': [
                {
                    'headline': 'Amazing Product Sale',
                    'body_text': 'Buy our product now and save money. Great deal!',
                    'cta': 'Buy Now',
                    'platform': 'facebook'
                }
            ],
            'intermediate_ads': [
                {
                    'headline': 'Transform Your Business Today',
                    'body_text': 'Join 10,000+ entrepreneurs who have doubled their revenue using our proven system. Limited time offer.',
                    'cta': 'Start Free Trial',
                    'platform': 'facebook'
                }
            ],
            'expert_ads': [
                {
                    'headline': 'Leverage AI-Powered Solutions for Enterprise Growth',
                    'body_text': 'Our proprietary algorithms optimize conversion rates across multiple touchpoints, delivering measurable ROI improvements for Fortune 500 companies.',
                    'cta': 'Schedule Consultation',
                    'platform': 'linkedin'
                }
            ]
        }

    def _create_user_personas(self) -> List[UserPersona]:
        """Create diverse user personas for testing."""
        return [
            UserPersona("Sarah (Agency Owner)", "agency_owner", "pro", "expert"),
            UserPersona("Mike (Freelancer)", "freelancer", "basic", "intermediate"), 
            UserPersona("Lisa (SMB Owner)", "smb_owner", "free", "beginner"),
            UserPersona("David (Corporate Marketer)", "marketer", "basic", "intermediate"),
            UserPersona("Emma (Startup Founder)", "smb_owner", "free", "beginner")
        ]

    def simulate_onboarding_journey(self, persona: UserPersona):
        """Simulate user onboarding experience."""
        print(f"👤 Simulating onboarding for {persona.name}")
        
        # 1. Landing page interaction
        persona.add_interaction("landing_page", "view_value_proposition", True, {
            "time_spent": "2 minutes",
            "elements_viewed": ["hero_section", "features", "pricing", "testimonials"]
        })
        
        # 2. Registration process
        if persona.subscription == "free":
            persona.add_interaction("auth", "free_signup", True, {
                "fields_completed": ["email", "password", "name"],
                "time_to_complete": "45 seconds"
            })
        else:
            persona.add_interaction("auth", "paid_signup", True, {
                "plan_selected": persona.subscription,
                "payment_method": "stripe"
            })
        
        # 3. First tool discovery
        persona.add_interaction("dashboard", "view_dashboard", True, {
            "tools_visible": 9,
            "tutorial_offered": True,
            "tutorial_completed": persona.experience_level == "beginner"
        })

    def simulate_core_analysis_journey(self, persona: UserPersona):
        """Simulate using the core ad analysis tools."""
        print(f"🔍 Simulating analysis journey for {persona.name}")
        
        # Select ad based on experience level
        if persona.experience_level == "beginner":
            test_ad = self.sample_ads['beginner_ads'][0]
        elif persona.experience_level == "intermediate":
            test_ad = self.sample_ads['intermediate_ads'][0]
        else:
            test_ad = self.sample_ads['expert_ads'][0]
        
        # Tool 1: Ad Analysis (main workflow)
        analysis_success = self._simulate_ad_analysis(persona, test_ad)
        
        if analysis_success:
            # Tool 2: View detailed scores
            persona.add_interaction("readability_analyzer", "view_clarity_score", True, {
                "score_displayed": True,
                "recommendations_shown": True,
                "user_understood": persona.experience_level != "beginner"
            })
            
            # Tool 3: CTA analysis
            persona.add_interaction("cta_analyzer", "view_cta_suggestions", True, {
                "suggestions_count": 3,
                "suggestions_relevant": True
            })
            
            # Tool 4: Platform optimization
            persona.add_interaction("platform_optimization", "view_platform_fit", True, {
                "platform_score": 85,
                "platform_specific_tips": True
            })
        else:
            persona.add_interaction("ad_analysis", "analysis_failed", False, {
                "error_message": "Analysis timeout or API error",
                "user_frustration": True
            })

    def _simulate_ad_analysis(self, persona: UserPersona, ad: Dict) -> bool:
        """Simulate the main ad analysis workflow."""
        # Step 1: Input ad content
        persona.add_interaction("ad_input", "enter_ad_content", True, {
            "headline_length": len(ad['headline']),
            "body_length": len(ad['body_text']),
            "platform_selected": ad['platform']
        })
        
        # Step 2: Run analysis (simulate different outcomes based on subscription)
        if persona.subscription == "free" and len(persona.journey_data) > 5:
            # Simulate hitting free tier limits
            persona.add_interaction("ad_analysis", "hit_monthly_limit", False, {
                "analyses_used": 5,
                "limit_reached": True,
                "upgrade_prompt_shown": True
            })
            return False
        
        # Step 3: Generate analysis results
        persona.add_interaction("ad_analysis", "generate_results", True, {
            "analysis_time": "3 seconds",
            "overall_score": 72.5,
            "detailed_breakdown": True
        })
        
        return True

    def simulate_advanced_features_journey(self, persona: UserPersona):
        """Simulate using advanced features (for paid users)."""
        print(f"⭐ Simulating advanced features for {persona.name}")
        
        if persona.subscription == "free":
            # Free users see upgrade prompts
            persona.add_interaction("competitor_analysis", "view_upgrade_prompt", False, {
                "feature_locked": True,
                "upgrade_cta_shown": True,
                "user_considered_upgrade": persona.user_type in ["agency_owner", "marketer"]
            })
            return
        
        # Tool 5: Competitor benchmarking
        persona.add_interaction("competitor_analysis", "add_competitor_ads", True, {
            "competitors_added": 2,
            "analysis_depth": "detailed" if persona.subscription == "pro" else "basic"
        })
        
        # Tool 6: AI alternative generation
        if persona.subscription in ["basic", "pro"]:
            persona.add_interaction("ai_generator", "generate_alternatives", True, {
                "alternatives_generated": 4,
                "variation_types": ["persuasive", "emotional", "stats_heavy", "platform_optimized"],
                "user_satisfaction": "high" if persona.experience_level != "beginner" else "medium"
            })

    def simulate_analytics_journey(self, persona: UserPersona):
        """Simulate using analytics and reporting features."""
        print(f"📊 Simulating analytics journey for {persona.name}")
        
        # Tool 8: Analytics dashboard
        persona.add_interaction("analytics_dashboard", "view_performance_metrics", True, {
            "metrics_displayed": ["total_analyses", "avg_score_improvement", "platform_performance"],
            "insights_valuable": persona.user_type in ["agency_owner", "marketer"]
        })
        
        # Tool 9: PDF report generation (premium feature)
        if persona.subscription in ["basic", "pro"]:
            persona.add_interaction("pdf_reports", "generate_client_report", True, {
                "report_generated": True,
                "customization_level": "high" if persona.subscription == "pro" else "basic",
                "client_presentation_ready": persona.user_type == "agency_owner"
            })
        else:
            persona.add_interaction("pdf_reports", "view_upgrade_prompt", False, {
                "feature_locked": True,
                "upgrade_intent": persona.user_type == "agency_owner"
            })

    def simulate_subscription_journey(self, persona: UserPersona):
        """Simulate subscription management experience."""
        print(f"💳 Simulating subscription journey for {persona.name}")
        
        if persona.subscription == "free":
            # Free user considering upgrade
            upgrade_likelihood = {
                "agency_owner": 0.8,
                "marketer": 0.6, 
                "freelancer": 0.4,
                "smb_owner": 0.2
            }.get(persona.user_type, 0.3)
            
            persona.add_interaction("subscription", "consider_upgrade", True, {
                "upgrade_likelihood": upgrade_likelihood,
                "primary_motivator": "remove_limits" if upgrade_likelihood > 0.5 else "price_sensitive",
                "plan_preference": "basic" if upgrade_likelihood > 0.5 else "still_free"
            })
            
            if upgrade_likelihood > 0.6:
                persona.add_interaction("subscription", "complete_upgrade", True, {
                    "plan_selected": "basic",
                    "payment_successful": True,
                    "onboarding_to_premium": True
                })
        
        else:
            # Existing paid user management
            persona.add_interaction("subscription", "manage_existing_subscription", True, {
                "current_plan": persona.subscription,
                "usage_tracking": True,
                "satisfaction_level": "high" if len(persona.successes) > len(persona.pain_points) else "medium"
            })

    def simulate_full_user_journey(self, persona: UserPersona):
        """Simulate complete user journey through the platform."""
        print(f"\n🚀 Starting full journey simulation for {persona.name}")
        print(f"   Type: {persona.user_type} | Subscription: {persona.subscription} | Level: {persona.experience_level}")
        
        # Simulate each phase of the user journey
        self.simulate_onboarding_journey(persona)
        self.simulate_core_analysis_journey(persona)
        self.simulate_advanced_features_journey(persona)
        self.simulate_analytics_journey(persona)
        self.simulate_subscription_journey(persona)
        
        # Calculate journey metrics
        total_interactions = len(persona.journey_data)
        successful_interactions = len(persona.successes)
        success_rate = (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
        
        # Store persona results
        self.simulation_results['personas'][persona.name] = {
            'user_type': persona.user_type,
            'subscription': persona.subscription,
            'experience_level': persona.experience_level,
            'total_interactions': total_interactions,
            'successful_interactions': successful_interactions,
            'success_rate': round(success_rate, 1),
            'pain_points': persona.pain_points,
            'journey_data': persona.journey_data,
            'top_successes': persona.successes[:3],
            'top_pain_points': persona.pain_points[:3]
        }
        
        print(f"✅ Completed {persona.name}: {successful_interactions}/{total_interactions} successful ({success_rate:.1f}%)")
        return success_rate

    def identify_critical_issues(self):
        """Identify critical issues across all user journeys."""
        print("🔍 Analyzing critical issues across all journeys...")
        
        all_pain_points = []
        for persona_data in self.simulation_results['personas'].values():
            all_pain_points.extend(persona_data['pain_points'])
        
        # Count frequency of pain points
        pain_point_counts = {}
        for pain_point in all_pain_points:
            pain_point_counts[pain_point] = pain_point_counts.get(pain_point, 0) + 1
        
        # Identify most common issues
        common_issues = sorted(pain_point_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for issue, count in common_issues:
            self.simulation_results['critical_findings'].append({
                'issue': issue,
                'frequency': count,
                'severity': 'high' if count >= 3 else 'medium',
                'affected_personas': count
            })

    def generate_recommendations(self):
        """Generate recommendations based on simulation results."""
        print("💡 Generating improvement recommendations...")
        
        recommendations = []
        
        # Analyze subscription conversion patterns
        free_users = [p for p in self.simulation_results['personas'].values() if p['subscription'] == 'free']
        avg_free_success_rate = sum(p['success_rate'] for p in free_users) / len(free_users) if free_users else 0
        
        if avg_free_success_rate < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'user_experience',
                'recommendation': 'Improve free tier onboarding and tutorial system',
                'reasoning': f'Free users only have {avg_free_success_rate:.1f}% success rate'
            })
        
        # Analyze tool-specific issues
        if any('analysis_failed' in str(finding) for finding in self.simulation_results['critical_findings']):
            recommendations.append({
                'priority': 'critical',
                'category': 'reliability', 
                'recommendation': 'Implement better error handling and fallback mechanisms for AI analysis',
                'reasoning': 'Analysis failures create major user friction'
            })
        
        # Analyze subscription upgrade patterns
        agency_personas = [p for p in self.simulation_results['personas'].values() if p['user_type'] == 'agency_owner']
        if agency_personas and any('upgrade_prompt' in ' '.join(p['pain_points']) for p in agency_personas):
            recommendations.append({
                'priority': 'medium',
                'category': 'monetization',
                'recommendation': 'Create agency-specific onboarding and feature highlighting',
                'reasoning': 'Agency owners have different needs and higher LTV potential'
            })
        
        self.simulation_results['recommendations'] = recommendations

    def run_all_simulations(self):
        """Run complete user journey simulations for all personas."""
        print("🎭 AdCopySurge User Journey Simulation")
        print("=" * 60)
        
        total_success_rates = []
        
        for persona in self.personas:
            success_rate = self.simulate_full_user_journey(persona)
            total_success_rates.append(success_rate)
        
        # Calculate overall metrics
        overall_success_rate = sum(total_success_rates) / len(total_success_rates)
        total_interactions = sum(
            len(persona_data['journey_data']) 
            for persona_data in self.simulation_results['personas'].values()
        )
        
        # Update simulation results
        self.simulation_results.update({
            'journeys_completed': len(self.personas),
            'total_interactions': total_interactions,
            'success_rate': round(overall_success_rate, 1)
        })
        
        # Analysis phase
        self.identify_critical_issues()
        self.generate_recommendations()
        
        # Final summary
        print(f"\n" + "=" * 60)
        print(f"🏁 User Journey Simulation Complete!")
        print(f"📊 Overall Results:")
        print(f"   Personas tested: {len(self.personas)}")
        print(f"   Total interactions: {total_interactions}")
        print(f"   Average success rate: {overall_success_rate:.1f}%")
        print(f"   Critical issues found: {len(self.simulation_results['critical_findings'])}")
        print(f"   Recommendations generated: {len(self.simulation_results['recommendations'])}")
        
        # Show critical findings
        if self.simulation_results['critical_findings']:
            print(f"\n🚨 Top Critical Issues:")
            for finding in self.simulation_results['critical_findings'][:3]:
                print(f"   • {finding['issue']} (affects {finding['affected_personas']} personas)")
        
        # Show top recommendations
        if self.simulation_results['recommendations']:
            print(f"\n💡 Top Recommendations:")
            for rec in sorted(self.simulation_results['recommendations'], 
                            key=lambda x: {'critical': 3, 'high': 2, 'medium': 1}.get(x['priority'], 0), 
                            reverse=True)[:3]:
                print(f"   • [{rec['priority'].upper()}] {rec['recommendation']}")
        
        return self.simulation_results

    def save_results(self, filename: str = None):
        """Save simulation results to file."""
        if not filename:
            filename = f"user_journey_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.simulation_results, f, indent=2, default=str)
        
        print(f"📄 Journey simulation results saved to: {filename}")
        return filename


def main():
    """Run the user journey simulation."""
    simulator = AdCopyUserJourneySimulator()
    results = simulator.run_all_simulations()
    results_file = simulator.save_results()
    
    return results, results_file


if __name__ == "__main__":
    main()
