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




##################################################
f_fund = 60
w_fund = 2*np.pi*f_fund
R_filtro = 100e-3
##################################################


st.title("Análise Filtros Harmônicos")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚙️ Filtro", "🔌Transformador", "💾 Leitura Correntes","📈 Resposta em Frequência", "📊 Tensões | Correntes | Potências"])

with tab1:
    st.markdown("## Filtro")
    col1_f, col2_f, col3_f = st.columns(3)
    
    with col3_f:
        imagem_filtroDAX = Image.open('./figs/Filtro_Fotografia.png')
        st.image(imagem_filtroDAX, caption='', width=400)
    
    with col1_f:
        tipo_de_filtro = st.radio("", ("Sintonizado", "Amortecido"))
        V_fund = 1e3 * st.slider("Tensão em kV", min_value=0.220, max_value=138.0, step=0.01, value=34.5)
        Q_reat_fund_filtro = 1e6 * st.slider("Reativos em MVAr", min_value=5.0, max_value=100.0, step=1.0, value=15.0)
        h_principal = st.slider("Filtro para o harmônico", min_value=2, max_value=23, step=1, value=5)
        dessintonia = 1e-2 * st.slider("Dessintonia em %", min_value=0, max_value=10, step=1, value=2) 
        Q0 = st.slider("Fator de Qualidade", min_value=1, max_value=140, step=1, value=80)
        XFILTRO_fund = V_fund ** 2 / Q_reat_fund_filtro
        h_dessintonia_quadrado = (h_principal * (1 - dessintonia)) ** 2
        XC_sobre_XL = h_dessintonia_quadrado
        XC_fund = V_fund ** 2 / (Q_reat_fund_filtro * (1 - 1 / XC_sobre_XL))
        XL_fund = XC_fund - XFILTRO_fund
        C_filtro = 1 / (w_fund * XC_fund)
        L_filtro = XL_fund / w_fund
        if tipo_de_filtro=="Sintonizado":
            Z0 = np.sqrt(L_filtro / C_filtro)
            R_filtro = Z0 / Q0
        elif tipo_de_filtro=="Amortecido":
            Z0 = np.sqrt(L_filtro / C_filtro)
            R_filtro = Z0 * Q0
        else:
            pass            

    with col2_f:    
        imagem_tipo_de_filtro = funcoes.selecao_da_imagem(tipo_de_filtro)
        st.image(imagem_tipo_de_filtro, caption='', width=300)
    with col2_f:   
        st.write("$\;\;\;\;\;\;\;\;\;\;\;\;R = $", EngNumber(R_filtro), "$\\Omega$")
        st.write("$\;\;\;\;\;\;\;\;\;\;\;\;L = $", EngNumber(L_filtro), "${\\rm{H}}$")
        st.write("$\;\;\;\;\;\;\;\;\;\;\;\;C = $", EngNumber(C_filtro), "${\\rm{H}}$")
        ### Filtro Amortecido ####
        ##########################
with tab2:
    st.markdown("## Transformador")
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

    xxx = df_correntes['h'].to_numpy()
    yyy = df_correntes['modulo'].to_numpy()
    fig_pu =    go.Figure(data=[
                go.Bar(name='Conteúdo Harmônico de Corrente em PU', x=xxx, y=yyy/I_base_trafo),
    ])
    fig_pu.update_layout(
                        title="Conteúdo Harmônico de Corrente em PU",
                        xaxis_title="Harmônico",
                        yaxis_title="Corrente [pu]",
    )

    st.plotly_chart(fig_pu)
    fig_A =    go.Figure(data=[
                go.Bar(name='Conteúdo Harmônico de Corrente em A', x=xxx, y=yyy),
    ])
    
    fig_A.update_layout(
                        title="Conteúdo Harmônico de Corrente em A",
                        xaxis_title="Harmônico",
                        yaxis_title="Corrente [A]",
    )
    st.plotly_chart(fig_A)
          
    
