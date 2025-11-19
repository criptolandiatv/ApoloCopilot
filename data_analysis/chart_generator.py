# -*- coding: utf-8 -*-
"""
Módulo para geração de gráficos e visualizações
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para servidores
from config import CHART_DPI, get_output_path, CHART1_FILENAME, CHART2_FILENAME


def create_leads_by_channel_chart(channels_df, output_path=None):
    """
    Cria gráfico de barras com Leads por Canal

    Args:
        channels_df: DataFrame com dados dos canais
        output_path: Caminho para salvar o gráfico (opcional)

    Returns:
        str: Caminho do arquivo salvo
    """
    if output_path is None:
        output_path = get_output_path(CHART1_FILENAME)

    plt.figure(figsize=(10, 6))
    plt.bar(channels_df["Canal"], channels_df["Leads"], color='#4A90E2')
    plt.title("Leads por Canal (Amostra)", fontsize=14, fontweight='bold')
    plt.xlabel("Canal", fontsize=12)
    plt.ylabel("Leads", fontsize=12)
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path, dpi=CHART_DPI, bbox_inches='tight')
    plt.close()

    return output_path


def create_conversion_chart(channels_df, output_path=None):
    """
    Cria gráfico de barras com Conversão Lead→Trial por canal

    Args:
        channels_df: DataFrame com dados dos canais
        output_path: Caminho para salvar o gráfico (opcional)

    Returns:
        str: Caminho do arquivo salvo
    """
    if output_path is None:
        output_path = get_output_path(CHART2_FILENAME)

    plt.figure(figsize=(10, 6))
    plt.bar(channels_df["Canal"], channels_df["CVR Lead→Trial %"], color='#50C878')
    plt.title("Conversão Lead→Trial (%)", fontsize=14, fontweight='bold')
    plt.xlabel("Canal", fontsize=12)
    plt.ylabel("CVR (%)", fontsize=12)
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')

    # Adiciona valores no topo das barras
    for i, v in enumerate(channels_df["CVR Lead→Trial %"]):
        plt.text(i, v + 0.5, f"{v}%", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=CHART_DPI, bbox_inches='tight')
    plt.close()

    return output_path


def create_mrr_trend_chart(report_df, output_path=None):
    """
    Cria gráfico de linha mostrando evolução do MRR

    Args:
        report_df: DataFrame com dados do relatório mensal
        output_path: Caminho para salvar o gráfico (opcional)

    Returns:
        str: Caminho do arquivo salvo
    """
    if output_path is None:
        output_path = get_output_path("chart_mrr_trend.png")

    plt.figure(figsize=(10, 6))
    plt.plot(report_df["Mês"], report_df["MRR (R$)"], marker='o',
             linewidth=2, markersize=8, color='#4A90E2')
    plt.title("Evolução do MRR", fontsize=14, fontweight='bold')
    plt.xlabel("Mês", fontsize=12)
    plt.ylabel("MRR (R$)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3, linestyle='--')

    # Formata valores do eixo Y
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {int(x):,}'.replace(',', '.')))

    plt.tight_layout()
    plt.savefig(output_path, dpi=CHART_DPI, bbox_inches='tight')
    plt.close()

    return output_path


def create_funnel_chart(report_df, output_path=None):
    """
    Cria gráfico de funil mostrando conversão Leads → Trials → Pagos

    Args:
        report_df: DataFrame com dados do relatório mensal
        output_path: Caminho para salvar o gráfico (opcional)

    Returns:
        str: Caminho do arquivo salvo
    """
    if output_path is None:
        output_path = get_output_path("chart_funnel.png")

    # Usa dados do último mês
    last_month = report_df.iloc[-1]

    stages = ['Leads', 'Trials', 'Pagos']
    values = [last_month['Leads'], last_month['Trials'], last_month['Pagos']]
    colors = ['#4A90E2', '#50C878', '#FFB347']

    plt.figure(figsize=(10, 6))

    # Cria barras horizontais com larguras decrescentes
    for i, (stage, value, color) in enumerate(zip(stages, values, colors)):
        plt.barh(i, value, color=color, alpha=0.8)
        plt.text(value + 20, i, f'{value}', va='center', fontweight='bold')

    plt.yticks(range(len(stages)), stages)
    plt.xlabel('Quantidade', fontsize=12)
    plt.title(f'Funil de Conversão - {last_month["Mês"]}', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path, dpi=CHART_DPI, bbox_inches='tight')
    plt.close()

    return output_path


def generate_all_charts(data_dict):
    """
    Gera todos os gráficos e retorna dicionário com os caminhos

    Args:
        data_dict: Dicionário com todos os DataFrames gerados

    Returns:
        dict: Dicionário com os caminhos dos gráficos gerados
    """
    charts = {}

    print("Gerando gráficos...")

    charts['leads_by_channel'] = create_leads_by_channel_chart(data_dict['channels'])
    print(f"  ✓ Gráfico de Leads por Canal criado")

    charts['conversion'] = create_conversion_chart(data_dict['channels'])
    print(f"  ✓ Gráfico de Conversão criado")

    charts['mrr_trend'] = create_mrr_trend_chart(data_dict['report'])
    print(f"  ✓ Gráfico de evolução MRR criado")

    charts['funnel'] = create_funnel_chart(data_dict['report'])
    print(f"  ✓ Gráfico de Funil criado")

    print(f"Todos os gráficos foram gerados com sucesso!\n")

    return charts
