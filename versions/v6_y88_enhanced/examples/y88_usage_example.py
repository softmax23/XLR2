#!/usr/bin/env python3
"""
XLR V6 Y88 Enhanced - Usage Examples

This script demonstrates the powerful Y88 features in V6:
- Y88 auto-detection and analysis
- Y88 template generation
- Y88 optimization recommendations
- Y88 configuration analysis
"""

import sys
import yaml
import json
from pathlib import Path

# Add V6 modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.y88.y88_detector import Y88Detector, Y88InterfaceType
from src.y88.y88_templates import Y88TemplateGenerator, Y88TemplateConfig, Y88TemplateType


def example_y88_detection():
    """Example: Y88 auto-detection on existing template."""
    print("🔍 Example 1: Y88 Auto-Detection")
    print("=" * 50)

    # Sample Y88 configuration
    sample_config = {
        'general_info': {
            'iua': 'NXY88',
            'xlr_folder': 'PFI/Y88_LoanIQ/TEST',
            'phases': ['DEV', 'UAT', 'BENCH', 'PRODUCTION']
        },
        'template_liste_package': {
            'App': {
                'package_build_name': 'LoanIQ_app_7.6.2.1.<version>',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_APP_LOANIQ/',
                'XLD_environment_path': 'Environments/PFI/Y88_LOANIQ/7.6/<ENV>/<ENV>/<XLD_env>/APP/<xld_prefix_env>Y88_APP_<XLD_env>_ENV'
            },
            'Interface_summit': {
                'package_build_name': 'Y88_INTERFACE_SUMMIT_BUILD-V<version>',
                'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/INT/Y88_INTERFACE_SUMMIT/'
            }
        },
        'jenkins': {
            'jenkinsServer': 'Configuration/Custom/Jenkins-Y88',
            'username': 'nxy88_jenkins@company.com'
        }
    }

    # Perform Y88 detection
    detector = Y88Detector()
    detection = detector.detect_y88_environment(sample_config)

    # Display results
    print(f"✅ Y88 Detected: {detection.is_y88}")
    print(f"📊 Confidence: {detection.confidence:.2f}")
    print(f"🎯 Project Type: {detection.project_type.value}")
    print(f"🔧 Detected Interfaces: {[i.value for i in detection.detected_interfaces]}")

    if detection.recommendations:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(detection.recommendations, 1):
            print(f"   {i}. {rec}")

    print(f"\n🔧 Suggested Configurations: {len(detection.suggested_configs)} items")

    # Configuration analysis
    analysis = detector.analyze_y88_completeness(sample_config)
    print(f"\n📈 Completeness Score: {analysis['completeness_score']:.2f}")
    if analysis['missing_components']:
        print(f"⚠️  Missing Components: {analysis['missing_components']}")

    print("\n" + "=" * 50 + "\n")


def example_y88_template_generation():
    """Example: Generate Y88 templates programmatically."""
    print("📦 Example 2: Y88 Template Generation")
    print("=" * 50)

    generator = Y88TemplateGenerator()

    # Example 1: Generate full LoanIQ template
    print("🚀 Generating Y88 LoanIQ Full Template...")

    config = Y88TemplateConfig(
        template_type=Y88TemplateType.LOANIQ_FULL,
        project_name="DEMO_LOANIQ",
        iua="NXY88",
        phases=["DEV", "UAT", "BENCH", "PRODUCTION"],
        interfaces=[
            Y88InterfaceType.SUMMIT,
            Y88InterfaceType.SUMMIT_COF,
            Y88InterfaceType.TOGE,
            Y88InterfaceType.DICTIONNAIRE
        ],
        enable_jenkins=True,
        enable_controlm=True
    )

    template = generator.generate_template(config)

    print(f"✅ Generated template with {len(template)} main sections")
    print(f"📦 Packages: {len(template.get('template_liste_package', {}))}")
    print(f"🔧 Phases: {len(template.get('Phases', {}))}")

    # Export template
    output_file = "generated_y88_full_demo.yaml"
    if generator.export_template(template, output_file):
        print(f"💾 Template exported to: {output_file}")

    # Example 2: Custom template
    print("\n🎨 Generating Custom Y88 Template...")

    custom_template = generator.create_custom_template(
        project_name="CUSTOM_Y88_PROJECT",
        iua="NXY88",
        phases=["DEV", "BENCH", "PRODUCTION"],
        interfaces=["summit", "toge"],
        enable_jenkins=True,
        enable_controlm=False
    )

    custom_output = "generated_y88_custom_demo.yaml"
    if generator.export_template(custom_template, custom_output):
        print(f"💾 Custom template exported to: {custom_output}")

    print("\n" + "=" * 50 + "\n")


def example_predefined_templates():
    """Example: Use predefined Y88 templates."""
    print("🏭 Example 3: Predefined Y88 Templates")
    print("=" * 50)

    generator = Y88TemplateGenerator()
    predefined = generator.get_predefined_templates()

    print(f"📋 Available predefined templates: {len(predefined)}")

    for name, config in predefined.items():
        print(f"\n🎯 {name}:")
        print(f"   • Type: {config.template_type.value}")
        print(f"   • Phases: {len(config.phases)}")
        print(f"   • Interfaces: {len(config.interfaces)}")
        print(f"   • Jenkins: {'✅' if config.enable_jenkins else '❌'}")
        print(f"   • ControlM: {'✅' if config.enable_controlm else '❌'}")

        # Generate and export
        template = generator.generate_template(config)
        output_file = f"predefined_{name}_demo.yaml"

        if generator.export_template(template, output_file):
            print(f"   💾 Exported: {output_file}")

    print("\n" + "=" * 50 + "\n")


