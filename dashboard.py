import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import io

VALID_CREDENTIALS = {"admin": "prevencao123"}
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


# Cache the Excel file loading to speed up reruns
@st.cache_resource
def get_xls(file_path):
    return pd.ExcelFile(file_path)

# Carregar dados
file_path = "./sistemageral/SISTEMA GERAL PREVENÇÃO - FRAGA MAIA3 (1).xlsm"
xls = get_xls(file_path)

# Folhas disponíveis
folhas = ["Recuperação de Avarias", "Furtos Recuperados", "Quebra Mês", "Quebra degustação"]

# Ler dados da folha selecionada
@st.cache_data(show_spinner=False)
def carregar_dados(nome_folha):
    # Try to read the sheet, handle missing sheets
    try:
        # For "Quebra Deg", columns may differ
        if nome_folha == "Quebra degustação":
            df = pd.read_excel(xls, sheet_name=nome_folha, skiprows=1)
            # Try to standardize columns if possible
            expected_cols = ['DATA', 'CÓDIGO BARRAS', 'CÓDIGO INTERNO', 'DESCRIÇÃO', 'QTD', 'VLR. UNI.', 'TOTAL']
            df = df.iloc[:, :len(expected_cols)]
            df.columns = expected_cols
        else:
            df = pd.read_excel(xls, sheet_name=nome_folha, skiprows=1, usecols="A:H")
            column_names = ['DATA', 'CÓDIGO BARRAS', 'CÓDIGO INTERNO', 'DESCRIÇÃO', 'QTD', 'VLR. UNI.', 'TOTAL', 'PREV.']
            df.columns = column_names

        # Limpar e pré-processar os dados
        df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce')

        def limpar_coluna_moeda(coluna):
            coluna = coluna.astype(str).str.replace('R\$', '', regex=True).str.strip()
            def processar_valor(valor):
                valor = valor.replace(' ', '')
                if ',' in valor:
                    partes = valor.rsplit(',', 1)
                    inteiro = partes[0].replace('.', '')
                    decimal = partes[1] if len(partes) > 1 else '00'
                    valor = f"{inteiro}.{decimal}"
                else:
                    partes = valor.rsplit('.', 1)
                    if len(partes) > 1:
                        inteiro = partes[0].replace('.', '')
                        decimal = partes[1]
                        valor = f"{inteiro}.{decimal}"
                return pd.to_numeric(valor, errors='coerce')
            return coluna.apply(processar_valor)

        df['VLR. UNI.'] = limpar_coluna_moeda(df['VLR. UNI.'])
        df['TOTAL'] = limpar_coluna_moeda(df['TOTAL'])

        # Remover linhas com quantidades inválidas ou zero
        df = df[(df['QTD'] > 0)].dropna(subset=['QTD', 'TOTAL'])

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da folha '{nome_folha}': {e}")
        return pd.DataFrame()

# Processar datas e períodos
def processar_dates(df):
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
    df['mês'] = df['DATA'].dt.month
    df['dia'] = df['DATA'].dt.day
    return df

# Filtrar por período (Mês, Semana)
def filtrar_por_periodo(df, tipo_periodo, valor_periodo, meses):
    if tipo_periodo == 'Mês':
        df = df[df['mês'] == valor_periodo]
    elif tipo_periodo == 'Semana':
        inicio, fim = valor_periodo.split('-')
        inicio = int(inicio.replace('Dia ', ''))
        fim = int(fim)
        df = df[(df['dia'] >= inicio) & (df['dia'] <= fim) & (df['mês'] == meses.index(st.session_state.mes_selecionado) + 1)]
    return df

# Top 5 prevenções por total recuperado
def top_5_prevencao(df):
    top_5 = df.groupby('PREV.')['TOTAL'].sum().nlargest(5).reset_index()
    return top_5

# Top 5 produtos por valor total
def top_5_por_valor(df):
    top_5 = df.groupby('DESCRIÇÃO')['TOTAL'].sum().nlargest(5).reset_index()
    return top_5

# Top 5 produtos por quantidade
def top_5_por_quantidade(df):
    top_5 = df.groupby('DESCRIÇÃO')['QTD'].sum().nlargest(5).reset_index()
    return top_5

# Resumo de prevenções
def resumo_prevencoes(df):
    resumo = df.groupby('DESCRIÇÃO').agg({
        'QTD': 'sum',
        'TOTAL': 'sum',
        'CÓDIGO INTERNO': 'first'
    }).reset_index()
    return resumo

# Função para formatar valores monetários no formato brasileiro
def formatar_moeda(valor):
    if pd.isna(valor):
        return "R$ 0,00"
    # Converter o valor para string com 2 casas decimais
    valor_str = f"{valor:.2f}"
    # Substituir o ponto decimal por vírgula e adicionar ponto como separador de milhares
    partes = valor_str.split('.')
    inteiro = partes[0]
    decimal = partes[1]
    # Adicionar pontos como separador de milhares
    inteiro_com_pontos = ''
    for i, digito in enumerate(reversed(inteiro)):
        if i > 0 and i % 3 == 0:
            inteiro_com_pontos = '.' + inteiro_com_pontos
        inteiro_com_pontos = digito + inteiro_com_pontos
    return f"R$ {inteiro_com_pontos},{decimal}"

# Função para exportar DataFrame para PDF
def exportar_pdf(df, titulo="Tabela de Prevenções Detalhada"):
    st.warning("Exportação para PDF está desabilitada devido a dependências ausentes no ambiente.")
    return None

