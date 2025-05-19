# avarias.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import base64
from datetime import datetime
import io
import tempfile
from fpdf import FPDF
from PIL import Image

# Constants and functions
VALID_CREDENTIALS = {
    "admin": "avarias123",
    "kairo": "avarias123"
}
def check_login(username, password):
    return username in VALID_CREDENTIALS and password == VALID_CREDENTIALS[username]

def login_popup(page="avarias"):
    if f"logged_in_{page}" not in st.session_state:
        st.session_state[f"logged_in_{page}"] = False
    
    if not st.session_state[f"logged_in_{page}"]:
        with st.form(key=f"login_form_{page}"):
            st.write(f"Login para {page.capitalize()}")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if check_login(username, password):
                    st.session_state[f"logged_in_{page}"] = True
                    st.success("Login bem-sucedido!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos")
        return False
    return True

# Carregar dados
file_path = r"./avarias/SISTEMA DE GESTÃO DE AVARIAS PREVENÇÃO - FRAGA MAIA (1).xlsm"
xls = pd.ExcelFile(file_path)
folhas = ["Avarias Padaria", "Avarias Salgados", "Avarias Rotisseria", "Avarias Açougue"]

def carregar_dados(nome_folha):
    try:
        df = pd.read_excel(xls, sheet_name=nome_folha, skiprows=1)
        
        # Ensure numeric columns are properly formatted
        df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce')

        def limpar_coluna_moeda(coluna):
            if isinstance(coluna, pd.Series):
                coluna = coluna.replace({r'R\$ ': '', r',': '.'}, regex=True)
                return pd.to_numeric(coluna, errors='coerce')
            return pd.to_numeric(str(coluna).replace('R$ ', '').replace(',', '.'), errors='coerce')

        # Clean monetary columns
        for col in ['VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']:
            if col in df.columns:
                df[col] = limpar_coluna_moeda(df[col])
            else:
                st.warning(f"Coluna {col} não encontrada nos dados")
                df[col] = 0
                
        # Filter out invalid QTD values
        df = df[(df['QTD'] > 0)].dropna(subset=['QTD'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def processar_datas(df):
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
    df['mês'] = df['DATA'].dt.month
    df['dia'] = df['DATA'].dt.day
    df['ano'] = df['DATA'].dt.year
    df['semana'] = df['DATA'].dt.isocalendar().week
    return df

def filtrar_por_periodo(df, tipo_periodo, valor_periodo, meses):
    if tipo_periodo == 'Mês':
        df = df[df['mês'] == valor_periodo]
    elif tipo_periodo == 'Semana':
        inicio, fim = valor_periodo.split('-')
        inicio = int(inicio.replace('Dia ', ''))
        fim = int(fim)
        df = df[(df['dia'] >= inicio) & (df['dia'] <= fim) & 
                (df['mês'] == meses.index(st.session_state.mes_selecionado) + 1)]
    return df

def top_10_por_qtd(df):
    return df.groupby('DESCRIÇÃO').agg({'QTD': 'sum'}).sort_values(by='QTD', ascending=False).head(10)

def top_10_por_valor_venda(df):
    df['VLR. TOT. VENDA'] = df['QTD'] * df['VLR. UNIT. VENDA']
    return df.groupby('DESCRIÇÃO').agg({'VLR. TOT. VENDA': 'sum'}).sort_values(by='VLR. TOT. VENDA', ascending=False).head(10)

def top_10_por_valor_custo(df):
    df['VLR. TOT. CUSTO'] = df['QTD'] * df['VLR. UNIT. CUSTO']
    return df.groupby('DESCRIÇÃO').agg({'VLR. TOT. CUSTO': 'sum'}).sort_values(by='VLR. TOT. CUSTO', ascending=False).head(10)

def resumo_avarias(df):
    return df.groupby('DESCRIÇÃO').agg({
        'QTD': 'sum',
        'VLR. TOT. VENDA': 'sum',
        'VLR. TOT. CUSTO': 'sum',
        'CÓD. INT.': 'first'
    }).reset_index()

def all_produtos_por_qtd(df):
    # Group all products by quantity and value, descending by quantity
    grouped = df.groupby('DESCRIÇÃO').agg({'QTD': 'sum', 'VLR. TOT. VENDA': 'sum'}).sort_values(by='QTD', ascending=False).reset_index()
    return grouped

def fig_to_base64_png(fig):
    img_bytes = pio.to_image(fig, format="png", width=1000, height=600, scale=2)
    return base64.b64encode(img_bytes).decode("utf-8")

def exportar_pdf(df, titulo="Tabela de Avarias Detalhada"):
    st.warning("Exportação para PDF está desabilitada devido a dependências ausentes no ambiente.")
    return None

def exportar_tudo_pdf(figs_dict, tabelas_dict, titulo="Relatório de Avarias"):
    st.warning("Exportação para PDF está desabilitada devido a dependências ausentes no ambiente.")
    return None

def plotly_fig_to_pdf(fig, pdf_title="grafico_avarias.pdf"):
    # Export Plotly figure to PNG in memory
    img_bytes = pio.to_image(fig, format="png", width=1000, height=600, scale=2)
    # Save PNG to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
        tmp_img.write(img_bytes)
        tmp_img.flush()
        img_path = tmp_img.name

    # Create PDF and add image
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    cover = Image.open(img_path)
    width, height = cover.size
    w, h = float(width * 0.264583), float(height * 0.264583)  # px to mm
    pdf.image(img_path, x=10, y=10, w=min(w, 277), h=min(h, 190))  # A4 landscape max: 297x210mm
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

def app():
    if not login_popup("avarias"):
        return

    st.title("Dashboard de Avarias")
    
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    # Restrição de acesso para o usuário kairo
    usuario_atual = None
    for user in VALID_CREDENTIALS:
        if st.session_state.get(f"logged_in_avarias") and st.session_state.get("logged_in_avarias"):
            if st.session_state.get("login_form_avarias-Usuário", "") == user:
                usuario_atual = user
                break
    # Alternativa: pegar o usuário do último login
    if "login_form_avarias-Usuário" in st.session_state:
        usuario_atual = st.session_state["login_form_avarias-Usuário"]
    elif "login_form_avarias-Usuário" not in st.session_state and "kairo" in st.session_state:
        usuario_atual = "kairo"

    with st.sidebar:
        st.title("Navegação")
        if usuario_atual == "kairo":
            setor = "Avarias Padaria"
            st.markdown("**Usuário restrito: apenas Avarias Padaria**")
        else:
            setor = st.selectbox('Escolha o setor', folhas)
        tipo_periodo = st.selectbox('Escolha o período', ['Geral', 'Mês', 'Semana'])
        
        # Carregar dados para filtro de responsável
        df_temp = carregar_dados(setor)
        responsaveis = []
        if not df_temp.empty and 'RESPONSÁVEL' in df_temp.columns:
            responsaveis = sorted(df_temp['RESPONSÁVEL'].dropna().unique())
            responsavel_filter = st.multiselect("Filtrar por Responsável", responsaveis)
        else:
            responsavel_filter = []

        if usuario_atual != "kairo":
            if st.button("Ir para Dashboard Prevenção"):
                st.session_state.page = "dashboard"
                st.session_state.logged_in_avarias = False
                st.rerun()

    df = carregar_dados(setor)
    if df.empty:
        st.error("Nenhum dado encontrado.")
        return
        
    df = processar_datas(df)

    # Aplicar filtro de responsável, se houver
    if responsavel_filter and 'RESPONSÁVEL' in df.columns:
        df = df[df['RESPONSÁVEL'].isin(responsavel_filter)]

    if tipo_periodo == 'Mês':
        mes_selecionado = st.sidebar.selectbox('Escolha o mês', meses)
        st.session_state.mes_selecionado = mes_selecionado
        valor_periodo = meses.index(mes_selecionado) + 1
        df_filtrado = filtrar_por_periodo(df, tipo_periodo, valor_periodo, meses)
    elif tipo_periodo == 'Semana':
        mes_selecionado = st.sidebar.selectbox('Escolha o mês para as semanas', meses)
        st.session_state.mes_selecionado = mes_selecionado
        semanas = ['Dia 1-7', 'Dia 8-14', 'Dia 15-21', 'Dia 22-31']
        valor_periodo = st.sidebar.selectbox('Escolha a semana', semanas)
        df_filtrado = filtrar_por_periodo(df, tipo_periodo, valor_periodo, meses)
    else:
        df_filtrado = df.copy()
        df_all = pd.concat([processar_datas(carregar_dados(folha)).assign(CATEGORIA=folha) for folha in folhas])
        
        # Gráficos para visão geral
        vendas_por_mes_por_setor = df_all.groupby(['CATEGORIA', 'mês']).agg({'VLR. TOT. VENDA': 'sum'}).reset_index()
        vendas_por_mes_por_setor['mês_nome'] = vendas_por_mes_por_setor['mês'].apply(
            lambda x: meses[int(x) - 1] if pd.notna(x) else 'Desconhecido'
        )
        
        fig_vendas_por_setor = px.line(vendas_por_mes_por_setor, x='mês_nome', y='VLR. TOT. VENDA', color='CATEGORIA')
        fig_vendas_por_setor.update_layout(title="Valor Total de Venda por Mês por Setor")
        st.plotly_chart(fig_vendas_por_setor)
        vendas_por_mes = df.groupby('mês').agg({'VLR. TOT. VENDA': 'sum'}).reset_index()
        vendas_por_mes['mês_nome'] = vendas_por_mes['mês'].apply(
            lambda x: meses[int(x) - 1] if pd.notna(x) else 'Desconhecido'
        )
        vendas_por_mes['Média Móvel (3 meses)'] = vendas_por_mes['VLR. TOT. VENDA'].rolling(window=3, min_periods=1).mean()
        
        fig_vendas = go.Figure()
        fig_vendas.add_trace(go.Scatter(x=vendas_por_mes['mês_nome'], y=vendas_por_mes['VLR. TOT. VENDA'],
                                      mode='lines+markers', name='Valor Real'))
        fig_vendas.add_trace(go.Scatter(x=vendas_por_mes['mês_nome'], y=vendas_por_mes['Média Móvel (3 meses)'],
                                      mode='lines', name='Média Móvel (3 meses)', line=dict(dash='dash')))
        fig_vendas.update_layout(title="Valor Total de Venda por Mês (com Média Móvel)")
        st.plotly_chart(fig_vendas)

        # Padrões Sazonais
        custo_por_semana_ano = df_all.groupby(['ano', 'semana'])['VLR. TOT. CUSTO'].sum().reset_index()
        fig_heatmap = px.density_heatmap(custo_por_semana_ano, x='semana', y='ano', z='VLR. TOT. CUSTO',
                                       title="Padrões Sazonais - Custos por Semana e Ano",
                                       color_continuous_scale="Viridis")
        st.plotly_chart(fig_heatmap)

    if tipo_periodo != 'Geral':
        total_vendas = df_filtrado['VLR. TOT. VENDA'].sum()
        total_custo = df_filtrado['VLR. TOT. CUSTO'].sum()
        st.markdown("### Total de Vendas e Custos")
        st.metric("Total de Vendas", f"R$ {total_vendas:,.2f}")
        st.metric("Total de Custo", f"R$ {total_custo:,.2f}")

        figs_dict = {}
        tabelas_dict = {}

        top_10_qtd = top_10_por_qtd(df_filtrado)
        if not top_10_qtd.empty:
            fig_qtd = px.bar(top_10_qtd.reset_index(), x='DESCRIÇÃO', y='QTD',
                           title="Top 10 Produtos por Quantidade Perdida")
            st.plotly_chart(fig_qtd)
            figs_dict["Top 10 Produtos por Quantidade Perdida"] = fig_qtd
        else:
            figs_dict["Top 10 Produtos por Quantidade Perdida"] = None

        all_produtos = all_produtos_por_qtd(df_filtrado)
        if not all_produtos.empty:
            st.markdown("### Todos os Produtos por Quantidade Perdida (Ordem Decrescente)")
            fig_all = px.bar(
                all_produtos,
                x='DESCRIÇÃO',
                y='QTD',
                title="Todos os Produtos por Quantidade Perdida",
                labels={'DESCRIÇÃO': 'Produto', 'QTD': 'Quantidade Perdida'}
            )
            fig_all.update_traces(
                text=[
                    f"Qtd: {row.QTD:.0f}<br>Valor: R$ {row['VLR. TOT. VENDA']:,.2f}"
                    for _, row in all_produtos.iterrows()
                ],
                textposition='outside'
            )
            fig_all.update_layout(
                xaxis_tickangle=-45,
                margin=dict(b=150),
                height=600
            )
            st.plotly_chart(fig_all, use_container_width=True)
            figs_dict["Todos os Produtos por Quantidade Perdida"] = fig_all

            # PDF download button
            if st.button("Baixar gráfico em PDF"):
                pdf_bytes = plotly_fig_to_pdf(fig_all)
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name="grafico_avarias.pdf",
                    mime="application/pdf"
                )
        else:
            figs_dict["Todos os Produtos por Quantidade Perdida"] = None

        top_10_vendas = top_10_por_valor_venda(df_filtrado)
        if not top_10_vendas.empty:
            fig_vendas = px.bar(top_10_vendas.reset_index(), x='DESCRIÇÃO', y='VLR. TOT. VENDA',
                              title="Top 10 Produtos por Valor Total de Venda Perdido")
            st.plotly_chart(fig_vendas)
            figs_dict["Top 10 Produtos por Valor Total de Venda Perdido"] = fig_vendas
        else:
            figs_dict["Top 10 Produtos por Valor Total de Venda Perdido"] = None

        top_10_custo = top_10_por_valor_custo(df_filtrado)
        if not top_10_custo.empty:
            fig_custo = px.bar(top_10_custo.reset_index(), x='DESCRIÇÃO', y='VLR. TOT. CUSTO',
                             title="Top 10 Produtos por Valor Total de Custo Perdido")
            st.plotly_chart(fig_custo)
            figs_dict["Top 10 Produtos por Valor Total de Custo Perdido"] = fig_custo
        else:
            figs_dict["Top 10 Produtos por Valor Total de Custo Perdido"] = None

        st.markdown("### Tabela de Avarias Detalhada")
        df_exibicao = df_filtrado[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 
                                 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']].copy()
        for col in ['VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']:
            df_exibicao[f'{col} (R$)'] = df_exibicao[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "R$ 0,00")
        st.dataframe(df_exibicao[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA (R$)', 
                                'VLR. UNIT. CUSTO (R$)', 'VLR. TOT. VENDA (R$)', 'VLR. TOT. CUSTO (R$)']])
        tabelas_dict["Tabela de Avarias Detalhada"] = df_exibicao[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA (R$)', 
                                'VLR. UNIT. CUSTO (R$)', 'VLR. TOT. VENDA (R$)', 'VLR. TOT. CUSTO (R$)']]

        # Botão para exportar tudo para PDF
        if st.button("Exportar gráficos e tabelas para PDF"):
            st.warning("Exportação para PDF está desabilitada devido a dependências ausentes no ambiente.")

        st.markdown("### Tabela de Avarias - Resumo")
        df_resumo = resumo_avarias(df_filtrado)
        for col in ['VLR. TOT. VENDA', 'VLR. TOT. CUSTO']:
            df_resumo[f'{col} (R$)'] = df_resumo[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "R$ 0,00")
        st.dataframe(df_resumo[['DESCRIÇÃO', 'QTD', 'CÓD. INT.', 'VLR. TOT. VENDA (R$)', 'VLR. TOT. CUSTO (R$)']])

if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "avarias"
    
    if st.session_state.page == "avarias":
        app()
    elif st.session_state.page == "dashboard":
        from dashboard import app as dashboard_app
        dashboard_app()