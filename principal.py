from dataclasses import dataclass
import streamlit as st
from PIL import Image
from funcoes import funcoes
import pandas as pd
import plotly.express as px
import numpy as np
from engineering_notation import EngNumber
import cmath as cm
import plotly.graph_objects as go


imagem_logoDAX = Image.open('./figs/logo-dax-otimizada.webp')
st.sidebar.image(imagem_logoDAX, caption='', width=100)

##################################################
f_fund = 60
w_fund = 2*np.pi*f_fund
R_filtro = 100e-3
##################################################


st.title("Análise Filtros Harmônicos")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚙️ Filtro", "⚡Transformador", "💾 Leitura Correntes","📈 Resposta em Frequência", "📊 Tensões | Correntes | Potências"])

with tab1:
    st.markdown("## Filtro")
    col1_f, col2_f, col3_f = st.columns(3)
    
    with col3_f:
        imagem_filtroDAX = Image.open('./figs/Filtro_Fotografia.png')
        st.image(imagem_filtroDAX, caption='', width=400)
    
    with col1_f:
        tipo_de_filtro = st.radio("", ("Tipo C","Sintonizado", "Amortecido"))
        V_fund = 1e3 * st.slider("Tensão em kV", min_value=0.220, max_value=138.0, step=0.01, value=34.5)
        Q_reat_fund_filtro = 1e6 * st.slider("Reativos em MVAr", min_value=0.1, max_value=100.0, step=0.01, value=15.0)
        h_principal = st.slider("Filtro para o harmônico", min_value=2, max_value=23, step=1, value=5)
        dessintonia = 1e-2 * st.slider("Dessintonia em %", min_value=0, max_value=10, step=1, value=2) 
    Q0 = st.slider("Fator de Qualidade", min_value=0.1, max_value=140.0, step=0.1, value=16.0)
    [XFILTRO_fund, R_filtro, L_filtro, C_filtro, La, Ca] = funcoes.parametros_filtro(tipo_de_filtro, h_principal, dessintonia, Q0, V_fund, Q_reat_fund_filtro, w_fund)

    with col2_f:    
        imagem_tipo_de_filtro = funcoes.selecao_da_imagem(tipo_de_filtro)
        st.image(imagem_tipo_de_filtro, caption='', width=300)
        funcoes.texto(tipo_de_filtro)
    with col2_f:   
        funcoes.escrita_RLC_filtro(R_filtro, L_filtro, C_filtro, La, Ca, tipo_de_filtro)
        
with tab2:
    st.markdown("## Transformador")
    st.sidebar.markdown("### Transformador")
    st.sidebar.write('Impedância de curto-circuito.')
    col1_tr, col2_tr = st.columns(2)
    with col1_tr:
        R_trafo_percentual = 1e-2 * st.slider("Resistência %", min_value=0.0, max_value=20.0, step=0.5, value=1.00)
        X_trafo_percentual = 1e-2 * st.slider("Reatância %", min_value=1.0, max_value=20.0, step=0.5, value=13.0)
        S_trafo_fund       = 1e6  * st.slider('Potência Nominal em MVA: ', min_value=0.1, max_value=500., value=60.0, step=1.)
        Z_base_trafo = V_fund**2 / S_trafo_fund
        I_base_trafo = S_trafo_fund / (np.sqrt(3) * V_fund)
        Z_traf_fund = Z_base_trafo * (R_trafo_percentual + 1j*X_trafo_percentual)
        st.write("$V_{base} = $", EngNumber(V_fund), "$\\rm{V}$")
        st.write("$I_{base} = $", EngNumber(V_fund), "$\\rm{A}$")
        st.write("$Z_{base} = $", EngNumber(Z_base_trafo),"$\Omega$")
        st.write("$R_{trafo} = $", EngNumber(np.real(Z_traf_fund)), "$\Omega$")
        st.write("$L_{trafo} = $", EngNumber(np.imag(Z_traf_fund)/w_fund), "$\\rm{H}$")

    with col2_tr:
        imagem_trafo = Image.open('./figs/Transformador.jpg')
        st.image(imagem_trafo, caption='', width=300)

