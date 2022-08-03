from dataclasses import dataclass
import streamlit as st
from PIL import Image
from funcoes import funcoes
import pandas as pd
import plotly.express as px
import numpy as np
from engineering_notation import EngNumber
import cmath as cm

##################################################
f_fund = 60
w_fund = 2*np.pi*f_fund
R_filtro = 100e-3
##################################################


st.title("Análise Filtros Harmônicos")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚙️ Filtro", "🔌Transformador", "💾 Correntes Harmônicas","📈 Impedância", "📊 Tensões e Correntes"])

with tab1:
    st.markdown("## Filtro")
    col1_f, col2_f, col3_f = st.columns(3)
    with col2_f:
        h_principal = st.slider("Filtro para o harmônico", min_value=2, max_value=24, step=1, value=5)
        dessintonia = 1e-2 * st.slider("Dessintonia em %", min_value=0, max_value=10, step=1, value=2)    
        imagem_filtroDAX = Image.open('./figs/Filtro_Fotografia.png')
        st.image(imagem_filtroDAX, caption='', width=400)
    with col1_f:
        V_fund = 1e3 * st.slider("Tensão em kV", min_value=0.220, max_value=138.0, step=0.01, value=34.5)
        Q_reat_fund_filtro = 1e6 * st.slider("Reativos em MVAr", min_value=5.0, max_value=100.0, step=1.0, value=15.0)
        
        XFILTRO_fund = V_fund ** 2 / Q_reat_fund_filtro
        h_dessintonia_quadrado = (h_principal * (1 - dessintonia)) ** 2
        XC_sobre_XL = h_dessintonia_quadrado
        XC_fund = V_fund ** 2 / (Q_reat_fund_filtro * (1 - 1 / XC_sobre_XL))
        XL_fund = XC_fund - XFILTRO_fund
        C_filtro = 1 / (w_fund * XC_fund)
        L_filtro = XL_fund / w_fund
        
        tipo_de_filtro = st.radio("", ("Sintonizado", "Amortecido"))
        imagem_tipo_de_filtro = funcoes.selecao_da_imagem(tipo_de_filtro)
        st.image(imagem_tipo_de_filtro, caption='', width=200)

    with col3_f:
        Q0 = st.slider("Fator de Qualidade", min_value=20, max_value=100, step=1, value=80)
        ### Filtro Sintonizado ####
        Z0 = np.sqrt(L_filtro / C_filtro)
        R_filtro = Z0 / Q0

    with col3_f:    
        st.write("$R = $", EngNumber(R_filtro), "$\\Omega$")
        st.write("$L = $", EngNumber(L_filtro), "${\\rm{H}}$")
        st.write("$C = $", EngNumber(C_filtro), "${\\rm{H}}$")
        ### Filtro Amortecido ####
        ##########################
with tab2:
    st.markdown("## Transformador")
    col1_tr, col2_tr = st.columns(2)
    with col1_tr:
        R_trafo_percentual = 1e-2 * st.slider("Reatância %", min_value=0.0, max_value=20.0, step=0.5, value=1.00)
        X_trafo_percentual = 1e-2 * st.slider("Reatância %", min_value=1.0, max_value=20.0, step=0.5, value=13.0)
        S_trafo_fund       = 1e6  * st.slider('Potência Nominal em MVA: ', min_value=0.1, max_value=500., value=60.0, step=1.)
        Z_base_trafo = V_fund**2 / S_trafo_fund
        Z_traf_fund = Z_base_trafo * (R_trafo_percentual + 1j*X_trafo_percentual)
        st.write("$V_{base} = $", EngNumber(V_fund), "$\\rm{V}$")
        st.write("$Z_{base} = $", EngNumber(Z_base_trafo),"$\Omega$")
        st.write("$R_{trafo} = $", EngNumber(np.real(Z_traf_fund)), "$\Omega$")
        st.write("$L_{trafo} = $", EngNumber(np.imag(Z_traf_fund)/w_fund), "$\\rm{H}$")

    with col2_tr:
        imagem_trafo = Image.open('./figs/Transformador.jpg')
        st.image(imagem_trafo, caption='', width=300)

with tab3:
    st.markdown("## Correntes Harmônicas da Carga")	    
    df_correntes = pd.read_excel('leitura_harmonicos_de_corrente.xlsx',sheet_name='Sheet1')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df_correntes = pd.read_excel(uploaded_file)


    # df_correntes = pd.read_excel('leitura_harmonicos_de_corrente.xlsx',sheet_name='Sheet1')    
    grafico_correntes_harm = px.bar(df_correntes, x="h", y="modulo", title='Correntes Harmônicas da Carga', labels={"h": "Harmônico", "modulo": "Corrente [pu]"})
    st.plotly_chart(grafico_correntes_harm)
          
    
with tab4:
    st.markdown("# Resposta em Frequência")
    hh = np.linspace(0.1, 50.1, 501)
    w = w_fund * hh
    tipo_de_filtro = "Sintonizado"
    Z_filtro, Z_trafo, Z_equivalente, Z_equivalenteC, X_somenteC, w_ressonancia = funcoes.impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, XFILTRO_fund, w, Z_traf_fund, hh)
    my_array = np.zeros((len(hh),4))
    my_array[:,0] = np.transpose(hh)
    my_array[:,1] = np.transpose(abs(Z_filtro)) / Z_base_trafo
    my_array[:,2] = np.transpose(abs(Z_trafo)) / Z_base_trafo
    my_array[:,3] = np.transpose(abs(Z_equivalente)) / Z_base_trafo
    df = pd.DataFrame(my_array, columns=['hh', 'Filtro', 'Tranformador', 'Equivalente'] )
    fig = px.line(df, x="hh", y=['Filtro', 'Tranformador', 'Equivalente'], title='Impedância versus Frequência',
                    labels={'hh':'Harmônico',"value": "Impedância [pu]","variable": "Impedância [pu]"},)
    fig.update_layout(yaxis_range=[0,5])
    st.plotly_chart(fig)
    index_min = np.where(np.abs(Z_filtro) == np.min(np.abs(Z_filtro)))[0]
    st.write(r'Harmônico de mínima impedância do filtro em $h=$', hh[index_min][0])

with tab5:
    ih_principal = df_correntes['modulo'][h_principal]
    h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros = funcoes.grandezas_inteiras(hh, w, Z_trafo, Z_equivalente, Z_filtro, Z_base_trafo, h_principal, ih_principal, tipo_de_filtro, R_filtro, L_filtro, C_filtro, V_fund, S_trafo_fund)
              


imagem_logoDAX = Image.open('./figs/logo-dax-otimizada.webp')
st.sidebar.image(imagem_logoDAX, caption='', width=100)
st.sidebar.markdown("## Qualidade de Energia")
