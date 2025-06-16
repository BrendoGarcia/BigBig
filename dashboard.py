# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
from fpdf import FPDF
import plotly.io as pio
import os
import auth  # seu arquivo auth.py
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap

if "mfa_passed" not in st.session_state or not st.session_state["mfa_passed"]:
    auth.app()
    st.stop()

def salvar_grafico(fig, filename):
    pio.write_image(fig, filename, format='png', width=800, height=500)

def gerar_pdf(df, fig1, fig2, fig3, fig4, fig5, fig6, resumo_texto, tabela_resumo=None):
    # Página 1
    salvar_grafico(fig1, "grafico1.png")
    salvar_grafico(fig2, "grafico2.png")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Evasão Escolar", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, resumo_texto)
    pdf.ln(5)
    pdf.image("grafico1.png", x=10, y=pdf.get_y(), w=180)
    pdf.ln(90)
    pdf.image("grafico2.png", x=10, y=pdf.get_y(), w=180)

    # Página 2 - Fatores
    salvar_grafico(fig3, "grafico3.png")
    salvar_grafico(fig4, "grafico4.png")
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Ranking de Fatores e Correlações", ln=True, align="C")
    pdf.ln(10)
    pdf.image("grafico3.png", x=10, y=30, w=180)
    pdf.ln(90)
    pdf.image("grafico4.png", x=10, y=pdf.get_y(), w=180)

    # Página 3 - Comparativo Redes
    salvar_grafico(fig5, "grafico5.png")
    salvar_grafico(fig6, "grafico6.png")
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comparativo entre Redes", ln=True, align="C")
    pdf.ln(10)
    pdf.image("grafico5.png", x=10, y=30, w=180)
    pdf.ln(90)
    pdf.image("grafico6.png", x=10, y=pdf.get_y(), w=180)

    # Tabela final
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Exemplo de Dados:", ln=True)
    if tabela_resumo is None:
        tabela_resumo = df.head(10)
    for i, row in tabela_resumo.iterrows():
        linha = f"{row['sigla_uf']}, {row['rede']}, IDEB: {row['ideb']:.2f}, NSE: {row['nivel_socioeconomico']:.2f}"
        pdf.cell(200, 10, txt=linha, ln=True)

    pdf.output("relatorio_evasao.pdf")



# Configuração da página
st.set_page_config(
    page_title="Preditor de Evasão Escolar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎓 Preditor de Evasão Escolar no Ensino Médio")
st.markdown("---")

# Carregar dados e modelo
@st.cache_data
def load_data():
    df = pd.read_csv("https://storage.googleapis.com/bigdataatividade/processed_data.csv")
    return df

@st.cache_resource
def load_model():
    model = joblib.load("evasion_model.joblib")
    columns = joblib.load("feature_columns.pkl")
    return model,columns
# Carregar dados
df = load_data()
model, load_columns = load_model()

# Siderbar Admin
if st.session_state["username"] == "Brendo":
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox("Escolha uma página:", 
                               ["Dashboard Principal", "Mapa de Risco", "Ranking de Fatores", 
                                "Comparativo Redes", "Simulador de Cenários","🔒 Painel de Auditoria"])



# Sidebar para navegação
else:
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox("Escolha uma página:", 
                               ["Dashboard Principal", "Mapa de Risco", "Ranking de Fatores", 
                                "Comparativo Redes", "Simulador de Cenários"])

