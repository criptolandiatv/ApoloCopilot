# -*- coding: utf-8 -*-
"""
Módulo para exportação de dados para Excel com formatação avançada
"""
import pandas as pd
from config import (
    get_output_path, OUTPUT_FILENAME, EXCEL_FORMATS,
    COLUMN_WIDTHS, SHEET_NAMES, CHART_SCALE, get_timestamp
)


class ExcelExporter:
    """Classe para gerenciar exportação de dados para Excel"""

    def __init__(self, output_path=None):
        """
        Inicializa o exportador

        Args:
            output_path: Caminho do arquivo Excel de saída (opcional)
        """
        self.output_path = output_path or get_output_path(OUTPUT_FILENAME)
        self.writer = None
        self.workbook = None
        self.formats = {}

    def __enter__(self):
        """Context manager enter"""
        self.writer = pd.ExcelWriter(self.output_path, engine="xlsxwriter")
        self.workbook = self.writer.book
        self._create_formats()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.writer:
            self.writer.close()

    def _create_formats(self):
        """Cria formatos de célula reutilizáveis"""
        for name, props in EXCEL_FORMATS.items():
            self.formats[name] = self.workbook.add_format(props)

    def write_dataframe(self, df, sheet_name, apply_header_format=True):
        """
        Escreve um DataFrame em uma aba do Excel

        Args:
            df: DataFrame a ser escrito
            sheet_name: Nome da aba
            apply_header_format: Se deve aplicar formatação ao cabeçalho
        """
        df.to_excel(self.writer, index=False, sheet_name=sheet_name)

        worksheet = self.writer.sheets[sheet_name]

        # Aplica formatação ao cabeçalho
        if apply_header_format:
            worksheet.set_row(0, None, self.formats['header'])

        # Define larguras das colunas
        for col_idx, width in COLUMN_WIDTHS.items():
            if col_idx < len(df.columns):
                worksheet.set_column(col_idx, col_idx, width)

    def apply_conditional_formatting(self, sheet_name, col_letter, min_val=0, max_val=10, reverse=False):
        """
        Aplica formatação condicional a uma coluna

        Args:
            sheet_name: Nome da aba
            col_letter: Letra da coluna (ex: 'E')
            min_val: Valor mínimo da escala
            max_val: Valor máximo da escala
            reverse: Se True, inverte as cores (verde para valores baixos)
        """
        worksheet = self.writer.sheets[sheet_name]
        cell_range = f"{col_letter}2:{col_letter}1000"

        if not reverse:
            # Verde para valores altos
            worksheet.conditional_format(cell_range, {
                "type": "3_color_scale",
                "min_value": min_val,
                "mid_value": (min_val + max_val) / 2,
                "max_value": max_val
            })
        else:
            # Verde para valores baixos (útil para fricção)
            worksheet.conditional_format(cell_range, {
                "type": "3_color_scale",
                "min_value": max_val,
                "mid_value": (min_val + max_val) / 2,
                "max_value": min_val,
                "min_color": "#63BE7B",
                "mid_color": "#FFEB84",
                "max_color": "#F8696B"
            })

    def create_dashboard_sheet(self, report_df, chart_paths):
        """
        Cria uma aba de dashboard com KPIs e gráficos

        Args:
            report_df: DataFrame com dados do relatório
            chart_paths: Dicionário com caminhos dos gráficos
        """
        dashboard = self.workbook.add_worksheet(SHEET_NAMES['dashboard'])

        # Título
        dashboard.write_row("A1", [
            "Resumo Executivo – plantoes.app",
            "Gerado em",
            get_timestamp()
        ], self.formats['header'])

        # Cabeçalhos da tabela de KPIs
        dashboard.write_row("A3", ["KPI", "Valor", "Nota"], self.formats['header'])

        # Dados do último mês
        last_month = report_df.iloc[-1]

        # KPIs principais
        kpi_rows = [
            ["Leads (mês atual)", int(last_month["Leads"]), "Aquisição"],
            ["Trials (mês atual)", int(last_month["Trials"]), "Ativação"],
            ["Pagos (mês atual)", int(last_month["Pagos"]), "Receita"],
            ["MRR (mês atual)", f"R$ {int(last_month['MRR (R$)']):,}".replace(",", "."), "Receita"],
            ["NPS (mês atual)", int(last_month["NPS"]), "Satisfação"],
        ]

        # Escreve KPIs
        for i, row in enumerate(kpi_rows):
            dashboard.write_row(3 + i, 0, row)

        # Insere gráficos se disponíveis
        if 'leads_by_channel' in chart_paths:
            dashboard.insert_image("E2", chart_paths['leads_by_channel'],
                                   {"x_scale": CHART_SCALE, "y_scale": CHART_SCALE})

        if 'conversion' in chart_paths:
            dashboard.insert_image("E22", chart_paths['conversion'],
                                   {"x_scale": CHART_SCALE, "y_scale": CHART_SCALE})

        if 'mrr_trend' in chart_paths:
            dashboard.insert_image("O2", chart_paths['mrr_trend'],
                                   {"x_scale": CHART_SCALE, "y_scale": CHART_SCALE})

        if 'funnel' in chart_paths:
            dashboard.insert_image("O22", chart_paths['funnel'],
                                   {"x_scale": CHART_SCALE, "y_scale": CHART_SCALE})

    def export_all_data(self, data_dict, chart_paths=None):
        """
        Exporta todos os dados para o Excel

        Args:
            data_dict: Dicionário com todos os DataFrames
            chart_paths: Dicionário com caminhos dos gráficos (opcional)
        """
        print(f"Exportando dados para {self.output_path}...")

        # Escreve cada DataFrame em sua aba
        sheet_mapping = {
            'vision': SHEET_NAMES['vision'],
            'personas': SHEET_NAMES['personas'],
            'jtbd': SHEET_NAMES['jtbd'],
            'vpc': SHEET_NAMES['vpc'],
            'modules': SHEET_NAMES['modules'],
            'use_cases': SHEET_NAMES['use_cases'],
            'lead_magnets': SHEET_NAMES['lead_magnets'],
            'funnel_events': SHEET_NAMES['funnel_events'],
            'kpis': SHEET_NAMES['kpis'],
            'pricing': SHEET_NAMES['pricing'],
            'automations': SHEET_NAMES['automations'],
            'data_model': SHEET_NAMES['data_model'],
            'compliance': SHEET_NAMES['compliance'],
            'pitch': SHEET_NAMES['pitch'],
            'roadmap': SHEET_NAMES['roadmap'],
            'tests': SHEET_NAMES['tests'],
            'report': SHEET_NAMES['report'],
            'channels': SHEET_NAMES['channels']
        }

        for data_key, sheet_name in sheet_mapping.items():
            if data_key in data_dict:
                self.write_dataframe(data_dict[data_key], sheet_name)
                print(f"  ✓ Aba '{sheet_name}' criada")

        # Aplica formatação condicional
        self._apply_all_conditional_formatting()

        # Cria dashboard
        if chart_paths:
            self.create_dashboard_sheet(data_dict['report'], chart_paths)
            print(f"  ✓ Dashboard criado")

        print(f"\n✅ Arquivo Excel criado com sucesso: {self.output_path}\n")

    def _apply_all_conditional_formatting(self):
        """Aplica toda a formatação condicional necessária"""
        # Personas: Clareza e Fricção
        if SHEET_NAMES['personas'] in self.writer.sheets:
            self.apply_conditional_formatting(SHEET_NAMES['personas'], "E")  # Clareza UX
            self.apply_conditional_formatting(SHEET_NAMES['personas'], "F", reverse=True)  # Fricção

        # Módulos: Clareza e Fricção
        if SHEET_NAMES['modules'] in self.writer.sheets:
            self.apply_conditional_formatting(SHEET_NAMES['modules'], "C")  # Clareza UX
            self.apply_conditional_formatting(SHEET_NAMES['modules'], "D", reverse=True)  # Fricção

        # Lead Magnets: Qualidade
        if SHEET_NAMES['lead_magnets'] in self.writer.sheets:
            self.apply_conditional_formatting(SHEET_NAMES['lead_magnets'], "F")  # Qualidade

        # Use Cases: Clareza
        if SHEET_NAMES['use_cases'] in self.writer.sheets:
            self.apply_conditional_formatting(SHEET_NAMES['use_cases'], "E")  # Clareza


def export_to_excel(data_dict, chart_paths=None, output_path=None):
    """
    Função auxiliar para exportar dados para Excel

    Args:
        data_dict: Dicionário com DataFrames
        chart_paths: Dicionário com caminhos dos gráficos
        output_path: Caminho do arquivo de saída

    Returns:
        str: Caminho do arquivo gerado
    """
    with ExcelExporter(output_path) as exporter:
        exporter.export_all_data(data_dict, chart_paths)

    return exporter.output_path
