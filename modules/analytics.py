"""
Analytics Module

This module provides analytics and reporting capabilities for the day planner,
including progress charts, completion statistics, and data visualization.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


class Analytics:
    """
    Analytics and reporting system for the day planner.
    
    This class provides:
    - Progress tracking and visualization
    - Completion rate analysis
    - Weekly/monthly reports
    - Chart generation
    - Data export capabilities
    """
    
    def __init__(self, event_logger: Any, reports_dir: Optional[str] = None):
        """
        Initialize the analytics system.
        
        Args:
            event_logger: Event logger instance for data access.
            reports_dir: Directory for storing reports and charts.
        """
        self.logger = logging.getLogger(__name__)
        self.event_logger = event_logger
        
        # Setup reports directory
        if reports_dir is None:
            project_root = Path(__file__).parent.parent
            reports_dir = project_root / "reports"
        
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configure matplotlib for non-interactive backend
        plt.switch_backend('Agg')
        
        self.logger.info(f"Analytics initialized with reports directory: {self.reports_dir}")
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a daily completion report.
        
        Args:
            date: Date for the report (defaults to today).
            
        Returns:
            Dictionary containing daily statistics.
        """
        if date is None:
            date = datetime.now()
        
        try:
            # Get completion stats for the day
            stats = self.event_logger.get_completion_stats(days=1)
            
            # Calculate daily metrics
            total_tasks = sum(task['total_occurrences'] for task in stats['tasks'])
            completed_tasks = sum(task['completions'] for task in stats['tasks'])
            snoozed_tasks = sum(task.get('avg_snoozes', 0) for task in stats['tasks'])
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Get task breakdown
            task_breakdown = []
            for task in stats['tasks']:
                task_breakdown.append({
                    'title': task['task_title'],
                    'total': task['total_occurrences'],
                    'completed': task['completions'],
                    'completion_rate': task['completion_rate'],
                    'avg_snoozes': task.get('avg_snoozes', 0)
                })
            
            report = {
                'date': date.strftime('%Y-%m-%d'),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'snoozed_tasks': int(snoozed_tasks),
                'completion_rate': round(completion_rate, 2),
                'task_breakdown': task_breakdown,
                'generated_at': datetime.now().isoformat()
            }
            
            # Save report to file
            report_file = self.reports_dir / f"daily_report_{date.strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Daily report generated for {date.strftime('%Y-%m-%d')}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate daily report: {e}")
            return {}
    
    def generate_weekly_report(self, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a weekly completion report.
        
        Args:
            end_date: End date for the week (defaults to today).
            
        Returns:
            Dictionary containing weekly statistics.
        """
        if end_date is None:
            end_date = datetime.now()
        
        try:
            # Get completion stats for the week
            stats = self.event_logger.get_completion_stats(days=7)
            
            # Calculate weekly metrics
            total_tasks = sum(task['total_occurrences'] for task in stats['tasks'])
            completed_tasks = sum(task['completions'] for task in stats['tasks'])
            avg_completion_rate = np.mean([task['completion_rate'] for task in stats['tasks']]) if stats['tasks'] else 0
            
            # Get daily breakdown
            daily_stats = []
            for i in range(7):
                day_date = end_date - timedelta(days=i)
                daily_report = self.generate_daily_report(day_date)
                if daily_report:
                    daily_stats.append({
                        'date': day_date.strftime('%Y-%m-%d'),
                        'completion_rate': daily_report.get('completion_rate', 0),
                        'total_tasks': daily_report.get('total_tasks', 0),
                        'completed_tasks': daily_report.get('completed_tasks', 0)
                    })
            
            report = {
                'period': 'weekly',
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'avg_completion_rate': round(avg_completion_rate, 2),
                'daily_breakdown': daily_stats,
                'generated_at': datetime.now().isoformat()
            }
            
            # Save report to file
            report_file = self.reports_dir / f"weekly_report_{end_date.strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Weekly report generated ending {end_date.strftime('%Y-%m-%d')}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate weekly report: {e}")
            return {}
    
    def create_completion_chart(self, days: int = 7, save_path: Optional[str] = None) -> str:
        """
        Create a completion rate chart.
        
        Args:
            days: Number of days to include in the chart.
            save_path: Path to save the chart (optional).
            
        Returns:
            Path to the saved chart file.
        """
        try:
            # Get completion data
            stats = self.event_logger.get_completion_stats(days=days)
            
            if not stats['tasks']:
                self.logger.warning("No task data available for chart generation")
                return ""
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle(f'Day Planner Progress - Last {days} Days', fontsize=16, fontweight='bold')
            
            # Task completion rates
            task_names = [task['task_title'] for task in stats['tasks']]
            completion_rates = [task['completion_rate'] for task in stats['tasks']]
            colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in completion_rates]
            
            bars = ax1.bar(task_names, completion_rates, color=colors, alpha=0.7)
            ax1.set_ylabel('Completion Rate (%)')
            ax1.set_title('Task Completion Rates')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, rate in zip(bars, completion_rates):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Rotate x-axis labels for better readability
            ax1.tick_params(axis='x', rotation=45)
            
            # Daily completion trend
            dates = []
            daily_rates = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                daily_report = self.generate_daily_report(date)
                if daily_report and daily_report.get('total_tasks', 0) > 0:
                    dates.append(date)
                    daily_rates.append(daily_report.get('completion_rate', 0))
            
            if dates:
                dates.reverse()
                daily_rates.reverse()
                
                ax2.plot(dates, daily_rates, marker='o', linewidth=2, markersize=6)
                ax2.set_ylabel('Daily Completion Rate (%)')
                ax2.set_title('Daily Completion Trend')
                ax2.set_ylim(0, 100)
                ax2.grid(True, alpha=0.3)
                
                # Format x-axis dates
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = self.reports_dir / f"completion_chart_{timestamp}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Completion chart saved to: {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create completion chart: {e}")
            return ""
    
    def create_productivity_chart(self, days: int = 30, save_path: Optional[str] = None) -> str:
        """
        Create a productivity analysis chart.
        
        Args:
            days: Number of days to include in the analysis.
            save_path: Path to save the chart (optional).
            
        Returns:
            Path to the saved chart file.
        """
        try:
            # Get events data for analysis
            events = self.event_logger.get_events(limit=1000)
            
            if not events:
                self.logger.warning("No event data available for productivity analysis")
                return ""
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(events)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter to specified date range
            start_date = datetime.now() - timedelta(days=days)
            df = df[df['timestamp'] >= start_date]
            
            # Group by date and event type
            df['date'] = df['timestamp'].dt.date
            daily_stats = df.groupby(['date', 'event_type']).size().unstack(fill_value=0)
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle(f'Productivity Analysis - Last {days} Days', fontsize=16, fontweight='bold')
            
            # Daily activity heatmap
            if not daily_stats.empty:
                daily_stats.plot(kind='bar', ax=ax1, alpha=0.7)
                ax1.set_ylabel('Number of Events')
                ax1.set_title('Daily Activity by Event Type')
                ax1.legend(title='Event Type')
                ax1.tick_params(axis='x', rotation=45)
            
            # Completion vs Snooze ratio
            if 'task_completed' in daily_stats.columns and 'task_snoozed' in daily_stats.columns:
                completion_ratio = daily_stats['task_completed'] / (daily_stats['task_completed'] + daily_stats['task_snoozed'])
                completion_ratio = completion_ratio.fillna(0)
                
                ax2.plot(completion_ratio.index, completion_ratio.values, marker='o', linewidth=2, markersize=6)
                ax2.set_ylabel('Completion Ratio')
                ax2.set_title('Daily Completion vs Snooze Ratio')
                ax2.set_ylim(0, 1)
                ax2.grid(True, alpha=0.3)
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = self.reports_dir / f"productivity_chart_{timestamp}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Productivity chart saved to: {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create productivity chart: {e}")
            return ""
    
    def export_csv_report(self, days: int = 7, filename: Optional[str] = None) -> str:
        """
        Export task completion data to CSV format.
        
        Args:
            days: Number of days to include in the export.
            filename: Output filename (optional).
            
        Returns:
            Path to the exported CSV file.
        """
        try:
            # Get completion stats
            stats = self.event_logger.get_completion_stats(days=days)
            
            if not stats['tasks']:
                self.logger.warning("No task data available for CSV export")
                return ""
            
            # Convert to DataFrame
            df = pd.DataFrame(stats['tasks'])
            
            # Add date information
            df['report_date'] = datetime.now().strftime('%Y-%m-%d')
            df['period_days'] = days
            
            # Reorder columns
            columns = ['report_date', 'period_days', 'task_title', 'total_occurrences', 
                      'completions', 'completion_rate', 'avg_snoozes']
            df = df[columns]
            
            # Save to CSV
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = self.reports_dir / f"task_report_{timestamp}.csv"
            
            df.to_csv(filename, index=False)
            
            self.logger.info(f"CSV report exported to: {filename}")
            return str(filename)
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV report: {e}")
            return ""
    
    def get_summary_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics for the specified period.
        
        Args:
            days: Number of days to analyze.
            
        Returns:
            Dictionary containing summary statistics.
        """
        try:
            stats = self.event_logger.get_completion_stats(days=days)
            
            if not stats['tasks']:
                return {
                    'period_days': days,
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'avg_completion_rate': 0,
                    'best_performing_task': None,
                    'needs_attention_task': None
                }
            
            # Calculate summary metrics
            total_tasks = sum(task['total_occurrences'] for task in stats['tasks'])
            completed_tasks = sum(task['completions'] for task in stats['tasks'])
            avg_completion_rate = np.mean([task['completion_rate'] for task in stats['tasks']])
            
            # Find best and worst performing tasks
            best_task = max(stats['tasks'], key=lambda x: x['completion_rate'])
            worst_task = min(stats['tasks'], key=lambda x: x['completion_rate'])
            
            summary = {
                'period_days': days,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'avg_completion_rate': round(avg_completion_rate, 2),
                'best_performing_task': {
                    'title': best_task['task_title'],
                    'completion_rate': best_task['completion_rate']
                },
                'needs_attention_task': {
                    'title': worst_task['task_title'],
                    'completion_rate': worst_task['completion_rate']
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get summary stats: {e}")
            return {}
    
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """
        Clean up old report files.
        
        Args:
            days_to_keep: Number of days of reports to keep.
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for report_file in self.reports_dir.glob("*"):
                if report_file.is_file():
                    file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        report_file.unlink()
                        self.logger.debug(f"Deleted old report: {report_file}")
            
            self.logger.info(f"Cleaned up reports older than {days_to_keep} days")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old reports: {e}") 