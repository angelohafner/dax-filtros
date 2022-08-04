import streamlit as st
import numpy as np
import plotly.express as px

from engineering_notation import EngNumber
from PIL import Image
from funcoes import funcoes

h = np.arange(0.1, 25, 0.01)
h = np.round(h, 6)

col1, col2, col3 = st.columns(3)
with col1:
	tipo_de_filtro = st.selectbox("Selecione o tipo de filtro", ("Sintonizado", "Amortecido"))
	imagem = funcoes.selecao_da_imagem(tipo_de_filtro)
	st.image(imagem, caption='', width=200)

with st.sidebar:
	st.subheader("Filtro")
	reativos_ou_capacitancia = st.selectbox("kVAr ou μF?", ("kVAr", "μF"))
	h_principal = st.slider('Maior harmônico h: ', min_value=2, max_value=24, value=5, step=1)
	ih_principal = st.slider('Corrente % neste harmônico: ', min_value=0, max_value=99, value=50, step=1)

	st.subheader("Transformador")
	f_fund_ = st.selectbox("Frequência Fundamental", ("60 Hz", "50 Hz"))
	V_fund_ = st.number_input('Tensão Fundamental em kV', min_value=0.380, max_value=380.0, value=34.5, step=1.0)
	V_fund, f_fund, w_fund, f, w = funcoes.definicoes_iniciais(f_fund_, V_fund_, h)
	R_trafo_percentual = st.number_input('Resistência %: ', min_value=0., max_value=5., value=1., step=1.)
	X_trafo_percentual = st.number_input('Reatância %: ', min_value=2., max_value=20., value=13., step=1.)
	S_trafo_fund = st.number_input('Potência Nominal em MVA: ', min_value=0.1, max_value=500., value=60.0, step=1.)
	S_trafo_fund = 1e6 * S_trafo_fund
	I_trafo_fund, Z_base_trafo, Z_trafo_fund = funcoes.dados_transformador_freq_fundamental(S_trafo_fund, V_fund,
	                                                                                        R_trafo_percentual,
	                                                                                        X_trafo_percentual)
	
with st.sidebar:
	R_filtro, L_filtro, C_filtro = funcoes.fundamentais_filtro(reativos_ou_capacitancia, h_principal, V_fund, w_fund,
	                                                           tipo_de_filtro)

Z_filtro, Z_trafo, Z_equivalente, w_ressonancia, w_min_lactec, ind_max_impedancia = funcoes.impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, w, h, Z_trafo_fund)


with col2:
	st.write("$R:$ ", EngNumber(R_filtro), " Ω")
	st.write("$L:$ ", EngNumber(L_filtro), " H")
	st.write("$C:$ ", EngNumber(C_filtro), " F")
with col3:
	st.write("$Z_{tr1}:$ ", EngNumber(np.real(Z_trafo_fund))," + 𝑗",EngNumber(np.imag(Z_trafo_fund))," Ω")
	st.write("$h_{paralela}:$ ", EngNumber(h[ind_max_impedancia[0][0]]))
	st.write("$h_{serie}:$ ", EngNumber(w_ressonancia / w_fund))


st.subheader("Impedância versus frequência")

funcoes.grafico_impedancia(h, Z_filtro, Z_equivalente, Z_trafo, h_principal, Z_base_trafo)


# col2_i, col3_i, col4_i = st.columns(3)


# st.subheader("Corrente versus frequência")

# h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros = funcoes.grandezas_inteiras(h, w, Z_trafo, Z_equivalente, Z_filtro, Z_base_trafo, h_principal, ih_principal, tipo_de_filtro, R_filtro, L_filtro, C_filtro, V_fund, S_trafo_fund)
# tensao_eficaz_resistor, tensao_eficaz_indutor, tensao_eficaz_capacitor      = funcoes.tensoes_eficazes_nos_elementos_do_filtro(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros)
# corrente_eficaz_resistor, corrente_eficaz_indutor, corrente_eficaz_capacitor = funcoes.correntes_eficazes_nos_elementos_do_filtro(i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)
# potencia_eficaz_resistor, potencia_eficaz_indutor, potencia_eficaz_capacitor = funcoes.potencias_eficazes(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros)
# p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros = funcoes.potencias_inteiras(v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros)

