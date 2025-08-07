#!/usr/bin/env python3
"""
Real-time UX Analytics Dashboard
Provides live monitoring and visualization of UX analysis results
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class AnalyticsMetric:
    """Structure for analytics metrics"""
    metric_name: str
    value: float
    timestamp: datetime
    app_type: str
    category: str

@dataclass
class DashboardAlert:
    """Structure for dashboard alerts"""
    alert_id: str
    title: str
    message: str
    severity: str
    timestamp: datetime
    app_type: str
    resolved: bool = False

class UXAnalyticsDatabase:
    """SQLite database for storing UX analytics data"""
    
    def __init__(self, db_path: str = "ux_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME NOT NULL,
                app_type TEXT NOT NULL,
                total_scenarios INTEGER NOT NULL,
                total_issues INTEGER NOT NULL,
                ai_enabled BOOLEAN NOT NULL,
                results_json TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ux_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                app_type TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                scenario_title TEXT NOT NULL,
                issue_title TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                work_item_id INTEGER NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                app_type TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                app_type TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_test_run(self, results_data: Dict[str, Any]):
        """Store test run results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert test run
            cursor.execute("""
                INSERT OR REPLACE INTO test_runs 
                (run_id, timestamp, app_type, total_scenarios, total_issues, ai_enabled, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                results_data.get("test_run_id", "unknown"),
                results_data.get("timestamp", datetime.now().isoformat()),
                results_data.get("app_type", "unknown"),
                results_data.get("scenarios_tested", 0),
                results_data.get("total_issues_found", 0),
                results_data.get("ai_analysis_enabled", False),
                json.dumps(results_data)
            ))
            
            # Extract and store individual issues
            run_id = results_data.get("test_run_id", "unknown")
            app_type = results_data.get("app_type", "unknown")
            
            if "scenarios" in results_data:
                for scenario_id, scenario_data in results_data["scenarios"].items():
                    if isinstance(scenario_data, dict) and "issues" in scenario_data:
                        for issue in scenario_data["issues"]:
                            self._store_ux_issue(cursor, run_id, app_type, scenario_id, scenario_data, issue)
            
            elif "app_results" in results_data:
                for app_type, app_data in results_data["app_results"].items():
                    for scenario_id, scenario_data in app_data.get("scenarios", {}).items():
                        if isinstance(scenario_data, dict) and "issues" in scenario_data:
                            for issue in scenario_data["issues"]:
                                self._store_ux_issue(cursor, run_id, app_type, scenario_id, scenario_data, issue)
            
            conn.commit()
            
        except Exception as e:
            print(f"Error storing test run: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _store_ux_issue(self, cursor, run_id: str, app_type: str, scenario_id: str, scenario_data: Dict, issue: Any):
        """Store individual UX issue"""
        
        if isinstance(issue, dict):
            issue_title = issue.get("category", "General Issue")
            issue_description = issue.get("description", str(issue))
            category = issue.get("category", "General")
            severity = issue.get("severity", "medium")
        else:
            issue_title = f"UX Issue in {scenario_data.get('title', scenario_id)}"
            issue_description = str(issue)
            category = "General"
            severity = "medium"
        
        cursor.execute("""
            INSERT INTO ux_issues 
            (run_id, app_type, scenario_id, scenario_title, issue_title, issue_description, category, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            app_type,
            scenario_id,
            scenario_data.get("title", scenario_id),
            issue_title,
            issue_description,
            category,
            severity,
            datetime.now().isoformat()
        ))
    
    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            # Total metrics
            cursor.execute("""
                SELECT COUNT(*) as total_runs, SUM(total_scenarios) as total_scenarios, 
                       SUM(total_issues) as total_issues
                FROM test_runs 
                WHERE timestamp >= ?
            """, (cutoff_date,))
            
            totals = cursor.fetchone()
            
            # Issues by app type
            cursor.execute("""
                SELECT app_type, COUNT(*) as issue_count
                FROM ux_issues 
                WHERE timestamp >= ?
                GROUP BY app_type
                ORDER BY issue_count DESC
            """, (cutoff_date,))
            
            issues_by_app = dict(cursor.fetchall())
            
            # Issues by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as issue_count
                FROM ux_issues 
                WHERE timestamp >= ?
                GROUP BY severity
                ORDER BY 
                    CASE severity 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                        ELSE 4 
                    END
            """, (cutoff_date,))
            
            issues_by_severity = dict(cursor.fetchall())
            
            # Issues by category
            cursor.execute("""
                SELECT category, COUNT(*) as issue_count
                FROM ux_issues 
                WHERE timestamp >= ?
                GROUP BY category
                ORDER BY issue_count DESC
                LIMIT 10
            """, (cutoff_date,))
            
            issues_by_category = dict(cursor.fetchall())
            
            # Daily trend
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as issue_count
                FROM ux_issues 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (cutoff_date,))
            
            daily_trend = dict(cursor.fetchall())
            
            return {
                "period_days": days,
                "total_runs": totals[0] or 0,
                "total_scenarios": totals[1] or 0,
                "total_issues": totals[2] or 0,
                "issues_by_app": issues_by_app,
                "issues_by_severity": issues_by_severity,
                "issues_by_category": issues_by_category,
                "daily_trend": daily_trend,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting analytics summary: {e}")
            return {}
        finally:
            conn.close()
    
    def store_alert(self, alert: DashboardAlert):
        """Store dashboard alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO dashboard_alerts 
                (alert_id, title, message, severity, timestamp, app_type, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.title,
                alert.message,
                alert.severity,
                alert.timestamp.isoformat(),
                alert.app_type,
                alert.resolved
            ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error storing alert: {e}")
        finally:
            conn.close()
    
    def get_active_alerts(self) -> List[DashboardAlert]:
        """Get active dashboard alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT alert_id, title, message, severity, timestamp, app_type, resolved
                FROM dashboard_alerts 
                WHERE resolved = FALSE
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            
            alerts = []
            for row in cursor.fetchall():
                alert = DashboardAlert(
                    alert_id=row[0],
                    title=row[1],
                    message=row[2],
                    severity=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    app_type=row[5],
                    resolved=bool(row[6])
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
        finally:
            conn.close()

class UXAnalyticsDashboard:
    """Real-time UX analytics dashboard"""
    
    def __init__(self):
        self.db = UXAnalyticsDatabase()
        self.alert_thresholds = {
            "high_issue_count": 10,      # Alert if more than 10 issues per run
            "critical_severity_count": 3, # Alert if more than 3 critical issues
            "failure_rate": 0.5          # Alert if 50% of scenarios fail
        }
    
    def process_analysis_results(self, results_file: str):
        """Process and store analysis results"""
        
        print(f"📊 Processing analysis results: {results_file}")
        
        try:
            with open(results_file, 'r') as f:
                results_data = json.load(f)
            
            # Store in database
            self.db.store_test_run(results_data)
            
            # Check for alerts
            self._check_alert_conditions(results_data)
            
            print(f"   ✅ Results processed and stored")
            
        except Exception as e:
            print(f"   ❌ Error processing results: {e}")
    
    def _check_alert_conditions(self, results_data: Dict[str, Any]):
        """Check for alert conditions and create alerts if needed"""
        
        total_issues = results_data.get("total_issues_found", 0)
        total_scenarios = results_data.get("scenarios_tested", 1)
        app_type = results_data.get("app_type", "unknown")
        
        # High issue count alert
        if total_issues > self.alert_thresholds["high_issue_count"]:
            alert = DashboardAlert(
                alert_id=f"high_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=f"High Issue Count in {app_type.title()}",
                message=f"Found {total_issues} issues in {total_scenarios} scenarios (avg: {total_issues/total_scenarios:.1f})",
                severity="medium",
                timestamp=datetime.now(),
                app_type=app_type
            )
            self.db.store_alert(alert)
        
        # Check for critical severity issues
        critical_count = 0
        if "scenarios" in results_data:
            for scenario_data in results_data["scenarios"].values():
                if isinstance(scenario_data, dict) and "issues" in scenario_data:
                    for issue in scenario_data["issues"]:
                        if isinstance(issue, dict) and issue.get("severity") == "high":
                            critical_count += 1
        
        if critical_count > self.alert_thresholds["critical_severity_count"]:
            alert = DashboardAlert(
                alert_id=f"critical_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=f"Critical Issues Detected in {app_type.title()}",
                message=f"Found {critical_count} critical severity issues requiring immediate attention",
                severity="high",
                timestamp=datetime.now(),
                app_type=app_type
            )
            self.db.store_alert(alert)
    
    def generate_dashboard_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive dashboard report"""
        
        print(f"📈 Generating dashboard report for last {days} days...")
        
        # Get analytics summary
        analytics = self.db.get_analytics_summary(days)
        
        # Get active alerts
        alerts = self.db.get_active_alerts()
        
        # Calculate additional metrics
        metrics = self._calculate_dashboard_metrics(analytics)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "summary": analytics,
            "metrics": metrics,
            "alerts": [asdict(alert) for alert in alerts],
            "recommendations": self._generate_recommendations(analytics, alerts)
        }
        
        return report
    
    def _calculate_dashboard_metrics(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional dashboard metrics"""
        
        total_issues = analytics.get("total_issues", 0)
        total_scenarios = analytics.get("total_scenarios", 1)
        
        return {
            "average_issues_per_scenario": total_issues / total_scenarios if total_scenarios > 0 else 0,
            "issue_resolution_rate": 0.0,  # Would come from work item tracking
            "most_problematic_app": max(analytics.get("issues_by_app", {}).items(), key=lambda x: x[1], default=("none", 0))[0],
            "most_common_category": max(analytics.get("issues_by_category", {}).items(), key=lambda x: x[1], default=("none", 0))[0],
            "severity_distribution": analytics.get("issues_by_severity", {}),
            "trend_direction": self._calculate_trend_direction(analytics.get("daily_trend", {}))
        }
    
    def _calculate_trend_direction(self, daily_trend: Dict[str, int]) -> str:
        """Calculate if issues are trending up, down, or stable"""
        
        if len(daily_trend) < 2:
            return "insufficient_data"
        
        dates = sorted(daily_trend.keys())
        recent_avg = sum(daily_trend[date] for date in dates[-3:]) / min(3, len(dates))
        earlier_avg = sum(daily_trend[date] for date in dates[:-3]) / max(1, len(dates) - 3)
        
        if recent_avg > earlier_avg * 1.2:
            return "increasing"
        elif recent_avg < earlier_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(self, analytics: Dict[str, Any], alerts: List[DashboardAlert]) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        
        recommendations = []
        
        # High issue count recommendations
        if analytics.get("total_issues", 0) > 50:
            recommendations.append("Consider prioritizing UX improvements - high issue count detected across scenarios")
        
        # App-specific recommendations
        issues_by_app = analytics.get("issues_by_app", {})
        if issues_by_app:
            most_problematic = max(issues_by_app.items(), key=lambda x: x[1])
            recommendations.append(f"Focus UX attention on {most_problematic[0].title()} application - highest issue count ({most_problematic[1]} issues)")
        
        # Severity recommendations
        severity_dist = analytics.get("issues_by_severity", {})
        if severity_dist.get("high", 0) > 5:
            recommendations.append("Address high-severity issues immediately - user experience significantly impacted")
        
        # Alert-based recommendations
        high_severity_alerts = [a for a in alerts if a.severity == "high"]
        if high_severity_alerts:
            recommendations.append(f"Urgent: {len(high_severity_alerts)} critical alerts require immediate attention")
        
        return recommendations
    
    def save_dashboard_report(self, report: Dict[str, Any], filename: str = None):
        """Save dashboard report to file"""
        
        if filename is None:
            filename = f"ux_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Dashboard report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save dashboard report: {e}")
    
    def monitor_results_directory(self, directory: str = ".", pattern: str = "test_results_*.json"):
        """Monitor directory for new analysis results and process them"""
        
        print(f"👁️  Monitoring {directory} for new analysis results...")
        
        processed_files = set()
        
        while True:
            try:
                # Find new result files
                result_files = list(Path(directory).glob(pattern))
                new_files = [f for f in result_files if str(f) not in processed_files]
                
                for file_path in new_files:
                    print(f"📥 New results detected: {file_path}")
                    self.process_analysis_results(str(file_path))
                    processed_files.add(str(file_path))
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(30)  # Wait longer on errors

def main():
    """Main execution for dashboard demonstration"""
    
    print("📊 UX Analytics Dashboard - Phase 2.5")
    print("=" * 50)
    
    # Initialize dashboard
    dashboard = UXAnalyticsDashboard()
    
    # Process any existing result files
    result_files = list(Path(".").glob("test_results_*.json"))
    
    if result_files:
        print(f"📁 Found {len(result_files)} existing result files")
        
        for result_file in result_files[-3:]:  # Process last 3 files
            print(f"   📊 Processing: {result_file}")
            dashboard.process_analysis_results(str(result_file))
    
    # Generate dashboard report
    print(f"\n📈 Generating dashboard report...")
    report = dashboard.generate_dashboard_report()
    
    # Save report
    dashboard.save_dashboard_report(report)
    
    # Print summary
    print(f"\n📊 Dashboard Summary:")
    print(f"   🧪 Total scenarios tested: {report['summary'].get('total_scenarios', 0)}")
    print(f"   🐛 Total issues found: {report['summary'].get('total_issues', 0)}")
    print(f"   ⚠️  Active alerts: {len(report['alerts'])}")
    print(f"   📈 Trend: {report['metrics']['trend_direction']}")
    
    if report['recommendations']:
        print(f"\n💡 Top recommendations:")
        for i, rec in enumerate(report['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    
    print("\n✅ Dashboard analysis completed!")

if __name__ == "__main__":
    main()
