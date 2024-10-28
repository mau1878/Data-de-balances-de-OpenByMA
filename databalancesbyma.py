import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# Ticker and Industry data
tickers_data = {
    "GGAL": "Bancos", "YPFD": "Petróleo y Gas", "PAMP": "Generación y Transporte de Energía Eléctrica",
    "TXAR": "Aluminio y acero", "ALUA": "Aluminio y acero", "CRES": "Real Estate", "SUPV": "Bancos",
    "CEPU": "Generación y Transporte de Energía Eléctrica", "BMA": "Bancos",
    "TGSU2": "Transporte y distribución de Gas",
    "TRAN": "Generación y Transporte de Energía Eléctrica", "EDN": "Generación y Transporte de Energía Eléctrica",
    "LOMA": "Construcción", "MIRG": "Consumo discrecional", "DGCU2": "Transporte y distribución de Gas",
    "BBAR": "Bancos", "MOLI": "Alimentos y Bebidas", "TGNO4": "Transporte y distribución de Gas",
    "CGPA2": "Transporte y distribución de Gas", "COME": "Holding", "IRSA": "Real Estate",
    "BYMA": "Actividades Financieras y Bursátiles", "TECO2": "Telecomunicaciones",
    "METR": "Transporte y distribución de Gas",
    "CECO2": "Generación y Transporte de Energía Eléctrica", "BHIP": "Bancos", "AGRO": "Maquinaria (Agro)",
    "LEDE": "Alimentos y Bebidas", "CVH": "Telecomunicaciones", "HAVA": "Consumo discrecional", "AUSO": "Autopistas",
    "VALO": "Bancos", "SEMI": "Alimentos y Bebidas", "INVJ": "Alimentos y Bebidas", "CTIO": "Real Estate",
    "MORI": "Alimentos y Bebidas", "HARG": "Construcción", "GCLA": "Telecomunicaciones", "SAMI": "Alimentos y Bebidas",
    "BOLT": "Holding", "MOLA": "Alimentos y Bebidas", "CAPX": "Petróleo y Gas", "OEST": "Autopistas",
    "LONG": "Consumo discrecional", "GCDI": "Construcción", "GBAN": "Transporte y distribución de Gas", "CELU": "Papel",
    "FERR": "Construcción", "CADO": "Agrícola-Ganadera", "GAMI": "Informática", "PATA": "Comercio",
    "CARC": "Petroquímica",
    "BPAT": "Bancos", "RICH": "Farmacéutica", "INTR": "Alimentos y Bebidas", "GARO": "Holding",
    "FIPL": "Consumo discrecional",
    "GRIM": "Calzado e indumentaria", "DYCA": "Construcción", "POLL": "Construcción",
    "DGCE": "Transporte y distribución de Gas",
    "DOME": "Consumo discrecional", "ROSE": "Sanidad Animal", "MOLA5": "Alimentos y Bebidas",
    "RIGO": "Manufacturas de Origen Industrial"
}

# Streamlit page setup
st.title("Financial Data Retrieval & Plotting")
st.write("Select tickers or industries, data categories, and plot type.")

# User selection: Industry or specific ticker
industries = list(set(tickers_data.values()))
selected_industries = st.multiselect("Select Industries", industries)
selected_tickers = st.multiselect("Select Tickers", list(tickers_data.keys()))

# Filter tickers based on industry selection
if selected_industries:
    filtered_tickers = [ticker for ticker, industry in tickers_data.items() if industry in selected_industries]
    if selected_tickers:
        filtered_tickers = list(set(filtered_tickers) & set(selected_tickers))
else:
    filtered_tickers = selected_tickers

st.write("Selected Tickers:", filtered_tickers)

