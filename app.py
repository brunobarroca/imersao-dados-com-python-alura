import streamlit as st
import pandas as pd
import plotly.express as px

# -- Configuração da Página -- #
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salário na Área de Dados",
    page_icon="📊",
    layout="wide"
)

# -- Carregamento dos dados -- #
dados = pd.read_csv("https://raw.githubusercontent.com/brunobarroca/imersao-dados-com-python-alura/refs/heads/main/imersao_dados.csv", sep=";")

# -- Barra Lateral  (Filtros) -- #
st.sidebar.header("🔍 Filtros")

# -- Filtro de Ano -- #
anos_disponiveis = sorted(dados["ano_trabalho"].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# -- Filtro de Nível de Experiência -- #
niveis_experiencias_disponiveis = sorted(dados["nivel_experiencia"].unique())
niveis_experiencias_selecionados = st.sidebar.multiselect("Nível de Experiência", niveis_experiencias_disponiveis, default=niveis_experiencias_disponiveis)

# -- Filtro por Tipo de Contrato -- #
contratos_disponiveis = sorted(dados["tipo_emprego"].unique())
contratos_selecionados = st.sidebar.multiselect("Contrato", contratos_disponiveis, default=contratos_disponiveis)

# -- Filtro por Empresa -- #
tamanhos_empresas_disponiveis = sorted(dados["tamanho_empresa"].unique())
tamanhos_empresas_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_empresas_disponiveis, default=tamanhos_empresas_disponiveis)

# -- Filtragem do DataFrame -- #
# O DataFrame principal é filtrado com base nas seleções feitas na barra lateral
dados_filtrado = dados[
    (dados["ano_trabalho"].isin(anos_selecionados)) &
    (dados["nivel_experiencia"].isin(niveis_experiencias_selecionados)) &
    (dados["tipo_emprego"].isin(contratos_selecionados)) &
    (dados["tamanho_empresa"].isin(tamanhos_empresas_selecionados))
]

# -- Conteúdo Principal -- #
st.title("Dashboard - Análise Salarial na área de Dados")
st.markdown("Explore os salários nos últimos anos na área de Dados. Refine sua exploração com os filtros à esquerda.")

# -- Métricas principais (KPIs) -- #
st.subheader("Principais indicadores (Salário Anual em Dólar)")

if not dados_filtrado.empty:
    salario_medio = dados_filtrado["salario_em_usd"].mean()
    salario_maximo = dados_filtrado["salario_em_usd"].max()
    total_registros = dados_filtrado.shape[0]
    cargo_mais_frequente = dados_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"${total_registros:,}")
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# -- Análises Visuais com Plotly -- #
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not dados_filtrado.empty:
        top_cargos = dados_filtrado.groupby("cargo")["salario_em_usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        graficos_cargos = px.bar(
            top_cargos,
            x="salario_em_usd",
            y="cargo",
            orientation="h",
            title="Top 10 Cargos por Salário Médio",
            labels={"salario_em_usd":"Média Salarial Anual (Dólar)", "cargo": ""}
        )
        graficos_cargos.update_layout(title_x=0.1, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(graficos_cargos, use_container_width=True)
    else:
        st.Warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not dados_filtrado.empty:
        grafico_hist = px.histogram(
            dados_filtrado,
            x="salario_em_usd",
            nbins=30,
            title="Distribuição de Salários Anuais",
            labels={"salario_em_usd":"Faixa Salarial (Dólar)", "count":""}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.Warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not dados_filtrado.empty:
        remoto_contagem = dados_filtrado["taxa_remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["tipo_emprego", "quantidade"]
        grafico_remoto = px.pie(
            remoto_contagem,
            names="tipo_emprego",
            values="quantidade",
            title="Proporção dos tipos de trabalho", 
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo="percent+label")
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.Warning("Nenhum dado para exibir no gráfico de tipos de empregos.")

with col_graf4:
    if not dados_filtrado.empty:
        dados_data_scientist = dados_filtrado[dados_filtrado["cargo"] == "Data Scientist"]
        media_ds_pais = dados_data_scientist.groupby("residencia_iso3")["salario_em_usd"].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
                                       locations="residencia_iso3",
                                       color="salario_em_usd",
                                       color_continuous_scale="rdylgn",
                                       title="Salário Médio de Cientista de Dados por País",
                                       labels={"salario_em_usd":"Salário Médio (USD)", "residencia_iso3":"País"})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.Warning("Nenhum dado para exibir no gráfico de países.")

# -- Tabela Analítica de Dados -- #
st.subheader("Relatório Analítico")
st.dataframe(dados_filtrado)