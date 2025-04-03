# avarias.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Constants and functions
VALID_CREDENTIALS = {
    "admin": "avarias123",
    "admin": "avarias123"
}

def check_login(username, password, page):
    if page == "avarias":
        return username == "admin" and password == VALID_CREDENTIALS["admin"]
    elif page == "dashboard":
        return username == "admin" and password == VALID_CREDENTIALS["admin"]
    return False

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
                if check_login(username, password, page):
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
folhas = ["Avarias Padaria", "Avarias Salgados", "Avarias Rotisseria"]

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

def app():
    if not login_popup("avarias"):
        return

    st.title("Dashboard de Avarias")
    
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    with st.sidebar:
        st.title("Navegação")
        setor = st.selectbox('Escolha o setor', folhas)
        tipo_periodo = st.selectbox('Escolha o período', ['Geral', 'Mês', 'Semana'])
        
        if st.button("Ir para Dashboard Prevenção"):
            st.session_state.page = "dashboard"
            st.session_state.logged_in_avarias = False
            st.rerun()

    df = carregar_dados(setor)
    if df.empty:
        st.error("Nenhum dado encontrado.")
        return
        
    df = processar_datas(df)

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
        # Fixed the typo: removed 'process.' prefix
        df_all = pd.concat([processar_datas(carregar_dados(folha)).assign(CATEGORIA=folha) for folha in folhas])
        
        # Gráficos para visão geral
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

        top_10_qtd = top_10_por_qtd(df_filtrado)
        if not top_10_qtd.empty:
            fig_qtd = px.bar(top_10_qtd.reset_index(), x='DESCRIÇÃO', y='QTD',
                           title="Top 10 Produtos por Quantidade Perdida")
            st.plotly_chart(fig_qtd)

        top_10_vendas = top_10_por_valor_venda(df_filtrado)
        if not top_10_vendas.empty:
            fig_vendas = px.bar(top_10_vendas.reset_index(), x='DESCRIÇÃO', y='VLR. TOT. VENDA',
                              title="Top 10 Produtos por Valor Total de Venda Perdido")
            st.plotly_chart(fig_vendas)

        top_10_custo = top_10_por_valor_custo(df_filtrado)
        if not top_10_custo.empty:
            fig_custo = px.bar(top_10_custo.reset_index(), x='DESCRIÇÃO', y='VLR. TOT. CUSTO',
                             title="Top 10 Produtos por Valor Total de Custo Perdido")
            st.plotly_chart(fig_custo)

        st.markdown("### Tabela de Avarias Detalhada")
        df_exibicao = df_filtrado[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 
                                 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']].copy()
        for col in ['VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']:
            df_exibicao[f'{col} (R$)'] = df_exibicao[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "R$ 0,00")
        st.dataframe(df_exibicao[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA (R$)', 
                                'VLR. UNIT. CUSTO (R$)', 'VLR. TOT. VENDA (R$)', 'VLR. TOT. CUSTO (R$)']])

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