if page == "Dashboard Principal":
    auth.log_action(st.session_state["username"], "Pagina Principal", "Navegando")
    st.header("📊 Dashboard Principal")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_escolas = len(df)
        st.metric("Total de Escolas", f"{total_escolas:,}")
    
    with col2:
        escolas_risco = df[df["alta_evasao"] == 1].shape[0]
        st.metric("Escolas em Risco", f"{escolas_risco:,}")
    
    with col3:
        taxa_media_evasao = df["taxa_evasao_historica"].mean()
        st.metric("Taxa Média de Evasão", f"{taxa_media_evasao:.2f}%")
    
    with col4:
        ideb_medio = df["ideb"].mean()
        st.metric("IDEB Médio", f"{ideb_medio:.2f}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição por Estado")
        fig_uf = px.bar(df.groupby("sigla_uf")["alta_evasao"].sum().reset_index(),
                        x="sigla_uf", y="alta_evasao",
                        title="Escolas em Risco por Estado")
        st.plotly_chart(fig_uf, use_container_width=True)
    
    with col2:
        st.subheader("Distribuição por Rede")
        fig_rede = px.pie(df, names="rede", values="alta_evasao",
                          title="Distribuição de Risco por Rede")
        st.plotly_chart(fig_rede, use_container_width=True)
        # Botão para gerar PDF
    st.markdown("### 📄 Gerar Relatório em PDF")

    if st.button("Gerar Relatório"):
        try:
            escolas_risco = df[df["alta_evasao"] == 1].shape[0]
            total_escolas = df.shape[0]
            perc_risco = (escolas_risco / total_escolas) * 100
            resumo_texto = (
            f"Total de escolas analisadas: {total_escolas:,}.\n"
            f"Número de escolas em risco de evasão: {escolas_risco:,} ({perc_risco:.2f}%).\n"
            "Esses dados refletem a situação atual considerando IDEB, nível socioeconômico, "
            "histórico de evasão e outros fatores analisados pelo modelo preditivo."
            )

            # Gerar os gráficos das outras páginas
            importances = model.feature_importances_
            ranking_df = pd.DataFrame({
            "Fator": load_columns,
            "Importância": importances
            }).sort_values(by="Importância", ascending=False)

            fig_importance = px.bar(
            ranking_df.head(15),
            x="Fator", y="Importância",
            title="Fatores que mais influenciam a evasão escolar",
            labels={"Importância": "Importância (modelo)", "Fator": "Variável"}
            )

            correlations = df[["ideb", "indicador_rendimento", "nivel_socioeconomico", "nota_saeb_media_padronizada", "taxa_evasao_historica", "alta_evasao"]].corr()["alta_evasao"].abs().sort_values(ascending=False)
            fig_corr = px.bar(
            x=correlations.index,
            y=correlations.values,
            title="Correlação com risco de evasão",
            labels={"x": "Fator", "y": "Correlação (abs)"}
            )

            df_rede = df.groupby("rede").agg({
            "alta_evasao": ["sum", "mean"],
            "taxa_evasao_historica": "mean",
            "ideb": "mean",
            "nivel_socioeconomico": "mean",
            "id_escola": "count"
            }).round(2)
            df_rede.columns = ["Escolas_Risco", "Percentual_Risco", "Taxa_Media_Evasao", "IDEB_Medio", "NSE_Medio", "Total_Escolas"]
            df_rede = df_rede.reset_index()

            fig_comp1 = px.bar(df_rede, x="rede", y="Percentual_Risco", title="Percentual de Risco por Rede")
            fig_comp2 = px.bar(df_rede, x="rede", y="IDEB_Medio", title="IDEB Médio por Rede")

            # Chamar PDF com todos os gráficos
            gerar_pdf(df, fig_uf, fig_rede, fig_importance, fig_corr, fig_comp1, fig_comp2, resumo_texto)

            with open("relatorio_evasao.pdf", "rb") as f:
                st.download_button("📥 Baixar PDF", f, file_name="relatorio_evasao.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
    

elif page == "Mapa de Risco":
    auth.log_action(st.session_state["username"], "Mapa de Risco", "Navegando")
    st.header("🗺️ Mapa de Risco de Evasão Escolar")

    # ---- Título do Heatmap ----
    st.subheader("🌡️ Heatmap de Escolas com Alta Probabilidade de Evasão")
    st.markdown("Este mapa mostra a concentração geográfica das escolas com risco elevado de evasão escolar, com base nos dados mais recentes.")

    # Mapa base centrado no Brasil
    m = folium.Map(location=[-15.8, -47.9], zoom_start=4, tiles="CartoDB positron")

    # Escolas com risco (alta_evasao == 1)
    heat_data = df[df["alta_evasao"] == 1][["id_escola_latitude", "id_escola_longitude"]].dropna().values.tolist()

    # Adiciona camada de calor
    HeatMap(heat_data, radius=8, blur=15, min_opacity=0.3).add_to(m)

    # Mostra o mapa no Streamlit
    st_folium(m, width=700, height=500)

    # ---- Tabela complementar (opcional) ----
    st.subheader("📋 Quantidade de Escolas em Risco por Estado")
    df_estado = df.groupby("sigla_uf").agg(
        Escolas_Risco=("alta_evasao", "sum"),
        Total_Escolas=("id_escola", "count")
    ).reset_index()
    df_estado["Percentual_Risco"] = (df_estado["Escolas_Risco"] / df_estado["Total_Escolas"]) * 100
    st.dataframe(df_estado.sort_values("Percentual_Risco", ascending=False))

elif page == "Ranking de Fatores":
    auth.log_action(st.session_state["username"], "Ranking de Fatores", "Navegando")
    st.header("📈 Ranking de Fatores Mais Influentes")
   
    # Importância das features
    importances = model.feature_importances_
    ranking_df = pd.DataFrame({
        "Fator": load_columns,
        "Importância": importances
    }).sort_values(by="Importância", ascending=False)

    # Gráfico
    fig_importance = px.bar(
        ranking_df.head(15),  # mostra os 15 mais importantes
        x="Fator",
        y="Importância",
        title="Fatores que mais influenciam a evasão escolar (segundo o modelo)",
        labels={"Importância": "Importância (modelo)", "Fator": "Variável"}
    )
    st.plotly_chart(fig_importance, use_container_width=True)

    
     # Análise de correlação
    correlations = df[["ideb","indicador_rendimento","nivel_socioeconomico","nota_saeb_media_padronizada", "taxa_evasao_historica", "alta_evasao"]].corr()["alta_evasao"].abs().sort_values(ascending=False)
    
    # Gráfico de barras
    fig_corr = px.bar(
        x=correlations.index,
        y=correlations.values,
        title="Correlação linear dos Fatores com Risco de Evasão",
        labels={"x": "Fatores", "y": "Correlação (Valor Absoluto)"}
    )
    st.plotly_chart(fig_corr, use_container_width=True)

elif page == "Comparativo Redes":
    auth.log_action(st.session_state["username"], "Comparativo Redes", "Navegando")
    st.header("🏫 Comparativo entre Redes (Pública/Privada)")
    
    # Análise por rede
    df_rede = df.groupby("rede").agg({
        "alta_evasao": ["sum", "mean"],
        "taxa_evasao_historica": "mean",
        "ideb": "mean",
        "nivel_socioeconomico": "mean",
        "id_escola": "count"
    }).round(2)
    
    df_rede.columns = ["Escolas_Risco", "Percentual_Risco", "Taxa_Media_Evasao", 
                       "IDEB_Medio", "NSE_Medio", "Total_Escolas"]
    df_rede = df_rede.reset_index()
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_comp1 = px.bar(df_rede, x="rede", y="Percentual_Risco",
                           title="Percentual de Risco por Rede")
        st.plotly_chart(fig_comp1, use_container_width=True)
    
    with col2:
        fig_comp2 = px.bar(df_rede, x="rede", y="IDEB_Medio",
                           title="IDEB Médio por Rede")
        st.plotly_chart(fig_comp2, use_container_width=True)
    
    # Tabela comparativa
    st.subheader("Tabela Comparativa")
    st.dataframe(df_rede)

elif page == "Simulador de Cenários":
    auth.log_action(st.session_state["username"], "Simulador de Cenários", "Navegando")
    st.header("🎯 Simulador de Cenários")
    
    st.markdown("Use os controles abaixo para simular diferentes cenários e ver a predição de risco de evasão:")
    
    # Controles para simulação
    col1, col2 = st.columns(2)
    
    with col1:
        ideb_sim = st.slider("IDEB", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
        nse_sim = st.slider("Nível Socioeconômico", min_value=10.0, max_value=70.0, value=50.0, step=0.1)
        taxa_historica = st.slider("Média de Evasão Historica", min_value=00.1, max_value=100.0, value=20.0, step=00.1)
        inse_quantidade_alunos = st.slider("Quantidade de alunos", min_value=1, max_value=1000, value=100, step=1)
    with col2:
        taxa_aprovacao = st.slider("Taxa de aprovados", min_value=01.0, max_value=100.0, value=10.0, step=01.0)
        nota_saeb_matematica = st.slider("Nota Saeb Matematica", min_value=0, max_value=10, value=7, step=1)
        nota_saeb_lingua_portuguesa = st.slider("Nota Saeb Portugues", min_value=1, max_value=10, value=7, step=1)
        uf_sim = st.selectbox("Estado", df["sigla_uf"].unique())
        rede_sim = st.selectbox("Rede", df["rede"].unique())
    
    # Preparar dados para predição
    # Criar um dataframe com os valores simulados
    # Criar o dataframe com os valores simulados
    sim_data = pd.DataFrame({
        "ideb": [ideb_sim],
        "nivel_socioeconomico": [nse_sim],
        "sigla_uf": [uf_sim],
        "rede": [rede_sim],
        "taxa_evasao_historica": [taxa_historica],
        "taxa_aprovacao" : [taxa_aprovacao],
        "inse_quantidade_alunos" : [inse_quantidade_alunos],
        "nota_saeb_matematica" : [nota_saeb_matematica],
        "nota_saeb_lingua_portuguesa" : [nota_saeb_lingua_portuguesa]
    })

    # Aplicar one-hot encoding
    sim_encoded = pd.get_dummies(sim_data, columns=["sigla_uf", "rede"])

    # Garantir que todas as colunas esperadas estejam presentes
    for col in load_columns:
        if col not in sim_encoded.columns:
            sim_encoded[col] = 0  # ou [0], ambos funcionam

    # Reordenar as colunas
    sim_encoded = sim_encoded[load_columns]

    
    # Fazer predição
    try:
        st.write("Dados simulados:", sim_data)
        st.write("Dados codificados:", sim_encoded)
        st.write("🔥 Colunas ativadas (dummies = 1):", sim_encoded.loc[:, sim_encoded.iloc[0] == 1])
        st.write("Proba completa:", model.predict_proba(sim_encoded))
        st.write("Classe predita:", model.predict(sim_encoded))
        st.write("Probabilidade (raw):", model.predict_proba(sim_encoded))


        probabilidade = model.predict_proba(sim_encoded)[0][1]
        risco = model.predict(sim_encoded)[0]
        
        # Mostrar resultado
        st.subheader("Resultado da Simulação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Probabilidade de Alta Evasão", f"{probabilidade:.2%}")
        
        with col2:
            status = "Alto Risco" if risco == 1 else "Baixo Risco"
            color = "red" if risco == 1 else "green"
            st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
        
        # Gráfico de probabilidade
        fig_prob = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = probabilidade * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Probabilidade de Evasão (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        st.plotly_chart(fig_prob, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro na predição: {str(e)}")

if page == "🔒 Painel de Auditoria":
    auth.log_action(st.session_state["username"], "Painel de Auditoria", "Navegando")
    st.header("📋 Painel de Logs de Auditoria")
    logs = pd.DataFrame(list(auth.db["logs"].find().sort("timestamp", -1)))
    if not logs.empty:
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])
        usuarios = logs["username"].unique().tolist()
        usuario_filtro = st.selectbox("Filtrar por usuário:", ["Todos"] + usuarios)
        if usuario_filtro != "Todos":
            logs = logs[logs["username"] == usuario_filtro]
        logs = logs.sort_values("timestamp", ascending=False)
        st.dataframe(logs[["timestamp", "username", "action", "details"]])
    else:
        st.info("Nenhum log registrado ainda.")

### Apartir daqui não tenho certeza mais de nada pode ser que funcione ou não.

# Rodapé
st.markdown("---")
st.markdown("**Predição de Evasão Escolar** - Sistema desenvolvido para identificar escolas com risco crítico de evasão no ensino médio.")
