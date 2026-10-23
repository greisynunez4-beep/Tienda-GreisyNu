import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Gestión y WhatsApp",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control y Automatización por WhatsApp")
st.write(
    "Registra las ventas de tus bolsos y accesorios para notificar a tus"
    " clientas al instante."
)

# Definir las columnas oficiales y obligatorias
COLUMNAS_OFICIALES = [
    "Fecha",
    "Cliente",
    "Teléfono",
    "Tipo",
    "Descripción",
    "Total ($)",
    "Estado",
]

# Inicializar o corregir la base de datos si las columnas no coinciden
if (
    "data" not in st.session_state
    or list(st.session_state.data.columns) != COLUMNAS_OFICIALES
):
    st.session_state.data = pd.DataFrame(columns=COLUMNAS_OFICIALES)

# --- MENÚ LATERAL: REGISTRAR VENTA O PAGO ---
st.sidebar.header("📝 Registrar Venta o Pago")

cliente = st.sidebar.text_input("Nombre de la Clienta", placeholder="Ej. Ana Gómez")
telefono = st.sidebar.text_input(
    "Teléfono (con código de país)", placeholder="573001234567"
)
tipo_movimiento = st.sidebar.selectbox(
    "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
)
fecha = st.sidebar.date_input("Fecha")

if tipo_movimiento == "Venta / Aviso de Pago":
    descripcion = st.sidebar.text_input(
        "Detalle del Producto", placeholder="Ej. Bolso Crossbody Negro"
    )
    monto = st.sidebar.number_input(
        "Monto Total ($)", min_value=0.0, value=50000.0, step=1000.0
    )
    estado = st.sidebar.selectbox(
        "Estado del Pago", ["Pago Recibido 🟢", "Pendiente de Pago 🟡"]
    )
else:
    descripcion = st.sidebar.text_area(
        "Texto de la Promoción",
        value=(
            "¡Hola! 👋 Te escribo de GreisyNu Store. Tenemos nuevos bolsos y"
            " accesorios disponibles. ¿Te gustaría ver el catálogo?"
        ),
    )
    monto = 0.0
    estado = "Promoción 📢"

if st.sidebar.button("Generar Registro y Mensaje de WhatsApp"):
    if not cliente or not telefono:
        st.sidebar.error(
            "⚠️ Por favor, ingresa el nombre y el teléfono de la clienta."
        )
    else:
        nuevo_registro = pd.DataFrame(
            [[fecha, cliente, telefono, tipo_movimiento, descripcion, monto, estado]],
            columns=COLUMNAS_OFICIALES,
        )
        st.session_state.data = pd.concat(
            [st.session_state.data, nuevo_registro], ignore_index=True
        )
        st.sidebar.success("¡Guardado con éxito!")

# --- PANEL PRINCIPAL ---
df = st.session_state.data

if not df.empty:
    st.subheader("📋 Historial de Clientas y Envíos por WhatsApp")
    st.write(
        "Verifica que el número y el valor sean correctos, luego haz clic en el"
        " botón verde para redactar el mensaje en WhatsApp."
    )

    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            col1.markdown(f"**👤 {row['Cliente']}**")
            col1.caption(f"📱 Tel: `{row['Teléfono']}`")

            col2.markdown(f"**Estado:** {row['Estado']}")
            col3.markdown(
                f"**Prod:** {row['Descripción']} <br> **Valor:**"
                f" ${row['Total ($)']:,.2f}",
                unsafe_allow_html=True,
            )

            # Construir mensaje personalizado con el nombre, producto y valor
            if "Pago Recibido" in str(row["Estado"]):
                texto_msj = (
                    f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                    " confirmarte que hemos recibido tu pago por"
                    f" ${row['Total ($)']:,.2f} correspondiente a:"
                    f" *{row['Descripción']}*. ¡Muchas gracias por tu compra!"
                )
            elif "Promoción" in str(row["Estado"]):
                texto_msj = row["Descripción"]
            else:
                texto_msj = (
                    f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                    f" recordarte que tienes un saldo pendiente de ${row['Total ($)']:,.2f}"
                    f" por: *{row['Descripción']}*."
                )

            mensaje_codificado = urllib.parse.quote(texto_msj)
            link_wsp = (
                f"https://wa.me/{row['Teléfono']}?text={mensaje_codificado}"
            )

            col4.markdown(
                f"[💬 Enviar a WhatsApp]({link_wsp})", unsafe_allow_html=True
            )
            st.markdown("---")

    if st.button("🗑️ Borrar Todo el Historial"):
        st.session_state.data = pd.DataFrame(columns=COLUMNAS_OFICIALES)
        st.rerun()
else:
    st.info(
        "Aún no hay registros. Llena los datos en el panel izquierdo (Nombre,"
        " Teléfono y Monto) para empezar."
    )
