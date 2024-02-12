from dataclasses import dataclass
import streamlit as st
from PIL import Image
from funcoes import funcoes
import pandas as pd
# import plotly.express as px
import numpy as np
from engineering_notation import EngNumber
from traducoes import *
# from st_aggrid import AgGrid, GridOptionsBuilder


##################################################
f_fund = 60
w_fund = 2*np.pi*f_fund
R_filtro = 100e-3
##################################################




# Interface do usuário para selecionar idioma
idioma = st.selectbox("Language, 语言, Sprache, Язык, Lingua, Langue, Idioma", ("en", "zh", "de", "it", "es", "ru", "fr", "pt"), index=0)

st.title(traduzir("harmonic_filter_analysis", idioma))
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    traduzir("⚙️ Filtro", idioma),
    traduzir("⚡Transformador", idioma),
    traduzir("💾 Leituras de Corrente", idioma),
    traduzir("📈 Resposta de Frequência", idioma),
    traduzir("📊 Tensão | Corrente | Potência", idioma)
])

with tab1:
    st.markdown("## " + traduzir("Filtro", idioma))
    col1_f, col2_f, col3_f = st.columns(3)
    
    with col3_f:
        imagem_filtroDAX = Image.open('./figs/Filtro_Fotografia.png')
        st.image(imagem_filtroDAX, caption='', width=400)
    
    with col1_f:
        tipo_de_filtro = st.radio(
            traduzir("Tipo de Filtro", idioma),
            (
                traduzir("Filtro Amortecido", idioma),
                traduzir("Filtro Sintonizado", idioma),
                traduzir("Filtro Tipo C", idioma)
            )
        )
        V_fund = 1e3 * st.number_input(
            traduzir("Tensão (kV)", idioma),
            min_value=0.220, max_value=138.0, step=0.5, value=34.5
        )
        Q_reat_fund_filtro = 1e6 * st.number_input(
            traduzir("Potência Reativa (MVAr)", idioma),
            min_value=0.001, max_value=100.0, step=0.001, value=4.0
        )
        h_principal = st.number_input(
            traduzir("Harmonica Principal", idioma),
            min_value=2, max_value=23, step=1, value=5
        )
        dessintonia = 1e-2 * st.number_input(
            traduzir("Dessintonia (%)", idioma),
            min_value=0, max_value=10, step=1, value=2
        )
        Q0 = st.number_input(
            traduzir("Fator de Qualidade do Filtro", idioma),
            min_value=0.1, max_value=140.0, step=0.1, value=50.0
        )

    [XFILTRO_fund, R_filtro, L_filtro, C_filtro, La, Ca] = funcoes.parametros_filtro(tipo_de_filtro, h_principal, dessintonia, Q0, V_fund, Q_reat_fund_filtro, w_fund, idioma)

    with col2_f:
        imagem_tipo_de_filtro = funcoes.selecao_da_imagem(tipo_de_filtro, idioma)
        # as imagens tem fundo branco, cuidar... fiz isso pra não precisar de ifs para ajustar o tamanho das figuras
        # ou seja, os fundos são retângulos de mesmo tamanho.
        st.image(imagem_tipo_de_filtro, caption='', width=250)
    with col2_f:
        funcoes.escrita_RLC_filtro(R_filtro, L_filtro, C_filtro, La, Ca, tipo_de_filtro)
        
with tab2:
    st.markdown("## " + traduzir("Transformador", idioma))
    col1_tr, col2_tr = st.columns(2)
    with col1_tr:
        R_trafo_percentual = 1e-2 * st.number_input(traduzir("Percentual de Resistência (%)", idioma), min_value=0.0,
                                                    max_value=20.0, step=0.5, value=0.12)
        X_trafo_percentual = 1e-2 * st.number_input(traduzir("Percentual de Reatância (%)", idioma), min_value=1.0,
                                                    max_value=20.0, step=0.5, value=6.1)
        S_trafo_fund = 1e6 * st.number_input(traduzir("Potência Nominal (MVA)", idioma), min_value=0.1, max_value=500.0,
                                             value=60.0, step=1.)

        Z_base_trafo = V_fund**2 / S_trafo_fund
        I_base_trafo = S_trafo_fund / (np.sqrt(3) * V_fund)
        Z_traf_fund = Z_base_trafo * (R_trafo_percentual + 1j*X_trafo_percentual)
        st.write("$V_{base} = $",  str(EngNumber(V_fund)), "$\\rm{V}$")
        st.write("$I_{base} = $",  str(EngNumber(I_base_trafo)), "$\\rm{A}$")
        st.write("$Z_{base} = $",  str(EngNumber(Z_base_trafo)),"$\Omega$")
        st.write("$R_{trafo} = $", str(EngNumber(np.real(Z_traf_fund))), "$\Omega$")
        st.write("$L_{trafo} = $", str(EngNumber(np.imag(Z_traf_fund)/w_fund)), "$\\rm{H}$")

    with col2_tr:
        imagem_trafo = Image.open('./figs/Transformador.jpg')
        st.image(imagem_trafo, caption='', width=300)

