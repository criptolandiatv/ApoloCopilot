#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para geração do Blueprint do Plantões App

Este script gera um workbook Excel completo com:
- 18 abas de dados estruturados
- Dashboard executivo com gráficos
- Formatação condicional
- KPIs e métricas

Uso:
    python main.py
    python main.py --output custom_output.xlsx
"""
import argparse
import sys
from config import ensure_directories, get_output_path, OUTPUT_FILENAME
from data_generator import generate_all_data
from chart_generator import generate_all_charts
from excel_exporter import export_to_excel


def print_banner():
    """Imprime banner do aplicativo"""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║         PLANTÕES APP - BLUEPRINT GENERATOR        ║
    ║                                                   ║
    ║     Geração automatizada de documentação de       ║
    ║          produto, KPIs e análises de dados        ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(data_dict, chart_paths, output_file):
    """
    Imprime resumo da execução

    Args:
        data_dict: Dicionário com DataFrames gerados
        chart_paths: Dicionário com caminhos dos gráficos
        output_file: Caminho do arquivo Excel gerado
    """
    print("\n" + "="*60)
    print("📊 RESUMO DA EXECUÇÃO")
    print("="*60)

    print(f"\n✅ Dados gerados:")
    print(f"   • {len(data_dict)} tabelas de dados")
    print(f"   • {len(chart_paths)} gráficos")

    print(f"\n📁 Arquivo gerado:")
    print(f"   {output_file}")

    print(f"\n📈 Principais métricas (último mês):")
    last_month = data_dict['report'].iloc[-1]
    print(f"   • Leads: {int(last_month['Leads'])}")
    print(f"   • Trials: {int(last_month['Trials'])}")
    print(f"   • Pagos: {int(last_month['Pagos'])}")
    print(f"   • MRR: R$ {int(last_month['MRR (R$)']):,}".replace(',', '.'))
    print(f"   • NPS: {int(last_month['NPS'])}")

    print("\n" + "="*60)
    print("✨ Processo concluído com sucesso!")
    print("="*60 + "\n")


def main(output_path=None):
    """
    Função principal

    Args:
        output_path: Caminho personalizado para o arquivo de saída
    """
    try:
        print_banner()

        # Prepara ambiente
        print("🔧 Preparando ambiente...")
        ensure_directories()
        print("   ✓ Diretórios verificados\n")

        # Gera dados
        print("📊 Gerando dados estruturados...")
        data_dict = generate_all_data()
        print(f"   ✓ {len(data_dict)} conjuntos de dados gerados\n")

        # Gera gráficos
        chart_paths = generate_all_charts(data_dict)

        # Exporta para Excel
        output_file = export_to_excel(data_dict, chart_paths, output_path)

        # Imprime resumo
        print_summary(data_dict, chart_paths, output_file)

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera blueprint completo do Plantões App em formato Excel"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Caminho personalizado para o arquivo de saída"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    sys.exit(main(args.output))