# funcoes.grafico_corrente(h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros)

# st.subheader("Corrente versus frequência nos elementos do filtro")
# funcoes.grafico_corrente_filtro(h_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros, i_trafo_inteiros[1])

# st.subheader("Tensão versus frequência nos elementos do filtro")
# funcoes.grafico_tensao_filtro(h_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros, V_fund)

# st.subheader("Potência versus frequência nos elementos do filtro")
# funcoes.grafico_potencia_filtro(h_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros)


# with col2_i:
#      st.write('$V_C =$', EngNumber(tensao_eficaz_capacitor),' V')
#      st.write('$V_L =$', EngNumber(tensao_eficaz_indutor),' V')
#      st.write('$V_R =$', EngNumber(tensao_eficaz_resistor),' V')
#      st.write('$V_{C1} =$', EngNumber(np.abs(v_capacitor_inteiros[1])),' V')
#      st.write('$V_{L1} =$', EngNumber(np.abs(v_indutor_inteiros[1])),' V')
#      st.write('$V_{R1} =$', EngNumber(np.abs(v_resistor_inteiros[1])),' V')
#      st.write('$V_{Ch} =$', EngNumber(np.abs(v_capacitor_inteiros[h_principal])),' V')
#      st.write('$V_{Lh} =$', EngNumber(np.abs(v_indutor_inteiros[h_principal])),' V')
#      st.write('$V_{Rh} =$', EngNumber(np.abs(v_resistor_inteiros[h_principal])),' V')

# with col3_i:
#      st.write('$I_C =$',    EngNumber(corrente_eficaz_capacitor),               ' A')
#      st.write('$I_L =$',    EngNumber(corrente_eficaz_indutor),                 ' A')
#      st.write('$I_R =$',    EngNumber(corrente_eficaz_resistor),                ' A')
#      st.write('$I_{C1} =$', EngNumber(np.abs(i_filtro_inteiros[1])),            ' A')
#      st.write('$I_{L1} =$', EngNumber(np.abs(i_indutor_inteiros[1])),           ' A')
#      st.write('$I_{R1} =$', EngNumber(np.abs(i_resistor_inteiros[1])),          ' A')
#      st.write('$I_{Ch} =$', EngNumber(np.abs(i_filtro_inteiros[h_principal])),  ' A')
#      st.write('$I_{Lh} =$', EngNumber(np.abs(i_indutor_inteiros[h_principal])), ' A')
#      st.write('$I_{Rh} =$', EngNumber(np.abs(i_resistor_inteiros[h_principal])),' A')


# with col4_i:

#      st.write('$Q_C =$',    EngNumber(np.imag(3*potencia_eficaz_capacitor)),        ' VAr')
#      st.write('$Q_L =$',    EngNumber(np.imag(3*potencia_eficaz_indutor)),          ' VAr')
#      st.write('$P_R =$',    EngNumber(np.real(3*potencia_eficaz_resistor)),         ' W')
#      st.write('$Q_{C1} =$', EngNumber(np.imag(3*p_capacitor_inteiros[1])),          ' VAr')
#      st.write('$Q_{L1} =$', EngNumber(np.imag(3*p_indutor_inteiros[1])),            ' VAr')
#      st.write('$P_{R1} =$', EngNumber(np.real(3*p_resistor_inteiros[1])),           ' W')
#      st.write('$Q_{Ch} =$', EngNumber(np.imag(3*p_capacitor_inteiros[h_principal])),' VAr')
#      st.write('$Q_{Lh} =$', EngNumber(np.imag(3*p_indutor_inteiros[h_principal])),  ' VAr')
#      st.write('$P_{Rh} =$', EngNumber(np.real(3*p_resistor_inteiros[h_principal])), ' W')