# Interface do Streamlit
def app():
    if not login_popup("dashboard"):
        return
    st.title("Dashboard Prevenção 👮🏻‍♂️")
    
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Filtros na barra lateral
    with st.sidebar:
        st.title('👮🏻‍♂️ Dashboard Prevenção')
        setor = st.selectbox('Escolha o setor', folhas)
        tipo_periodo = st.selectbox('Escolha o período', ['Mês', 'Semana'])
        
        if tipo_periodo == 'Mês':
            mes_selecionado = st.selectbox('Escolha o mês', meses)
            st.session_state.mes_selecionado = mes_selecionado
            valor_periodo = meses.index(mes_selecionado) + 1
        else:
            mes_selecionado = st.selectbox('Escolha o mês para as semanas', meses)
            st.session_state.mes_selecionado = mes_selecionado
            semanas = ['Dia 1-7', 'Dia 8-14', 'Dia 15-21', 'Dia 22-31']
            valor_periodo = st.selectbox('Escolha a semana', semanas)
        
        df_temp = carregar_dados(setor)
        # Only show prevention filter if column exists
        if not df_temp.empty and 'PREV.' in df_temp.columns:
            prevention_filter = st.multiselect("Escolha o Prevenção", sorted(df_temp['PREV.'].dropna().unique()))
        else:
            prevention_filter = []

    df = carregar_dados(setor)
    if df.empty:
        st.warning("Nenhum dado encontrado para este setor.")
        return

    df = processar_dates(df)
    df_filtrado = filtrar_por_periodo(df, tipo_periodo, valor_periodo, meses)

    # Aplicar filtro de PREV. se existir
    if prevention_filter and 'PREV.' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['PREV.'].isin(prevention_filter)]

    # Exibir total recuperado
    total_recuperado = df_filtrado['TOTAL'].sum()
    st.markdown("### Total Recuperado")
    st.metric("Total Recuperado", formatar_moeda(total_recuperado))

    # Top 5 Prevenções que mais recuperaram (only if column exists)
    if 'PREV.' in df_filtrado.columns:
        top_5_prev = top_5_prevencao(df_filtrado)
        if not top_5_prev.empty:
            st.markdown("### Top 5 Prevenções que Mais Recuperaram")
            fig_prev = px.bar(
                top_5_prev, x='PREV.', y='TOTAL',
                title="Top 5 Prevenções que Mais Recuperaram",
                labels={'PREV.': 'Prevenção', 'TOTAL': 'Recuperado (R$)'}
            )
            st.plotly_chart(fig_prev)
        else:
            st.markdown("### Nenhum dado disponível para Prevenções")
    else:
        st.info("Coluna 'PREV.' não disponível para este setor.")

    # Top 5 Produtos por Valor
    top_5_valor = top_5_por_valor(df_filtrado)
    if not top_5_valor.empty:
        st.markdown("### Top 5 Produtos (por Valor)")
        fig_valor = px.bar(
            top_5_valor, x='DESCRIÇÃO', y='TOTAL',
            title="Top 5 Produtos por Valor",
            labels={'DESCRIÇÃO': 'Produto', 'TOTAL': 'Valor Total (R$)'}
        )
        st.plotly_chart(fig_valor)
    else:
        st.markdown("### Nenhum dado disponível para Valor")
    
    # Top 5 Produtos por Quantidade
    top_5_qtd = top_5_por_quantidade(df_filtrado)
    if not top_5_qtd.empty:
        st.markdown("### Top 5 Produtos (por Quantidade)")
        fig_qtd = px.bar(
            top_5_qtd, x='DESCRIÇÃO', y='QTD',
            title="Top 5 Produtos por Quantidade",
            labels={'DESCRIÇÃO': 'Produto', 'QTD': 'Quantidade Total'}
        )
        st.plotly_chart(fig_qtd)
    else:
        st.markdown("### Nenhum dado disponível para Quantidade")
    
    # Tabela de dados filtrados
    st.markdown("### Tabela de Prevenções Detalhada")
    # Only show columns that exist
    cols_to_show = ['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNI.', 'TOTAL']
    if 'PREV.' in df_filtrado.columns:
        cols_to_show.append('PREV.')
    df_exibicao = df_filtrado[cols_to_show].copy()
    if 'VLR. UNI.' in df_exibicao.columns:
        df_exibicao['VLR. UNI. (R$)'] = df_exibicao['VLR. UNI.'].apply(formatar_moeda)
    if 'TOTAL' in df_exibicao.columns:
        df_exibicao['TOTAL (R$)'] = df_exibicao['TOTAL'].apply(formatar_moeda)
    show_cols = ['DATA', 'DESCRIÇÃO', 'QTD']
    if 'VLR. UNI. (R$)' in df_exibicao.columns:
        show_cols.append('VLR. UNI. (R$)')
    if 'TOTAL (R$)' in df_exibicao.columns:
        show_cols.append('TOTAL (R$)')
    if 'PREV.' in df_exibicao.columns:
        show_cols.append('PREV.')
    st.dataframe(df_exibicao[show_cols])

    # Botão para exportar para PDF
    if st.button("Exportar tabela detalhada para PDF"):
        st.warning("Exportação para PDF está desabilitada devido a dependências ausentes no ambiente.")
    
    # Tabela de resumo
    st.markdown("### Tabela de Prevenções - Resumo")
    df_resumo = resumo_prevencoes(df_filtrado)
    if 'TOTAL' in df_resumo.columns:
        df_resumo['TOTAL (R$)'] = df_resumo['TOTAL'].apply(formatar_moeda)
    resumo_cols = ['DESCRIÇÃO', 'QTD', 'CÓDIGO INTERNO']
    if 'TOTAL (R$)' in df_resumo.columns:
        resumo_cols.append('TOTAL (R$)')
    st.dataframe(df_resumo[resumo_cols])

if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    if st.session_state.page == "dashboard":
        app()
    elif st.session_state.page == "dashboard":
        from avarias import app as avarias_app
        avarias_app()
