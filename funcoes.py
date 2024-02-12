import streamlit as st
import plotly.graph_objects as go
from engineering_notation import EngNumber
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px
import xlsxwriter
from io import BytesIO
from traducoes import *
from dataclasses import dataclass


class funcoes():

    def definicoes_iniciais(ff_fund_, VV_fund_, hh):
        V_fund = 1e3 * VV_fund_
        if ff_fund_ == "60 Hz":
            f_fund = 60
        elif ff_fund_ == "50 Hz":
            f_fund = 50
        else:
            pass
        w_fund = 2 * np.pi * f_fund
        f = f_fund * hh
        w = 2 * np.pi * f
        return [V_fund, f_fund, w_fund, f, w]

    def dados_transformador_freq_fundamental(Snom, V1, Rperc, Xperc):
        I_trafo_fund = Snom / (np.sqrt(3) * V1)
        Z_base_trafo = V1 / np.sqrt(3) / I_trafo_fund
        Z_trafo_fund = 1e-2 * (Rperc + 1j * Xperc) * Z_base_trafo
        return [I_trafo_fund, Z_base_trafo, Z_trafo_fund]

    def fundamentais_filtro(reativos_ou_capacitancia, h_principal, V_fund, w_fund, tipo_de_filtro):
        if reativos_ou_capacitancia == "μF":
            L_filtro = st.number_input('Indutância do filtro em mH', min_value=0.0, max_value=80.0, value=26.31,
                                       step=1.0)
            C_filtro = st.number_input('Capacitância do Filtro em μF', min_value=0.0, max_value=30.0, value=10.70,
                                       step=1.0)
            L_filtro = L_filtro * 1e-3
            C_filtro = C_filtro * 1e-6
        elif reativos_ou_capacitancia == "kVAr":
            dessintonia = st.number_input('Dessintonia %:', min_value=0.0, max_value=5.0, value=2.0, step=0.1)
            Q_reat_fund_filtro = st.number_input('MVAr Capacitivos Fundamental:', min_value=0.0, max_value=100.0,
                                                 value=5.0, step=1.0)
            dessintonia = 1e-2 * dessintonia
            Q_reat_fund_filtro = 1e6 * Q_reat_fund_filtro
            XFILTRO_fund = V_fund ** 2 / Q_reat_fund_filtro
            h_dessintonia_quadrado = (h_principal * (1 - dessintonia)) ** 2
            XC_sobre_XL = h_dessintonia_quadrado
            XC_fund = V_fund ** 2 / (Q_reat_fund_filtro * (1 - 1 / XC_sobre_XL))
            XL_fund = XC_fund - XFILTRO_fund
            C_filtro = 1 / (w_fund * XC_fund)
            L_filtro = XL_fund / w_fund
        else:
            pass
        if tipo_de_filtro == "谐振型过滤器":
            R_filtro = st.number_input('Resistência do filtro em mΩ', min_value=0.0, max_value=1000.0, value=100.,
                                       step=1.0)
            R_filtro = R_filtro * 1e-3
        elif tipo_de_filtro == "阻尼型过滤器":
            R_filtro = st.number_input('Resistência do filtro em Ω', min_value=10.0, max_value=5000.0, value=100.0,
                                       step=100.0)
        else:
            pass

        return [R_filtro, L_filtro, C_filtro]

    def selecao_da_imagem(tipo_de_filtro, idioma):
        if tipo_de_filtro == traduzir("Filtro Sintonizado", idioma):
            imagem = Image.open('./figs/Sintonizado.png')
        elif tipo_de_filtro == traduzir("Filtro Amortecido", idioma):
            imagem = Image.open('./figs/Amortecido.png')
        elif tipo_de_filtro == traduzir("Filtro Tipo C", idioma):
            imagem = Image.open('./figs/Tipo_C.png')
        return imagem

    def filtro_sintonizado(R_filtro, L_filtro, C_filtro, w):
        Zsint = R_filtro + 1j * w * L_filtro + 1 / (1j * w * C_filtro)
        w0 = 1 / np.sqrt(L_filtro * C_filtro)
        return [Zsint, w0]

    def filtro_amortecido(R_filtro, L_filtro, C_filtro, w):
        Zamort = 1 / ((1 / R_filtro) + 1 / (1j * w * L_filtro)) + 1 / (1j * w * C_filtro)
        num = np.sqrt(L_filtro * R_filtro ** 2)
        w0 = R_filtro / np.sqrt(L_filtro * (C_filtro * R_filtro ** 2 - L_filtro))
        return [Zamort, w0]

    def grafico_impedancia(hh, ZZ_filtro, ZZ_equivalente, ZZ_trafo, hh_filtrar, Z_base_trafo):
        indice_fund = np.where(hh == 1)
        X_filtro_fund = np.imag(ZZ_filtro[indice_fund])
        Z_capacitores = -1j * X_filtro_fund / hh
        Z_equivalente_somente_capacitores = 1 / (1 / Z_capacitores + 1 / ZZ_trafo)

        my_array = np.zeros((len(hh), 6), dtype=complex)
        my_array[:, 0] = np.transpose(hh)
        my_array[:, 1] = np.transpose(ZZ_filtro / Z_base_trafo)
        my_array[:, 2] = np.transpose(ZZ_trafo / Z_base_trafo)
        my_array[:, 3] = np.transpose(ZZ_equivalente / Z_base_trafo)
        my_array[:, 4] = np.transpose(Z_capacitores / Z_base_trafo)
        my_array[:, 5] = np.transpose(Z_equivalente_somente_capacitores / Z_base_trafo)
        my_array = np.absolute(my_array)
        df = pd.DataFrame(my_array, columns=['h', 'filtro', 'trafo', 'fi∥tr', 'C', 'C∥tr'])
        fig = px.line(df, x="h", y=['filtro', 'trafo', 'fi∥tr', 'C', 'C∥tr'],
                      labels={"h": "Harmônico",
                              "value": "Impedância [pu]",
                              "variable": "Impedância"}, )
        fig.update_layout(yaxis_range=[-0.1, 2])
        fig.update_layout(xaxis_range=[hh_filtrar - 2, hh_filtrar + 2])
        st.plotly_chart(fig, use_container_width=True)

    def impedancias(tipo_de_filtro, R_filtro, L_filtro, C_filtro, XFILTRO_fund, w, Z_trafo_fund, hh, La, Ca, idioma):
        if tipo_de_filtro == traduzir("Filtro Sintonizado", idioma):
            Z_filtro = R_filtro + 1j * w * L_filtro + 1 / (1j * w * C_filtro)
            w_ressonancia = 1 / np.sqrt(L_filtro * C_filtro)
        elif tipo_de_filtro == traduzir("Filtro Amortecido", idioma):
            Z_filtro = 1 / ((1 / R_filtro) + 1 / (1j * w * L_filtro)) + 1 / (1j * w * C_filtro)
            w_ressonancia = R_filtro / np.sqrt(L_filtro * (C_filtro * R_filtro ** 2 - L_filtro))
        elif tipo_de_filtro == traduzir("Filtro Tipo C", idioma):
            Z_LaCa_serie = 1j * w * La + 1 / (1j * w * Ca)
            Z_LaCa_serie[np.imag(Z_LaCa_serie) == 0] = 1j * 1e-9  # Evitar divisão por zero em cálculo de impedância
            Y_RLCa_paralelo = 1 / Z_LaCa_serie + 1 / R_filtro
            Z_filtro = 1 / Y_RLCa_paralelo + 1 / (1j * w * C_filtro)
            w_ressonancia = R_filtro / np.sqrt(L_filtro * (C_filtro * R_filtro ** 2 - L_filtro))

        Z_trafo = np.real(Z_trafo_fund) + 1j * hh * np.imag(Z_trafo_fund)
        Z_equivalente = 1 / (1 / Z_trafo + 1 / Z_filtro)
        X_somenteC = XFILTRO_fund * hh
        Z_equivalenteC = 1 / (1 / Z_trafo + 1 / (1j * X_somenteC))

        return [Z_filtro, Z_trafo, Z_equivalente, Z_equivalenteC, X_somenteC, w_ressonancia, La, Ca]

    def grandezas_inteiras(hh, w, Z_trafo, Z_equivalente, Z_filtro, i_carga_inteiros, tipo_de_filtro, R_filtro,
                           L_filtro, C_filtro, V_fund, La, Ca, idioma):
        # --- somente os harmônicos inteiros
        temp = np.where(np.mod(hh, 1) == 0)[0]
        indices_h_inteiro = np.zeros(len(temp) + 1, dtype=int)
        indices_h_inteiro[1:len(indices_h_inteiro)] = temp
        h_inteiros = hh[indices_h_inteiro]
        w_inteiros = w[indices_h_inteiro]
        # --- todas as impedâncias inteiras
        Z_trafo_inteiros = Z_trafo[indices_h_inteiro]
        Z_filtro_inteiros = Z_filtro[indices_h_inteiro]
        Z_equivalente_inteiros = Z_equivalente[indices_h_inteiro]
        # --- todas as correntes inteiras da carga ou fonte no caso de gerador
        # --- tensão na barra comum já com o filtro instalado
        v_queda_trafo_paralelo_com_filtro = Z_equivalente_inteiros * i_carga_inteiros
        v_barra_inteiros = v_queda_trafo_paralelo_com_filtro
        v_barra_inteiros[1] = V_fund / (np.sqrt(3))  # - v_queda_trafo_paralelo_com_filtro[1]
        # --- corrente do filtro e do transformador
        i_filtro_inteiros = v_barra_inteiros / Z_filtro_inteiros
        i_trafo_inteiros = i_carga_inteiros - i_filtro_inteiros
        # --- tensões e correntes nos elementos do filtro
        v_capacitor_inteiros = i_filtro_inteiros * 1 / (1j * w_inteiros * C_filtro)
        i_capacitor_inteiros = i_filtro_inteiros
        if tipo_de_filtro == traduzir("Filtro Sintonizado", idioma):
            v_resistor_inteiros = i_filtro_inteiros * R_filtro
            v_indutor_inteiros = i_filtro_inteiros * 1j * w_inteiros * L_filtro
            i_indutor_inteiros = i_filtro_inteiros
            i_resistor_inteiros = i_filtro_inteiros


        elif tipo_de_filtro == traduzir("Filtro Amortecido", idioma):
            z_paralelo_RL_inteiros = 1 / (1 / R_filtro + 1 / (1j * w_inteiros * L_filtro))
            v_paralelo_RL_inteiros = i_filtro_inteiros * z_paralelo_RL_inteiros
            i_resistor_inteiros = v_paralelo_RL_inteiros / R_filtro
            i_indutor_inteiros = v_paralelo_RL_inteiros / (1j * w_inteiros * L_filtro)
            v_indutor_inteiros = v_paralelo_RL_inteiros
            v_resistor_inteiros = v_paralelo_RL_inteiros


        elif tipo_de_filtro == traduzir("Filtro Tipo C", idioma):
            z_paralelo_RL_inteiros = 1 / (1 / R_filtro + 1 / (1j * w_inteiros * L_filtro))
            v_paralelo_RL_inteiros = i_filtro_inteiros * z_paralelo_RL_inteiros
            i_resistor_inteiros = v_paralelo_RL_inteiros / R_filtro
            i_indutor_inteiros = v_paralelo_RL_inteiros / (1j * w_inteiros * L_filtro)
            v_indutor_inteiros = v_paralelo_RL_inteiros
            v_resistor_inteiros = v_paralelo_RL_inteiros
            i_La_inteiros = i_indutor_inteiros
            v_La_inteiros = 1j * w_inteiros * La * i_La_inteiros
            i_Ca_inteiros = i_indutor_inteiros
            v_Ca_inteiros = 1 / (1j * w_inteiros * Ca) * i_La_inteiros
        # se não for tipo C não será últil, porém o código ficou mais otimizado assim
        i_La_inteiros = i_indutor_inteiros
        v_La_inteiros = 1j * w_inteiros * La * i_La_inteiros
        i_Ca_inteiros = i_indutor_inteiros
        v_Ca_inteiros = 0*i_La_inteiros

        return [h_inteiros, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros, v_barra_inteiros,
                i_resistor_inteiros, i_indutor_inteiros, i_capacitor_inteiros,
                v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros,
                i_La_inteiros, i_Ca_inteiros, v_La_inteiros, v_Ca_inteiros]

    def tensoes_eficazes_nos_elementos_do_filtro(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros,
                                                 v_capacitor_inteiros):
        temp = np.abs(v_indutor_inteiros)
        tensao_eficaz_indutor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(v_capacitor_inteiros)
        tensao_eficaz_capacitor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(v_resistor_inteiros)
        tensao_eficaz_resistor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(v_La_inteiros)
        tensao_eficaz_La = np.sqrt(np.dot(temp, temp))
        temp = np.abs(v_Ca_inteiros)
        tensao_eficaz_Ca = np.sqrt(np.dot(temp, temp))
        return [tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor, tensao_eficaz_indutor,
                tensao_eficaz_capacitor]

    def correntes_eficazes_nos_elementos_do_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros,
                                                   i_indutor_inteiros, i_capacitor_inteiros):
        temp = np.abs(i_indutor_inteiros)
        corrente_eficaz_indutor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(i_capacitor_inteiros)
        corrente_eficaz_capacitor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(i_resistor_inteiros)
        corrente_eficaz_resistor = np.sqrt(np.dot(temp, temp))
        temp = np.abs(i_La_inteiros)
        corrente_eficaz_La = np.sqrt(np.dot(temp, temp))
        temp = np.abs(i_Ca_inteiros)
        corrente_eficaz_Ca = np.sqrt(np.dot(temp, temp))
        return [corrente_eficaz_La, corrente_eficaz_Ca, corrente_eficaz_resistor, corrente_eficaz_indutor,
                corrente_eficaz_capacitor]

    def potencias_eficazes(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros,
                           i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros, i_filtro_inteiros):
        potencia_eficaz_resistor = 3 * np.dot(v_resistor_inteiros, np.conjugate(i_resistor_inteiros))
        potencia_eficaz_indutor = 3 * np.dot(v_indutor_inteiros, np.conjugate(i_indutor_inteiros))
        potencia_eficaz_capacitor = 3 * np.dot(v_capacitor_inteiros, np.conjugate(i_filtro_inteiros))
        potencia_eficaz_La = 3 * np.dot(v_La_inteiros, np.conjugate(i_La_inteiros))
        potencia_eficaz_Ca = 3 * np.dot(v_Ca_inteiros, np.conjugate(i_Ca_inteiros))
        return [potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor, potencia_eficaz_indutor,
                potencia_eficaz_capacitor]

    def potencias_inteiras(v_La_inteiros, v_Ca_inteiros, v_resistor_inteiros, v_indutor_inteiros, v_capacitor_inteiros,
                           i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros,
                           i_indutor_inteiros, i_capacitor_inteiros):
        p_capacitor_inteiros = 3 * v_capacitor_inteiros * np.conjugate(i_capacitor_inteiros)
        p_indutor_inteiros = 3 * v_indutor_inteiros * np.conjugate(i_indutor_inteiros)
        p_resistor_inteiros = 3 * v_resistor_inteiros * np.conjugate(i_resistor_inteiros)
        p_La_inteiros = 3 * v_La_inteiros * np.conjugate(i_La_inteiros)
        p_Ca_inteiros = 3 * v_Ca_inteiros * np.conjugate(i_Ca_inteiros)
        return [p_La_inteiros, p_Ca_inteiros, p_resistor_inteiros, p_indutor_inteiros, p_capacitor_inteiros]

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'})
        worksheet.set_column('A:A', None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    def parametros_filtro(tipo_de_filtro, h_principal, dessintonia, Q0, V_fund, Q_reat_fund_filtro, w_fund, idioma):
        XFILTRO_fund = V_fund ** 2 / Q_reat_fund_filtro
        XC_sobre_XL = (h_principal * (1 - dessintonia)) ** 2
        XC_fund = V_fund ** 2 / (Q_reat_fund_filtro * (1 - 1 / XC_sobre_XL))
        XL_fund = XC_fund - XFILTRO_fund
        C_filtro = 1 / (w_fund * XC_fund)
        L_filtro = XL_fund / w_fund
        La = 0
        Ca = 0
        if tipo_de_filtro == traduzir("Filtro Sintonizado", idioma):
            Z0 = np.sqrt(L_filtro / C_filtro)
            R_filtro = Z0 / Q0
        elif tipo_de_filtro == traduzir("Filtro Amortecido", idioma):
            Z0 = np.sqrt(L_filtro / C_filtro)
            R_filtro = Z0 * Q0
        elif tipo_de_filtro == traduzir("Filtro Tipo C", idioma):  ###############################################
            Z0 = np.sqrt(L_filtro / C_filtro)
            R_filtro = Z0 * Q0
            w0 = (h_principal * (1 - dessintonia)) * w_fund
            La = w0 * L_filtro / (w0 - w_fund ** 2 / w0)
            Ca = 1 / ((w_fund) ** 2 * La)
        return [XFILTRO_fund, R_filtro, L_filtro, C_filtro, La, Ca]

    # def texto(tipo_de_filtro):
    #     if tipo_de_filtro == "Sintonizado":
    #         st.sidebar.markdown("### Filtro Sintonizado")
    #         st.sidebar.write("Tipo mais econômico e frequentemente suficiente para a aplicação.")
    #         st.sidebar.write("Fornece um caminho de baixa impedância para uma corrente harmônica específica.")
    #     elif tipo_de_filtro == "Amortecido":
    #         st.sidebar.markdown("### Filtro Amortecido")
    #         st.sidebar.write("Trata-se de um filtro passa-altas.")
    #         st.sidebar.write("Geralmente usado em harmônicos superiores ao 11°.")
    #         st.sidebar.write(
    #             "Para filtrar o 5° ou o 7° harmônicos com amortecimento, sugere-se a utilização do Filtro tipo C.")
    #     elif tipo_de_filtro == "Tipo C":
    #         st.sidebar.markdown("### Filtro Tipo C")
    #         st.sidebar.write(
    #             "Muito parecido ao Filtro Amortecido, contudo a adição de $C_a$ elimina perdas em $R$ na frequência fundamental.")

    def escrita_RLC_filtro(R_filtro, L_filtro, C_filtro, La, Ca, tipo_de_filtro):
        st.write("$\;\;\;\;\;\;\;\;\;\;\;\;R   = $", str(EngNumber(R_filtro)), "$\\Omega$")
        if tipo_de_filtro == "谐振型过滤器" or tipo_de_filtro == "阻尼型过滤器":
            st.write("$\;\;\;\;\;\;\;\;\;\;\;\;L   = $", str(EngNumber(L_filtro)), "${\\rm{H}}$")
            st.write("$\;\;\;\;\;\;\;\;\;\;\;\;C   = $", str(EngNumber(C_filtro)), "${\\rm{F}}$")
        elif tipo_de_filtro == "C型过滤器":
            st.write("$\;\;\;\;\;\;\;\;\;\;\;\;L_a = $", str(EngNumber(La)), "${\\rm{H}}$")
            st.write("$\;\;\;\;\;\;\;\;\;\;\;\;C_a = $", str(EngNumber(Ca)), "${\\rm{F}}$")
            st.write("$\;\;\;\;\;\;\;\;\;\;\;\;C   = $", str(EngNumber(C_filtro)), "${\\rm{F}}$")

    def grafico_corrente_trafo_e_filtro(h_inteiros, h_principal, i_trafo_inteiros, i_filtro_inteiros, i_carga_inteiros,
                                        I_base_trafo, idioma):
        fig = go.Figure(data=[
            go.Bar(name=traduzir('Transformador', idioma), x=h_inteiros, y=abs(i_trafo_inteiros) / I_base_trafo),
            go.Bar(name=traduzir('Filtro', idioma), x=h_inteiros, y=abs(i_filtro_inteiros) / I_base_trafo),
            go.Bar(name=traduzir('Carga', idioma), x=h_inteiros, y=abs(i_carga_inteiros) / I_base_trafo)
        ])

        fig.update_layout(
            title=traduzir("Corrente / Corrente Nominal do Transformador", idioma),
            xaxis_title=traduzir("Harmônicas", idioma),
            yaxis_title=traduzir("Corrente", idioma)+" / [{} A]".format(EngNumber(I_base_trafo)),
        )

        fig.update(layout_xaxis_range=[0, min(3 * h_principal, np.max(h_inteiros))])
        st.plotly_chart(fig)

    def grafico_corrente_elementos_filtro(i_La_inteiros, i_Ca_inteiros, i_resistor_inteiros, i_indutor_inteiros,
                                          i_capacitor_inteiros, i_nominal_capacitores, h_principal, h_inteiros, idioma):
        fig = go.Figure()
        fig.add_trace(go.Bar(name=traduzir('Resistor', idioma), x=h_inteiros, y=abs(i_resistor_inteiros) / i_nominal_capacitores))
        fig.add_trace(go.Bar(name=traduzir('Indutor', idioma), x=h_inteiros, y=abs(i_indutor_inteiros) / i_nominal_capacitores))
        fig.add_trace(go.Bar(name=traduzir('Capacitor', idioma), x=h_inteiros, y=abs(i_capacitor_inteiros) / i_nominal_capacitores))

        fig.update_layout(
            title=traduzir("Corrente Total / Corrente Nominal dos Capacitores", idioma),
            xaxis_title=traduzir("Harmônicas", idioma),
            yaxis_title=traduzir("Corrente", idioma) +" / [" + str(EngNumber(i_nominal_capacitores)) + " A]",
        )

        fig.update(layout_xaxis_range=[0, min(3 * h_principal, np.max(h_inteiros))])
        st.plotly_chart(fig)

    def escritas_correntes_de_fase_pu(tipo_de_filtro, corrente_eficaz_La, corrente_eficaz_resistor,
                                      corrente_eficaz_indutor, corrente_eficaz_capacitor, i_nominal_capacitores, idioma):
        st.write("$I_R = $", str(EngNumber((abs(corrente_eficaz_resistor)))), "$\\rm{A}$")
        if tipo_de_filtro == traduzir("Filtro Sintonizado", idioma) or traduzir(tipo_de_filtro, idioma) == "Amortecido":
            st.write("$I_L = $", str(EngNumber((abs(corrente_eficaz_indutor)))), "$\\rm{A}$")
        elif tipo_de_filtro == traduzir("Filtro Tipo C", idioma):
            st.write("$I_{La} = I_{Ca} = $", str(EngNumber((abs(corrente_eficaz_La)))), "$\\rm{A}$")
        st.write("$I_C = $", str(EngNumber((abs(corrente_eficaz_capacitor)))), "$= $", str(EngNumber((abs(corrente_eficaz_capacitor) / i_nominal_capacitores))), "$I_{C1}$")

    def escritas_potencias_trifasicas(tipo_de_filtro, potencia_eficaz_La, potencia_eficaz_Ca, potencia_eficaz_resistor,
                                      potencia_eficaz_indutor, potencia_eficaz_capacitor, Q_reat_fund_filtro,
                                      sobretensao_Angelo, sobretensao_Angelo_a):
        st.write("$P_R = $", str(EngNumber((abs(potencia_eficaz_resistor)))), "$\\rm{W}$")
        if tipo_de_filtro == "谐振型过滤器" or tipo_de_filtro == "阻尼型过滤器":
            st.write("$Q_L = $", str(EngNumber((abs(potencia_eficaz_indutor)))), "$\\rm{VAr}$")
        elif tipo_de_filtro == "C型过滤器":
            st.write("$Q_{La} = $", str(EngNumber((abs(potencia_eficaz_La)))), "$\\rm{VAr}$")
            st.write("$Q_{Ca} = $", str(EngNumber((abs(potencia_eficaz_La)))), "$\\rm{VAr} = $", str(EngNumber((abs(potencia_eficaz_Ca) / Q_reat_fund_filtro))), "$Q_{C1}$")
            # st.write(EngNumber(sobretensao_Angelo_a))
        st.write("$Q_C = $", str(EngNumber((abs(potencia_eficaz_capacitor)))), "$\\rm{VAr}$")
        st.write("${Q_C} = $", str(EngNumber((abs(potencia_eficaz_capacitor)))), "$\\rm{VAr}$", "$=$", str(EngNumber((abs(potencia_eficaz_capacitor)/Q_reat_fund_filtro))), "$Q_1$")
        # st.write(EngNumber(sobretensao_Angelo))

    def escritas_tensoes_de_fase_pu(tipo_de_filtro, tensao_eficaz_La, tensao_eficaz_Ca, tensao_eficaz_resistor,
                                    tensao_eficaz_indutor, tensao_eficaz_capacitor, V_fund_fase):
        # st.write("$V_R = $", EngNumber((abs(tensao_eficaz_resistor) / V_fund_fase)), "$\\rm{pu}$")
        st.write("$V_L = $", str(EngNumber((abs(tensao_eficaz_resistor)))), "$\\rm{V} =$", str(EngNumber((abs(tensao_eficaz_resistor / V_fund_fase)))), "$V_{1f}$")
        if tipo_de_filtro == "谐振型过滤器" or tipo_de_filtro == "阻尼型过滤器":
            st.write("$V_L = $", EngNumber((abs(tensao_eficaz_indutor))), "$\\rm{V}$",  str(EngNumber((abs(tensao_eficaz_indutor / V_fund_fase)))), "$V_{1f}$")
        elif tipo_de_filtro == "C型过滤器":
            st.write("$V_{La} = $", str(EngNumber((abs(tensao_eficaz_La)))), "$\\rm{V}$", "$=$", str(EngNumber((abs(tensao_eficaz_La / V_fund_fase)))), "$V_{1f}$")
            st.write("$V_{Ca} = $", str(EngNumber((abs(tensao_eficaz_Ca)))), "$\\rm{V}$", "$=$", str(EngNumber((abs(tensao_eficaz_Ca / V_fund_fase)))), "$V_{1f}$")

        st.write("$V_C = $", str(EngNumber((abs(tensao_eficaz_capacitor)))), "$\\rm{V}$", "$=$", str(EngNumber((abs(tensao_eficaz_capacitor / V_fund_fase)))), "$V_{1f}$")

    def grafico_tensao_elementos_filtro(h_principal, h_inteiros, v_resistor_inteiros, v_indutor_inteiros,
                                        v_capacitor_inteiros, v_barra_inteiros, V_fund_fase, idioma):
        fig = go.Figure()
        fig.add_trace(go.Bar(name=traduzir('Resistor', idioma), x=h_inteiros, y=abs(v_resistor_inteiros) / V_fund_fase))
        fig.add_trace(go.Bar(name=traduzir('Indutor', idioma), x=h_inteiros, y=abs(v_indutor_inteiros) / V_fund_fase))
        fig.add_trace(
            go.Bar(name=traduzir('Capacitor', idioma), x=h_inteiros, y=abs(v_capacitor_inteiros) / V_fund_fase))
        fig.add_trace(go.Bar(name=traduzir('Total', idioma), x=h_inteiros, y=abs(v_barra_inteiros) / V_fund_fase))

        fig.update_layout(
            title=traduzir("Tensão / Tensão de Fase", idioma),
            xaxis_title=traduzir("Harmônicas", idioma),
            yaxis_title=traduzir("Tensão", idioma)+" / [{} V]".format(EngNumber(V_fund_fase)),
        )

        fig.update(layout_xaxis_range=[0, min(3 * h_principal, np.max(h_inteiros))])
        st.plotly_chart(fig)

    def grafico_potencias_elementos_filtro(h_principal, h_inteiros, p_resistor_inteiros, p_indutor_inteiros,
                                           p_capacitor_inteiros, idioma):
        fig = go.Figure()
        fig.add_trace(go.Bar(name=traduzir('Resistor [W]', idioma), x=h_inteiros, y=abs(p_resistor_inteiros)))
        fig.add_trace(go.Bar(name=traduzir('Indutor [VAr]', idioma), x=h_inteiros, y=abs(p_indutor_inteiros)))
        fig.add_trace(go.Bar(name=traduzir('Capacitor [VAr]', idioma), x=h_inteiros, y=abs(p_capacitor_inteiros)))

        fig.update_layout(
            title=traduzir("Potência nos Elementos do Filtro", idioma),
            xaxis_title=traduzir("Harmônicas", idioma),
            yaxis_title=traduzir("Potência [VA]", idioma),
        )

        fig.update(layout_xaxis_range=[0, min(3 * h_principal, np.max(h_inteiros))])
        st.plotly_chart(fig)

    def grafico_modulo_impedancia(hh, Z_filtro, Z_trafo, Z_equivalente, Z_base_trafo, h_principal, idioma):
        my_array = np.zeros((len(hh), 4))
        my_array[:, 0] = np.transpose(hh)
        my_array[:, 1] = np.transpose(abs(Z_filtro)) / Z_base_trafo
        my_array[:, 2] = np.transpose(abs(Z_trafo)) / Z_base_trafo
        my_array[:, 3] = np.transpose(abs(Z_equivalente)) / Z_base_trafo

        colunas = ['hh', traduzir('Filtro', idioma), traduzir('Transformador', idioma), traduzir('Equivalente', idioma)]
        df = pd.DataFrame(my_array, columns=colunas)
        fig = px.line(df, x="hh", y=colunas[1:],
                      title=traduzir('Relação entre Módulo de Impedância e Frequência', idioma),
                      labels={'hh': traduzir('Harmônica', idioma), "value": traduzir("Módulo [pu]", idioma),
                              "variable": traduzir("Componente", idioma)})
        fig.update_layout(yaxis_range=[0, 4])
        fig.update_layout(xaxis_range=[0, 3 * h_principal])
        st.plotly_chart(fig)

        index_min = np.where(np.abs(Z_filtro) == np.min(np.abs(Z_filtro)))[0]
        st.write(traduzir('Harmônica de Mínima Impedância do Filtro', idioma) + f" $h=$ {hh[index_min][0]}")

        my_array = np.zeros((len(hh), 4))
        my_array[:, 0] = np.transpose(hh)
        my_array[:, 1] = np.transpose(np.angle(Z_filtro, deg=True))
        my_array[:, 2] = np.transpose(np.angle(Z_trafo, deg=True))
        my_array[:, 3] = np.transpose(np.angle(Z_equivalente, deg=True))

        df = pd.DataFrame(my_array, columns=colunas)
        fig = px.line(df, x="hh", y=colunas[1:],
                      title=traduzir('Relação entre Fase da Impedância e Frequência', idioma),
                      labels={'hh': traduzir('Harmônica', idioma), "value": traduzir("Fase [°]", idioma),
                              "variable": traduzir("Componente", idioma)})
        fig.update_layout(xaxis_range=[0, 3 * h_principal])
        st.plotly_chart(fig)

    def grafico_de_correntes_entrada(xxx, yyy, I_base_trafo, idioma):

        fig_pu = go.Figure(data=[
            go.Bar(name=traduzir("Conteúdo Harmônico da Corrente [pu]", idioma), x=xxx, y=yyy / I_base_trafo),
        ])

        fig_pu.update_layout(
            title=traduzir("Conteúdo Harmônico da Corrente [pu]", idioma),
            xaxis_title=traduzir("Harmônica", idioma),
            yaxis_title=traduzir("Corrente [pu]", idioma),
        )

        st.plotly_chart(fig_pu)

        fig_A = go.Figure(data=[
            go.Bar(name=traduzir("Conteúdo Harmônico da Corrente [A]", idioma), x=xxx, y=yyy),
        ])

        fig_A.update_layout(
            title=traduzir("Conteúdo Harmônico da Corrente [A]", idioma),
            xaxis_title=traduzir("Harmônica", idioma),
            yaxis_title=traduzir("Corrente [A]", idioma),
        )

        st.plotly_chart(fig_A)

