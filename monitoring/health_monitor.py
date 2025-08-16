#!/usr/bin/env python3
"""
Gurukul Platform - Comprehensive Health Monitor
Continuous monitoring with alerting and metrics collection
"""

import asyncio
import aiohttp
import time
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/gurukul-health.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.services = {
            'frontend': {'url': 'http://frontend:80', 'timeout': 10},
            'backend': {'url': 'http://backend:8000/health', 'timeout': 15},
            'mongodb': {'url': 'http://backend:8000/health', 'timeout': 10},
            'redis': {'url': 'http://backend:8000/health', 'timeout': 10},
            'nginx': {'url': 'http://nginx:80/health', 'timeout': 5}
        }
        
        self.metrics = {
            'uptime': {},
            'response_times': {},
            'error_counts': {},
            'last_check': {}
        }
        
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.1,     # 10%
            'downtime': 300        # 5 minutes
        }
        
        self.notification_config = {
            'email': {
                'enabled': os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true',
                'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'from_email': os.getenv('ALERT_FROM_EMAIL', 'alerts@gurukul.com'),
                'to_emails': os.getenv('ALERT_TO_EMAILS', '').split(',')
            },
            'webhook': {
                'enabled': os.getenv('WEBHOOK_ALERTS_ENABLED', 'false').lower() == 'true',
                'url': os.getenv('ALERT_WEBHOOK_URL', ''),
                'timeout': 10
            }
        }

    async def check_service_health(self, service_name: str, config: Dict) -> Dict:
        """Check health of a single service"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config['timeout'])) as session:
                async with session.get(config['url']) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'service': service_name,
                            'status': 'healthy',
                            'response_time': response_time,
                            'status_code': response.status,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            'service': service_name,
                            'status': 'unhealthy',
                            'response_time': response_time,
                            'status_code': response.status,
                            'error': f'HTTP {response.status}',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
        except asyncio.TimeoutError:
            return {
                'service': service_name,
                'status': 'timeout',
                'response_time': time.time() - start_time,
                'error': 'Request timeout',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'response_time': time.time() - start_time,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def check_all_services(self) -> List[Dict]:
        """Check health of all services"""
        tasks = []
        for service_name, config in self.services.items():
            task = self.check_service_health(service_name, config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

    def collect_system_metrics(self) -> Dict:
        """Collect system-level metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    def update_metrics(self, health_results: List[Dict]):
        """Update internal metrics with health check results"""
        for result in health_results:
            service = result['service']
            
            # Update response times
            if service not in self.metrics['response_times']:
                self.metrics['response_times'][service] = []
            
            self.metrics['response_times'][service].append(result['response_time'])
            
            # Keep only last 100 measurements
            if len(self.metrics['response_times'][service]) > 100:
                self.metrics['response_times'][service] = self.metrics['response_times'][service][-100:]
            
            # Update error counts
            if service not in self.metrics['error_counts']:
                self.metrics['error_counts'][service] = 0
            
            if result['status'] != 'healthy':
                self.metrics['error_counts'][service] += 1
            
            # Update last check time
            self.metrics['last_check'][service] = result['timestamp']

    async def send_alert(self, alert_type: str, message: str, details: Dict = None):
        """Send alert via configured channels"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'critical' if 'down' in message.lower() else 'warning'
        }
        
        # Email alerts
        if self.notification_config['email']['enabled']:
            await self.send_email_alert(alert_data)
        
        # Webhook alerts
        if self.notification_config['webhook']['enabled']:
            await self.send_webhook_alert(alert_data)
        
        logger.warning(f"ALERT: {alert_type} - {message}")

    async def send_email_alert(self, alert_data: Dict):
        """Send email alert"""
        try:
            config = self.notification_config['email']
            
            msg = MimeMultipart()
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = f"Gurukul Alert: {alert_data['type']}"
            
            body = f"""
            Alert Type: {alert_data['type']}
            Severity: {alert_data['severity']}
            Message: {alert_data['message']}
            Timestamp: {alert_data['timestamp']}
            
            Details:
            {json.dumps(alert_data['details'], indent=2)}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    async def send_webhook_alert(self, alert_data: Dict):
        """Send webhook alert"""
        try:
            config = self.notification_config['webhook']
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config['timeout'])) as session:
                async with session.post(config['url'], json=alert_data) as response:
                    if response.status == 200:
                        logger.info("Webhook alert sent successfully")
                    else:
                        logger.error(f"Webhook alert failed: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    def analyze_health_results(self, health_results: List[Dict]) -> List[Dict]:
        """Analyze health results and generate alerts if needed"""
        alerts = []
        
        for result in health_results:
            service = result['service']
            
            # Check if service is down
            if result['status'] != 'healthy':
                alerts.append({
                    'type': 'service_down',
                    'message': f"Service {service} is {result['status']}",
                    'details': result
                })
            
            # Check response time
            if result['response_time'] > self.alert_thresholds['response_time']:
                alerts.append({
                    'type': 'slow_response',
                    'message': f"Service {service} response time is {result['response_time']:.2f}s",
                    'details': result
                })
        
        return alerts

    async def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("Starting health monitoring cycle")
        
        # Check service health
        health_results = await self.check_all_services()
        
        # Collect system metrics
        system_metrics = self.collect_system_metrics()
        
        # Update internal metrics
        self.update_metrics(health_results)
        
        # Analyze results and generate alerts
        alerts = self.analyze_health_results(health_results)
        
        # Send alerts
        for alert in alerts:
            await self.send_alert(alert['type'], alert['message'], alert['details'])
        
        # Log summary
        healthy_count = sum(1 for r in health_results if r['status'] == 'healthy')
        total_count = len(health_results)
        
        logger.info(f"Health check completed: {healthy_count}/{total_count} services healthy")
        
        return {
            'health_results': health_results,
            'system_metrics': system_metrics,
            'alerts': alerts,
            'summary': {
                'healthy_services': healthy_count,
                'total_services': total_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    async def run_continuous_monitoring(self, interval: int = 60):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous health monitoring (interval: {interval}s)")
        
        while True:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                await asyncio.sleep(interval)

async def main():
    """Main function"""
    monitor = HealthMonitor()
    
    # Get monitoring interval from environment
    interval = int(os.getenv('MONITORING_INTERVAL', '60'))
    
    # Run continuous monitoring
    await monitor.run_continuous_monitoring(interval)

if __name__ == "__main__":
    asyncio.run(main())