with tab3:
    st.markdown("## " + traduzir("Conteúdo Harmônico da Corrente de Carga", idioma))
    df_correntes = pd.read_csv("leitura_harmonicos_de_corrente.csv", header=0, dtype=np.float64)
    modulo = df_correntes['Módulo [A]']
    fase = df_correntes['Fase [Graus]']
    nr_correntes_harm = st.selectbox(traduzir("Quantidade de Harmônicas", idioma), (1, 2, 3, 4, 5, 6))
    harm = np.zeros(nr_correntes_harm, dtype=int)
    modu = np.zeros(nr_correntes_harm)
    cols = st.columns(nr_correntes_harm)
    for k in range(nr_correntes_harm):
        ii = k
        with cols[k]:
            harm[k] = st.number_input(traduzir("Harmônica [h]", idioma), min_value=2, max_value=50, value=5, step=1,
                                      key="h_" + str(k))
            modu[k] = st.number_input(traduzir("Corrente [A]", idioma), min_value=0.0, max_value=999.9,
                                      value=100.0 / (k + 1), step=1.1, key="m_" + str(k))

    modulo[harm[:]] = modu[:]
    funcoes.grafico_de_correntes_entrada(df_correntes['Ordem [h]'].to_numpy(), df_correntes['Módulo [A]'].to_numpy(), I_base_trafo, idioma)
          
    
with tab4:
    st.markdown("## " + traduzir("Resposta de Frequência", idioma))
    hh = np.linspace(0.1, 50.1, 5001)
    hh =np.round(hh, 2)
    w = w_fund * hh
    Z_filtro, Z_trafo, Z_equivalente, Z_equivalenteC, X_somenteC, w_ressonancia, La, Ca = \
        funcoes.impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, XFILTRO_fund, \
                            w, Z_traf_fund, hh, La, Ca, idioma)

    funcoes.grafico_modulo_impedancia(hh, Z_filtro, Z_trafo, Z_equivalente, Z_base_trafo, h_principal, idioma)

with tab5:

    i_carga_inteiros = modulo * np.exp(1j*fase)
    I_modulo = df_correntes['Módulo [A]']
    I_modulo_principal = modulo[5]    
    h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros, \
        i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, v_resistor_inteiros, \
        v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, \
        i_Ca_inteiros, v_La_inteiros, v_Ca_inteiros = \
        funcoes.grandezas_inteiras(hh, w, Z_trafo, Z_equivalente, Z_filtro,\
                                   i_carga_inteiros, tipo_de_filtro, \
                                   R_filtro, L_filtro, C_filtro, \
                                   V_fund, La, Ca, idioma)

    tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor = funcoes.tensoes_eficazes_nos_elementos_do_filtro(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros)
    corrente_eficaz_La, corrente_eficaz_Ca, corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor = funcoes.correntes_eficazes_nos_elementos_do_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
    st.markdown("#### " + traduzir("Corrente / Corrente de Base do Transformador", idioma))

    funcoes.grafico_corrente_trafo_e_filtro(h_inteiros, h_principal, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, I_base_trafo, idioma)
    i_nominal_capacitores = Q_reat_fund_filtro / (np.sqrt(3)*V_fund)
    st.markdown("#### " + traduzir("Corrente", idioma))

    funcoes.escritas_correntes_de_fase_pu(tipo_de_filtro, corrente_eficaz_La,
                                          corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor,
                                          i_nominal_capacitores, idioma)
    funcoes.grafico_corrente_elementos_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, i_nominal_capacitores, h_principal, h_inteiros, idioma)
    

    st.markdown("#### " + traduzir("Corrente", idioma))

    V_fund_fase = V_fund / np.sqrt(3)
    funcoes.escritas_tensoes_de_fase_pu(tipo_de_filtro, tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor, V_fund_fase)
    funcoes.grafico_tensao_elementos_filtro(h_principal, h_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, v_barra_inteiros, V_fund_fase, idioma)

    
    st.markdown("#### " + traduzir("Potência nos Elementos do Filtro", idioma))

    p_La_inteiros, p_Ca_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros = funcoes.potencias_inteiras(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
    potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor = funcoes.potencias_eficazes(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
    sobretensao_Angelo = np.sqrt(abs(potencia_eficaz_capacitor)/Q_reat_fund_filtro)
    sobretensao_Angelo_a = np.sqrt(abs(potencia_eficaz_Ca)/Q_reat_fund_filtro)
    funcoes.escritas_potencias_trifasicas(tipo_de_filtro, potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor, Q_reat_fund_filtro, sobretensao_Angelo, sobretensao_Angelo_a)
    funcoes.grafico_potencias_elementos_filtro(h_principal, h_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros, idioma)
    