with tab3:
    st.markdown("## Conteúdo Harmônico de Corrente da Carga")	    
    df_correntes = pd.read_excel('leitura_harmonicos_de_corrente.xlsx',sheet_name='Sheet1')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df_correntes = pd.read_excel(uploaded_file)

    df_xlsx = funcoes.to_excel(df_correntes)
    st.download_button(label='📥 Download do Modelo de Arquivo',
                                data=df_xlsx ,
                                file_name= 'df_modelo.xlsx')
 
    funcoes.grafico_de_correntes_entrada(df_correntes['h'].to_numpy(), df_correntes['modulo'].to_numpy(), I_base_trafo)
          
    
with tab4:
    st.markdown("## Resposta em Frequência")
    st.sidebar.markdown("### Resposta em Frequência")
    st.sidebar.write("Impedância do Filtro, Transformador e o Equivalente Trafo∥Filtro com a frequência, inclusive inter-harmônicos.")
    hh = np.linspace(0.1, 50.1, 5001)
    hh =np.round(hh, 2)
    w = w_fund * hh
    Z_filtro, Z_trafo, Z_equivalente, Z_equivalenteC, X_somenteC, w_ressonancia, La, Ca = funcoes.impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, XFILTRO_fund, w, Z_traf_fund, hh, La, Ca)
    funcoes.grafico_modulo_impedancia(hh, Z_filtro, Z_trafo, Z_equivalente, Z_base_trafo, h_principal)

with tab5:
        
    modulo = df_correntes['modulo']
    fase = df_correntes['fase']
    i_carga_inteiros = modulo * np.exp(1j*fase)
    I_modulo = df_correntes['modulo']
    I_modulo_principal = modulo[5]    
    h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, i_Ca_inteiros, v_La_inteiros, v_Ca_inteiros = funcoes.grandezas_inteiras(hh, w, Z_trafo, Z_equivalente, Z_filtro, i_carga_inteiros, tipo_de_filtro, R_filtro, L_filtro, C_filtro, V_fund, La, Ca)

    tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor = funcoes.tensoes_eficazes_nos_elementos_do_filtro(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros)
    corrente_eficaz_La, corrente_eficaz_Ca, corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor = funcoes.correntes_eficazes_nos_elementos_do_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
    st.markdown("#### Corrente / Corrente Base do Transformador")
    
    st.sidebar.markdown("### Tensões | Correntes | Potências")
    st.sidebar.write("Estabelece limites de ordem de corrente, tensão e potência nos elementos, em especial nos capacitores.")

    funcoes.grafico_corrente_trafo_e_filtro(h_inteiros, h_principal, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, I_base_trafo)
    i_nominal_capacitores = Q_reat_fund_filtro / (np.sqrt(3)*V_fund)
    st.markdown("#### Correntes / Corrente Nominal do Capacitor")
    funcoes.escritas_correntes_de_fase_pu(tipo_de_filtro, corrente_eficaz_La, corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor, i_nominal_capacitores)
    funcoes.grafico_corrente_elementos_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, i_nominal_capacitores, h_principal, h_inteiros)
    

    st.markdown("#### Tensão / Tensão de Fase")
    V_fund_fase = V_fund / np.sqrt(3)
    funcoes.escritas_tensoes_de_fase_pu(tipo_de_filtro, tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor, V_fund_fase)
    funcoes.grafico_tensao_elementos_filtro(h_principal, h_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, v_barra_inteiros, V_fund_fase)

    
    st.markdown("#### Potências nos Elementos do Filtro")
    p_La_inteiros, p_Ca_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros = funcoes.potencias_inteiras(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
    potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor = funcoes.potencias_eficazes(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
    sobretensao_Angelo = np.sqrt(abs(potencia_eficaz_capacitor)/Q_reat_fund_filtro)
    sobretensao_Angelo_a = np.sqrt(abs(potencia_eficaz_Ca)/Q_reat_fund_filtro)
    funcoes.escritas_potencias_trifasicas(tipo_de_filtro, potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor, Q_reat_fund_filtro, sobretensao_Angelo, sobretensao_Angelo_a)
    funcoes.grafico_potencias_elementos_filtro(h_principal, h_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros)
    