# Define all data categories available
data_categories = [
    "Ingresos Por Intereses", "Egresos Por Intereses", "Ingresos por Comisiones", "Egresos por Comisiones",
    "Cargo por Incobrabilidad",
    "Resultado neto por medición de instrumentos financieros a valor razonable con cambios en resultados",
    "Diferencia de cotización de oro y moneda extranjera", "Otros ingresos operativos",
    "Resultado por baja de activos medidos a costo amortizado",
    "Ingreso operativo neto", "Honorarios a Directores y Síndicos", "Otros gastos de administracion",
    "Beneficios al personal",
    "Otros gastos operativos", "Depreciaciones y Amortizaciones", "RESULTADOS POR ASOCIADAS Y NEGOCIOS CONJUNTOS",
    "RECPAM", "Ganancia (pérdida), antes de impuestos", "Ingreso (gasto) por impuestos a las ganancias",
    "Ganancia (pérdida) del período / ejercicio", "Otro resultado integral del ejercicio / período",
    "Resultado Integral Total del Ejercicio / Período",
    "Flujos de efectivo procedentes de (utilizados en) actividades de operación",
    "Flujos de efectivo procedentes de (utilizados en) actividades de inversión",
    "Flujos de efectivo procedentes de (utilizados en) actividades de financiación",
    "EFECTO DE LAS VARIACIONES DEL TIPO DE CAMBIO", "EFECTO DEL RESULTADO MONETARIO DE EFECTIVO Y SUS EQUIVALENTES",
    "Incremento (Disminución) Neta de efectivo y equivalentes", "Ganancia (pérdida) básica por acción",
    "Ganancias (pérdida) diluída por acción", "Total Patrimonio Neto del Ejercicio anterior (mismo peródo)"
]
selected_data_categories = st.multiselect("Select Data Categories", data_categories, default=data_categories[:2])

# Define plot types
plot_types = ["Line", "Bar", "Scatter"]
selected_plot_type = st.selectbox("Select Plot Type", plot_types)

# Fetch and process data when button is pressed
if st.button("Fetch & Plot Data"):
    all_data = []

    for ticker in filtered_tickers:
        cookies = {'JSESSIONID': '8A8FE329FE5AFCEF16E27D2ADA32956E'}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0',
        }
        params = {'symbol': ticker}

        response = requests.get(
            'https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bolsar/balances',
            params=params,
            cookies=cookies,
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            data = response.json()
            data_list = data.get('data', [])

            if data_list and 'errorMsg' not in data_list[0]:
                df = pd.DataFrame(data_list)
                cuentas_df = df['Cuentas'].explode().reset_index(drop=True)
                cuentas_df = pd.json_normalize(cuentas_df)
                cuentas_df['Ticker'] = ticker
                cuentas_df['Fecha'] = df['fecha'].iloc[0] if 'fecha' in df.columns else None
                all_data.append(cuentas_df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Filter selected data categories
        plot_df = combined_df[combined_df['Nombre'].isin(selected_data_categories)]

        # Plotting with Plotly
        if not plot_df.empty:
            if selected_plot_type == "Line":
                fig = px.line(
                    plot_df,
                    x='Fecha',
                    y='Importe',
                    color='Nombre',
                    line_group='Ticker',
                    title="Financial Data Over Time",
                    labels={'Importe': 'Value'}
                )
            elif selected_plot_type == "Bar":
                fig = px.bar(
                    plot_df,
                    x='Ticker',
                    y='Importe',
                    color='Nombre',
                    barmode='group',
                    title="Financial Data by Ticker",
                    labels={'Importe': 'Value'}
                )
            elif selected_plot_type == "Scatter":
                if len(selected_data_categories) >= 2:
                    x_category = selected_data_categories[0]
                    y_category = selected_data_categories[1]
                    scatter_df = plot_df[plot_df['Nombre'].isin([x_category, y_category])]
                    scatter_df = scatter_df.pivot(index="Ticker", columns="Nombre", values="Importe").reset_index()

                    fig = px.scatter(
                        scatter_df,
                        x=x_category,
                        y=y_category,
                        text='Ticker',
                        title=f"Scatter Plot of {x_category} vs {y_category}",
                        labels={'Ticker': 'Tickers'}
                    )
                else:
                    st.warning("Please select at least two data categories for scatter plot.")
            st.plotly_chart(fig)
        else:
            st.warning("No data available for the selected categories.")
    else:
        st.warning("Failed to fetch data for the selected tickers.")
