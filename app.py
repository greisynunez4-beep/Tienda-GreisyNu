import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y WhatsApp",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero y WhatsApp")
st.write(
    "Lleva el control de tus ventas, costos, ganancias y notifica a tus"
    " clientas al instante."
)

# Definir las columnas oficiales y completas de la tienda
COLUMNAS_OFICIALES = [
    "Fecha",
    "Cliente",
    "Teléfono",
    "Tipo",
    "Descripción",
    "Cantidad",
    "Costo Unitario ($)",
    "Precio Venta ($)",
    "Ingreso Total ($)",
    "Costo Total ($)",
    "Ganancia Neta ($)",
    "Margen (%)",
    "Estado",
]

# Inicializar o corregir la base de datos si las columnas no coinciden
if (
    "data" not in st.session_state
    or list(st.session_state.data.columns) != COLUMNAS_OFICIALES
):
    st.session_state.data = pd.DataFrame(columns=COLUMNAS_OFICIALES)

# --- MENÚ LATERAL: REGISTRAR MOVIMIENTO ---
st.sidebar.header("📝 Registrar Transacción")

cliente = st.sidebar.text_input("Nombre de la Clienta", placeholder="Ej. Ana Gómez")
telefono = st.sidebar.text_input(
    "Teléfono (con código de país)", placeholder="573001234567"
)
tipo_movimiento = st.sidebar.selectbox(
    "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
)
fecha = st.sidebar.date_input("Fecha")
cantidad = st.sidebar.number_input("Cantidad", min_value=1, value=1, step=1)

if tipo_movimiento == "Venta / Aviso de Pago":
    descripcion = st.sidebar.text_input(
        "Detalle del Producto", placeholder="Ej. Bolso Crossbody Negro"
    )
    costo_unitario = st.sidebar.number_input(
        "Costo de Compra (Mayorista) c/u ($)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )
    precio_unitario = st.sidebar.number_input(
        "Precio de Venta al Público c/u ($)",
        min_value=0.0,
        value=50000.0,
        step=1000.0,
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
    costo_unitario = 0.0
    precio_unitario = 0.0
    estado = "Promoción 📢"

if st.sidebar.button("Guardar y Generar WhatsApp"):
    if not cliente or not telefono:
        st.sidebar.error(
            "⚠️ Por favor, ingresa el nombre y el teléfono de la clienta."
        )
    else:
        if tipo_movimiento == "Venta / Aviso de Pago":
            ingreso_total = cantidad * precio_unitario
            costo_total = cantidad * costo_unitario
            ganancia_neta = ingreso_total - costo_total
            margen = (
                (ganancia_neta / ingreso_total * 100)
                if ingreso_total > 0
                else 0
            )
        else:
            ingreso_total = 0.0
            costo_total = 0.0
            ganancia_neta = 0.0
            margen = 0.0

        nuevo_registro = pd.DataFrame(
            [[
                fecha,
                cliente,
                telefono,
                tipo_movimiento,
                descripcion,
                cantidad,
                costo_unitario,
                precio_unitario,
                ingreso_total,
                costo_total,
                ganancia_neta,
                margen,
                estado,
            ]],
            columns=COLUMNAS_OFICIALES,
        )
        st.session_state.data = pd.concat(
            [st.session_state.data, nuevo_registro], ignore_index=True
        )
        st.sidebar.success("¡Registrado con éxito!")

# --- PANEL PRINCIPAL: RESUMEN FINANCIERO Y WHATSAPP ---
df = st.session_state.data

if not df.empty:
    # Filtrar métricas de ventas reales
    df_ventas = df[df["Tipo"] == "Venta / Aviso de Pago"]

    if not df_ventas.empty:
        total_ingresos = df_ventas["Ingreso Total ($)"].sum()
        total_costos = df_ventas["Costo Total ($)"].sum()
        ganancia_total = df_ventas["Ganancia Neta ($)"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ventas Totales", f"${total_ingresos:,.2f}")
        col2.metric("📦 Costo de Mercancía", f"${total_costos:,.2f}")
        col3.metric("📈 Ganancia Neta Real", f"${ganancia_total:,.2f}")

        st.markdown("---")

    st.subheader("📋 Historial de Clientas y Envíos por WhatsApp")

    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            col1.markdown(f"**👤 {row['Cliente']}**")
            col1.caption(f"📱 Tel: `{row['Teléfono']}`")

            col2.markdown(f"**Estado:** {row['Estado']}")

            if row["Tipo"] == "Venta / Aviso de Pago":
                col3.markdown(
                    f"**Prod:** {row['Descripción']} <br> **Venta:**"
                    f" ${row['Ingreso Total ($)']:,.2f} <br> **Ganancia:**"
                    f" 🟢 ${row['Ganancia Neta ($)']:,.2f}",
                    unsafe_allow_html=True,
                )
            else:
                col3.markdown(f"**Promoción:** {row['Descripción']}")

            # Construir mensaje personalizado para WhatsApp
            if "Pago Recibido" in str(row["Estado"]):
                texto_msj = (
                    f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                    " confirmarte que hemos recibido tu pago por"
                    f" ${row['Ingreso Total ($)']:,.2f} correspondiente a:"
                    f" *{row['Descripción']}*. ¡Muchas gracias por tu compra!"
                )
            elif "Promoción" in str(row["Estado"]):
                texto_msj = row["Descripción"]
            else:
                texto_msj = (
                    f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store para"
                    f" recordarte que tienes un saldo pendiente de"
                    f" ${row['Ingreso Total ($)']:,.2f} por:"
                    f" *{row['Descripción']}*."
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
        "Aún no hay registros. Llena los datos en el panel izquierdo para"
        " empezar a ver tus cuentas y generar mensajes."
    )