def example_y88_package_analysis():
    """Example: Analyze Y88 packages in detail."""
    print("🔍 Example 4: Y88 Package Analysis")
    print("=" * 50)

    detector = Y88Detector()

    # Sample Y88 packages for analysis
    packages = {
        'App': {
            'package_build_name': 'LoanIQ_app_7.6.2.1.<version>',
            'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_APP_LOANIQ_76/',
            'controlm_mode': 'master'
        },
        'Interface_summit': {
            'package_build_name': 'Y88_INTERFACE_SUMMIT_BUILD-V<version>',
            'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/INT/Y88_INTERFACE_SUMMIT/',
            'controlm_mode': 'Independant'
        },
        'Scripts': {
            'package_build_name': 'PKG_SCRIPTS-V7.6-<version>',
            'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/APP/Y88_SCR_LOANIQ/',
            'controlm_mode': 'master'
        },
        'Interface_TOGE': {
            'package_build_name': 'Y88_INTERFACE_TOGE_BUILD-V<version>',
            'XLD_application_path': 'Applications/PFI/Y88_LOANIQ/INT/Y88_INTERFACE_TOGE/',
            'controlm_mode': 'Independant'
        }
    }

    print("📦 Analyzing Y88 packages...")

    for package_name, package_config in packages.items():
        package_info = detector.get_y88_package_info(package_name, package_config)

        print(f"\n🔧 {package_name}:")
        print(f"   • Category: {package_info.category}")
        print(f"   • Interface Type: {package_info.interface_type.value if package_info.interface_type else 'None'}")
        print(f"   • ControlM Mode: {package_info.controlm_mode}")
        print(f"   • XLD Pattern: {package_info.xld_path_pattern}")

    print("\n" + "=" * 50 + "\n")


def example_y88_comprehensive_analysis():
    """Example: Comprehensive Y88 environment analysis."""
    print("📊 Example 5: Comprehensive Y88 Analysis")
    print("=" * 50)

    # Load a real Y88 template for analysis
    try:
        # Try to load the predefined Y88 template
        template_path = Path(__file__).parent.parent / "templates" / "y88_loaniq_full.yaml"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                y88_config = yaml.safe_load(f)

            print(f"📁 Analyzing: {template_path.name}")

            detector = Y88Detector()

            # Perform detection
            detection = detector.detect_y88_environment(y88_config)

            print(f"\n🎯 Detection Results:")
            print(f"   • Y88 Environment: {detection.is_y88}")
            print(f"   • Confidence: {detection.confidence:.2f}")
            print(f"   • Project Type: {detection.project_type.value}")
            print(f"   • Interfaces Found: {len(detection.detected_interfaces)}")

            # Detailed interface analysis
            if detection.detected_interfaces:
                print(f"\n🔧 Detected Interfaces:")
                for interface in detection.detected_interfaces:
                    print(f"   • {interface.value}")

            # Completeness analysis
            completeness = detector.analyze_y88_completeness(y88_config)
            print(f"\n📈 Completeness Analysis:")
            print(f"   • Score: {completeness['completeness_score']:.2f}")
            print(f"   • Missing Components: {completeness['missing_components']}")
            print(f"   • Configuration Gaps: {len(completeness['configuration_gaps'])}")

            if completeness['configuration_gaps']:
                print(f"   • Gaps Details:")
                for gap in completeness['configuration_gaps']:
                    print(f"     - {gap}")

            # Recommendations
            if detection.recommendations:
                print(f"\n💡 Optimization Recommendations:")
                for i, rec in enumerate(detection.recommendations, 1):
                    print(f"   {i}. {rec}")

            # Export detailed report
            report_data = {
                "analysis_timestamp": "2025-01-01T00:00:00Z",
                "detection_results": {
                    "is_y88": detection.is_y88,
                    "confidence": detection.confidence,
                    "project_type": detection.project_type.value,
                    "interfaces": [i.value for i in detection.detected_interfaces]
                },
                "completeness_analysis": completeness,
                "recommendations": detection.recommendations,
                "suggested_configurations": detection.suggested_configs
            }

            report_file = "y88_comprehensive_analysis_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"\n📄 Detailed report exported: {report_file}")

        else:
            print("⚠️  Y88 template not found, using sample data...")
            # Fallback to sample analysis
            example_y88_detection()

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("📝 Falling back to sample analysis...")
        example_y88_detection()

    print("\n" + "=" * 50 + "\n")


def main():
    """Run all Y88 V6 examples."""
    print("🚀 XLR V6 Y88 Enhanced - Usage Examples")
    print("=" * 60)
    print("Demonstrating revolutionary Y88 management capabilities")
    print("=" * 60 + "\n")

    try:
        # Run all examples
        example_y88_detection()
        example_y88_template_generation()
        example_predefined_templates()
        example_y88_package_analysis()
        example_y88_comprehensive_analysis()

        print("🎉 All Y88 V6 examples completed successfully!")
        print("🔍 Check the generated files:")
        print("   • generated_y88_*.yaml - Generated templates")
        print("   • predefined_*.yaml - Predefined templates")
        print("   • y88_comprehensive_analysis_report.json - Analysis report")

        print("\n🚀 Ready to use V6 Y88 Enhanced features!")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())