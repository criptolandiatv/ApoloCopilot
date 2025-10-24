#!/usr/bin/env python3
"""
Workflow Analyzer for n8n Templates
Categorizes and evaluates 2060+ n8n workflow templates
"""

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

class WorkflowAnalyzer:
    def __init__(self, workflows_dir: str = "./workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows = []
        self.categories = defaultdict(list)
        self.game_changers = []

    def analyze_all_workflows(self):
        """Analyze all workflow JSON files"""
        print(f"Analyzing workflows in {self.workflows_dir}...")

        json_files = list(self.workflows_dir.rglob("*.json"))
        print(f"Found {len(json_files)} workflow files")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                    analysis = self.analyze_workflow(workflow, json_file)
                    if analysis:
                        self.workflows.append(analysis)
            except Exception as e:
                print(f"Error analyzing {json_file}: {e}")

        return self.workflows

    def analyze_workflow(self, workflow: dict, file_path: Path) -> dict:
        """Analyze individual workflow and extract metadata"""
        try:
            name = workflow.get('name', file_path.stem)
            nodes = workflow.get('nodes', [])
            connections = workflow.get('connections', {})
            tags = workflow.get('tags', [])

            # Extract node types
            node_types = [node.get('type', '') for node in nodes]
            node_names = [node.get('name', '') for node in nodes]

            # Identify integrations/services used
            integrations = set()
            for node in nodes:
                node_type = node.get('type', '')
                if node_type and node_type not in ['n8n-nodes-base.start', 'n8n-nodes-base.set',
                                                     'n8n-nodes-base.if', 'n8n-nodes-base.merge',
                                                     'n8n-nodes-base.noOp', 'n8n-nodes-base.function']:
                    # Extract service name from node type
                    service = node_type.replace('n8n-nodes-base.', '').split('.')[0]
                    integrations.add(service)

            # Determine workflow purpose/category
            category = self.categorize_workflow(nodes, node_types, integrations, name, tags)

            # Calculate complexity score
            complexity = self.calculate_complexity(nodes, connections)

            # Determine if game-changer
            is_game_changer, gc_score, gc_reason = self.evaluate_game_changer(
                nodes, integrations, complexity, name, category
            )

            analysis = {
                'name': name,
                'file_path': str(file_path.relative_to(self.workflows_dir.parent)),
                'category': category,
                'num_nodes': len(nodes),
                'integrations': list(integrations),
                'complexity': complexity,
                'is_game_changer': is_game_changer,
                'gc_score': gc_score,
                'gc_reason': gc_reason,
                'tags': tags,
                'trigger_type': self.identify_trigger(nodes)
            }

            return analysis

        except Exception as e:
            print(f"Error in analyze_workflow: {e}")
            return None

    def categorize_workflow(self, nodes: List, node_types: List,
                           integrations: Set, name: str, tags: List) -> str:
        """Categorize workflow based on its purpose and integrations"""

        name_lower = name.lower()
        integrations_lower = [i.lower() for i in integrations]

        # AI/ML Category
        if any(ai in integrations_lower for ai in ['openai', 'anthropic', 'huggingface',
                                                      'stabilityai', 'cohere', 'pinecone',
                                                      'qdrant', 'weaviate', 'chatgpt']):
            return "AI & Machine Learning"

        # Data Processing & ETL
        if any(db in integrations_lower for db in ['postgres', 'mysql', 'mongodb', 'redis',
                                                     'elasticsearch', 'snowflake', 'bigquery']):
            if any(x in integrations_lower for x in ['googledrive', 'dropbox', 's3', 'airtable']):
                return "Data Pipeline & ETL"

        # CRM & Sales
        if any(crm in integrations_lower for crm in ['hubspot', 'salesforce', 'pipedrive',
                                                       'zoho', 'activecampaign', 'autopilot']):
            return "CRM & Sales Automation"

        # Marketing Automation
        if any(mkt in integrations_lower for mkt in ['mailchimp', 'sendgrid', 'customerio',
                                                       'klaviyo', 'lemlist', 'convertkit']):
            return "Marketing Automation"

        # Communication & Notifications
        if any(comm in integrations_lower for comm in ['slack', 'discord', 'telegram', 'whatsapp',
                                                         'twilio', 'vonage', 'sendgrid', 'gmail']):
            if 'openai' not in integrations_lower:  # AI chatbots go to AI category
                return "Communication & Notifications"

        # Project Management
        if any(pm in integrations_lower for pm in ['asana', 'clickup', 'trello', 'jira',
                                                     'monday', 'notion', 'baserow']):
            return "Project Management"

        # E-commerce
        if any(ecom in integrations_lower for ecom in ['shopify', 'woocommerce', 'stripe',
                                                         'magento', 'prestashop', 'square']):
            return "E-commerce"

        # Content & Media
        if any(media in integrations_lower for media in ['wordpress', 'contentful', 'webflow',
                                                           'ghost', 'medium', 'youtube']):
            return "Content Management & Publishing"

        # Development & DevOps
        if any(dev in integrations_lower for dev in ['github', 'gitlab', 'bitbucket', 'jenkins',
                                                       'docker', 'kubernetes', 'circleci']):
            return "Development & DevOps"

        # Finance & Accounting
        if any(fin in integrations_lower for fin in ['quickbooks', 'xero', 'stripe', 'paypal',
                                                       'chargebee', 'paddle']):
            return "Finance & Accounting"

        # Form Processing
        if any(form in integrations_lower for form in ['typeform', 'jotform', 'googleforms',
                                                         'formstack']):
            return "Form Processing & Data Collection"

        # Document Processing
        if any(doc in integrations_lower for doc in ['pdf', 'docparser', 'mindee',
                                                       'awstextract', 'ocrspace']):
            return "Document Processing & OCR"

        # Social Media
        if any(social in integrations_lower for social in ['twitter', 'facebook', 'instagram',
                                                             'linkedin', 'reddit', 'tiktok']):
            return "Social Media Management"

        # Scheduling & Calendar
        if any(cal in integrations_lower for cal in ['calendly', 'googlecalendar', 'outlook',
                                                       'acuityscheduling', 'cal.com']):
            return "Scheduling & Calendar"

        # Storage & File Management
        if any(storage in integrations_lower for storage in ['googledrive', 'dropbox', 'box',
                                                               'onedrive', 's3', 'awss3']):
            return "Storage & File Management"

        # Analytics & Monitoring
        if any(analytics in integrations_lower for analytics in ['googleanalytics', 'mixpanel',
                                                                   'segment', 'amplitude']):
            return "Analytics & Monitoring"

        # Image & Video Processing
        if any(img in integrations_lower for img in ['bannerbear', 'cloudinary', 'imgbb',
                                                       'awsrekognition', 'stabilityai']):
            return "Image & Video Processing"

        # Webhooks & API Integration
        if 'webhook' in name_lower or 'http' in integrations_lower:
            return "Webhooks & API Integration"

        # Default category
        return "General Automation"

    def calculate_complexity(self, nodes: List, connections: dict) -> int:
        """Calculate workflow complexity score (0-100)"""
        score = 0

        # Base score from node count
        score += min(len(nodes) * 3, 30)

        # Connection complexity
        total_connections = sum(len(v) for v in connections.values())
        score += min(total_connections * 2, 20)

        # Check for advanced nodes
        advanced_nodes = ['function', 'code', 'switch', 'if', 'loop', 'merge', 'split']
        for node in nodes:
            node_type = node.get('type', '').lower()
            if any(adv in node_type for adv in advanced_nodes):
                score += 5

        # Check for error handling
        has_error_handling = any('error' in str(node).lower() for node in nodes)
        if has_error_handling:
            score += 10

        return min(score, 100)

    def evaluate_game_changer(self, nodes: List, integrations: Set,
                              complexity: int, name: str, category: str) -> tuple:
        """
        Evaluate if workflow is a game-changer (>90% certainty required)
        Returns: (is_game_changer, score, reason)
        """
        score = 0
        reasons = []

        # High-value integrations (20 points each)
        premium_integrations = {
            'openai': 20, 'anthropic': 20, 'chatgpt': 20,
            'stripe': 15, 'shopify': 15, 'salesforce': 15,
            'hubspot': 15, 'postgres': 10, 'mongodb': 10,
            'elasticsearch': 10, 'snowflake': 15, 'bigquery': 15,
            'github': 10, 'gitlab': 10
        }

        for integration in integrations:
            integration_lower = integration.lower()
            for premium, points in premium_integrations.items():
                if premium in integration_lower:
                    score += points
                    reasons.append(f"Uses {integration}")

        # Multiple premium integrations combo (bonus)
        if len(integrations) >= 3:
            score += 15
            reasons.append(f"Integrates {len(integrations)} services")

        # Complexity bonus
        if complexity >= 60:
            score += 20
            reasons.append(f"High complexity ({complexity}/100)")
        elif complexity >= 40:
            score += 10

        # AI-powered workflows
        ai_services = ['openai', 'anthropic', 'chatgpt', 'huggingface', 'cohere']
        if any(ai in str(integrations).lower() for ai in ai_services):
            score += 25
            reasons.append("AI-powered automation")

        # Data processing pipelines
        has_database = any(db in str(integrations).lower()
                          for db in ['postgres', 'mysql', 'mongodb', 'redis'])
        has_storage = any(s in str(integrations).lower()
                         for s in ['s3', 'googledrive', 'dropbox'])
        if has_database and has_storage:
            score += 20
            reasons.append("Complete data pipeline")

        # E-commerce workflows
        has_ecommerce = any(e in str(integrations).lower()
                           for e in ['shopify', 'stripe', 'woocommerce'])
        has_marketing = any(m in str(integrations).lower()
                           for m in ['mailchimp', 'sendgrid', 'klaviyo'])
        if has_ecommerce and has_marketing:
            score += 20
            reasons.append("E-commerce + Marketing automation")

        # Advanced features
        advanced_features = ['function', 'code', 'loop', 'switch']
        advanced_count = sum(1 for node in nodes
                           if any(feat in str(node.get('type', '')).lower()
                                 for feat in advanced_features))
        if advanced_count >= 2:
            score += 10
            reasons.append(f"Uses {advanced_count} advanced features")

        # Only mark as game-changer if score >= 90
        is_game_changer = score >= 90
        reason_text = "; ".join(reasons) if reasons else "Standard workflow"

        return is_game_changer, score, reason_text

    def identify_trigger(self, nodes: List) -> str:
        """Identify the trigger type of the workflow"""
        for node in nodes:
            node_type = node.get('type', '').lower()
            if 'webhook' in node_type:
                return 'Webhook'
            elif 'schedule' in node_type or 'cron' in node_type:
                return 'Scheduled'
            elif 'manual' in node_type or 'start' in node_type:
                return 'Manual'
            elif 'trigger' in node_type:
                return 'Event Trigger'
        return 'Unknown'

    def generate_report(self):
        """Generate comprehensive categorization and game-changer report"""

        # Organize by category
        categorized = defaultdict(list)
        for workflow in self.workflows:
            categorized[workflow['category']].append(workflow)

        # Sort categories by workflow count
        sorted_categories = sorted(categorized.items(),
                                  key=lambda x: len(x[1]), reverse=True)

        # Identify game-changers
        game_changers = sorted(
            [w for w in self.workflows if w['is_game_changer']],
            key=lambda x: x['gc_score'],
            reverse=True
        )

        # Generate report
        report = {
            'summary': {
                'total_workflows': len(self.workflows),
                'total_categories': len(categorized),
                'game_changers_count': len(game_changers)
            },
            'categories': {},
            'game_changers': game_changers[:50],  # Top 50
            'top_by_complexity': sorted(self.workflows,
                                       key=lambda x: x['complexity'],
                                       reverse=True)[:30]
        }

        for category, workflows in sorted_categories:
            report['categories'][category] = {
                'count': len(workflows),
                'workflows': sorted(workflows,
                                   key=lambda x: x['complexity'],
                                   reverse=True)[:10]  # Top 10 per category
            }

        return report

def main():
    analyzer = WorkflowAnalyzer()

    print("=" * 80)
    print("N8N WORKFLOW ANALYZER")
    print("=" * 80)

    # Analyze all workflows
    workflows = analyzer.analyze_all_workflows()
    print(f"\nAnalyzed {len(workflows)} workflows successfully!")

    # Generate report
    print("\nGenerating comprehensive report...")
    report = analyzer.generate_report()

    # Save report
    output_file = "workflow_analysis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Workflows: {report['summary']['total_workflows']}")
    print(f"Categories: {report['summary']['total_categories']}")
    print(f"Game-Changers (>90% score): {report['summary']['game_changers_count']}")

    print("\n" + "=" * 80)
    print("CATEGORIES BY SIZE")
    print("=" * 80)
    for i, (category, data) in enumerate(list(report['categories'].items())[:15], 1):
        print(f"{i}. {category}: {data['count']} workflows")

    print("\n" + "=" * 80)
    print("TOP 20 GAME-CHANGERS")
    print("=" * 80)
    for i, gc in enumerate(report['game_changers'][:20], 1):
        print(f"\n{i}. {gc['name']}")
        print(f"   Score: {gc['gc_score']}/100 | Category: {gc['category']}")
        print(f"   Integrations: {', '.join(gc['integrations'][:5])}")
        print(f"   Reason: {gc['gc_reason']}")

if __name__ == "__main__":
    main()