with tab4:
    st.markdown("## Resposta em Frequência")
    hh = np.linspace(0.1, 50.1, 501)
    hh =np.round(hh, 2)
    w = w_fund * hh
    Z_filtro, Z_trafo, Z_equivalente, Z_equivalenteC, X_somenteC, w_ressonancia = funcoes.impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, XFILTRO_fund, w, Z_traf_fund, hh)
    my_array = np.zeros((len(hh),4))
    my_array[:,0] = np.transpose(hh)
    my_array[:,1] = np.transpose(abs(Z_filtro)) / Z_base_trafo
    my_array[:,2] = np.transpose(abs(Z_trafo)) / Z_base_trafo
    my_array[:,3] = np.transpose(abs(Z_equivalente)) / Z_base_trafo
    df = pd.DataFrame(my_array, columns=['hh', 'Filtro', 'Tranformador', 'Equivalente'] )
    fig = px.line(df, x="hh", y=['Filtro', 'Tranformador', 'Equivalente'], title='Impedância versus Frequência',
                    labels={'hh':'Harmônico',"value": "Impedância [pu]","variable": "Impedância [pu]"},)
    fig.update_layout(yaxis_range=[0, 4])
    fig.update_layout(xaxis_range=[0, 3*h_principal])
    st.plotly_chart(fig)
    index_min = np.where(np.abs(Z_filtro) == np.min(np.abs(Z_filtro)))[0]
    st.write(r'Harmônico de mínima impedância do filtro em $h=$', hh[index_min][0])

with tab5:
    modulo = df_correntes['modulo']
    fase = df_correntes['fase']
    i_carga_inteiros = modulo * np.exp(1j*fase)
    I_modulo = df_correntes['modulo']
    I_modulo_principal = modulo[5]    
    h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, v_resistor_inteiros, v_indutor_inteiros,v_capacitor_inteiros = funcoes.grandezas_inteiras(hh, w, Z_trafo, Z_equivalente, Z_filtro, i_carga_inteiros, tipo_de_filtro, R_filtro, L_filtro, C_filtro, V_fund)

    tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor = funcoes.tensoes_eficazes_nos_elementos_do_filtro(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros)
    corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor = funcoes.correntes_eficazes_nos_elementos_do_filtro(i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
    st.markdown("#### Corrente / Corrente Base do Transformador")
    fig = go.Figure(data=[
        go.Bar(name='Transformador',    x=h_inteiros, y=abs(i_trafo_inteiros)/I_base_trafo),
        go.Bar(name='Filtro',           x=h_inteiros, y=abs(i_filtro_inteiros)/I_base_trafo),
        go.Bar(name='Carga',            x=h_inteiros, y=abs(i_carga_inteiros)/I_base_trafo)
    ])
    fig.update_layout(
                        title="Corrente / Corrente Nominal do Transformador",
                        xaxis_title="Harmônico",
                        yaxis_title="Corrente / ["+str(EngNumber(I_base_trafo))+" A]",
    )
    fig.update(layout_xaxis_range = [0,min(3*h_principal,np.max(h_inteiros))])
    st.plotly_chart(fig)

    i_nominal_capacitores = Q_reat_fund_filtro / (np.sqrt(3)*V_fund)
    st.markdown("#### Correntes / Corrente Nominal do Capacitor")
    st.write("$I_R = $", EngNumber((abs(corrente_eficaz_resistor)/i_nominal_capacitores)) , "$\\rm{pu}$"  )
    st.write("$I_L = $", EngNumber((abs(corrente_eficaz_indutor)/i_nominal_capacitores))  , "$\\rm{pu}$"  )
    st.write("$I_C = $", EngNumber((abs(corrente_eficaz_capacitor)/i_nominal_capacitores)), "$\\rm{pu}$"  )

    i_nominal_capacitores = Q_reat_fund_filtro / (np.sqrt(3)*V_fund)

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Resistor',  x=h_inteiros, y=abs(i_resistor_inteiros)/i_nominal_capacitores))
    fig.add_trace(go.Bar(name='Indutor',   x=h_inteiros, y=abs(i_indutor_inteiros)/i_nominal_capacitores))
    fig.add_trace(go.Bar(name='Capacitor', x=h_inteiros, y=abs(i_capacitor_inteiros)/i_nominal_capacitores))

    fig.update_layout(
                        title="Corrente Total / Corrente Nominal Capacitores",
                        xaxis_title="Harmônico",
                        yaxis_title="Corrente / ["+str(EngNumber(i_nominal_capacitores))+" A]",
    )

    fig.update(layout_xaxis_range = [0,min(3*h_principal,np.max(h_inteiros))])
    st.plotly_chart(fig)

    st.markdown("#### Tensão / Tensão de Fase")
    V_fund_fase = V_fund / np.sqrt(3)
    st.write("$V_R = $", EngNumber((abs(tensao_eficaz_resistor)/V_fund_fase)) , "$\\rm{pu}$"  )
    st.write("$V_L = $", EngNumber((abs(tensao_eficaz_indutor)/V_fund_fase))  , "$\\rm{pu}$"  )
    st.write("$V_C = $", EngNumber((abs(tensao_eficaz_capacitor)/V_fund_fase)), "$\\rm{pu}$"  )
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Resistor',  x=h_inteiros, y=abs(v_resistor_inteiros)/V_fund_fase))
    fig.add_trace(go.Bar(name='Indutor',   x=h_inteiros, y=abs(v_indutor_inteiros)/V_fund_fase))
    fig.add_trace(go.Bar(name='Capacitor', x=h_inteiros, y=abs(v_capacitor_inteiros)/V_fund_fase))
    fig.add_trace(go.Bar(name='Geral',     x=h_inteiros, y=abs(v_barra_inteiros)/V_fund_fase))

    fig.update_layout(
                        title="Tensões / Tensão de Fase",
                        xaxis_title="Harmônico",
                        yaxis_title="Tensão / ["+str(EngNumber(V_fund_fase))+" V]",
    )

    fig.update(layout_xaxis_range = [0,min(3*h_principal,np.max(h_inteiros))])
    st.plotly_chart(fig)

    p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros = funcoes.potencias_inteiras(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
    potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor = funcoes.potencias_eficazes(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
    st.markdown("#### Potências nos Elementos do Filtro")
    sobretensao_Angelo = np.sqrt(abs(potencia_eficaz_capacitor)/Q_reat_fund_filtro)
    
    st.write("$P_R = $",                 EngNumber((abs(potencia_eficaz_resistor))) , "$\\rm{W}$"  )
    st.write("$Q_L = $",                 EngNumber((abs(potencia_eficaz_indutor)))  , "$\\rm{VAr}$"  )
    st.write("$Q_C = $",                 EngNumber((abs(potencia_eficaz_capacitor))), "$\\rm{VAr}$"  )
    st.write("$\\dfrac{Q_C}{Q_{C1}} = $", EngNumber((abs(potencia_eficaz_capacitor)/Q_reat_fund_filtro)), "$\\rm{pu}$"  )
    st.write(EngNumber(sobretensao_Angelo))
   
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Resistor [W]',    x=h_inteiros, y=abs(p_resistor_inteiros)))
    fig.add_trace(go.Bar(name='Indutor [VAr]',   x=h_inteiros, y=abs(p_indutor_inteiros)))
    fig.add_trace(go.Bar(name='Capacitor [VAr]', x=h_inteiros, y=abs(p_capacitor_inteiros)))


    fig.update_layout(
                        title="Potências nos Elementos do Filtro",
                        xaxis_title="Harmônico",
                        yaxis_title="Potência [VA]",
    )

    fig.update(layout_xaxis_range = [0,min(3*h_principal,np.max(h_inteiros))])
    st.plotly_chart(fig)


              

p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros = funcoes.potencias_inteiras(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor = funcoes.potencias_eficazes(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
imagem_logoDAX = Image.open('./figs/logo-dax-otimizada.webp')
st.sidebar.image(imagem_logoDAX, caption='', width=100)
st.sidebar.markdown("## Qualidade de Energia")
