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
    "Lleva el control de tus compras globales, tus ventas y notifica a tus"
    " clientas al instante."
)

# Inicializar bases de datos separadas para Compras y Ventas/Mensajes en la sesión
if "compras" not in st.session_state:
    st.session_state.compras = pd.DataFrame(
        columns=["Fecha", "Proveedor / Detalle", "Inversión Total ($)"]
    )

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame(
        columns=[
            "Fecha",
            "Cliente",
            "Teléfono",
            "Tipo",
            "Descripción",
            "Precio Venta ($)",
            "Estado",
        ]
    )

# --- MENÚ LATERAL: REGISTRAR COMPRAS O VENTAS ---
st.sidebar.header("📝 Menú de Registro")

menu_opcion = st.sidebar.selectbox(
    "¿Qué deseas registrar?",
    ["Registrar Compra / Inversión Global", "Registrar Venta o Promoción"],
)

if menu_opcion == "Registrar Compra / Inversión Global":
    st.sidebar.subheader("📦 Inversión en Mercancía")
    fecha_compra = st.sidebar.date_input("Fecha de Compra")
    detalle_compra = st.sidebar.text_input(
        "Proveedor o Detalle",
        placeholder="Ej. Surtido de bolsos y accesorios mayorista",
    )
    total_inversion = st.sidebar.number_input(
        "Costo Total de la Compra ($)",
        min_value=0.0,
        value=200000.0,
        step=10000.0,
    )

    if st.sidebar.button("Guardar Compra"):
        if not detalle_compra:
            st.sidebar.error("⚠️ Por favor, ingresa un detalle o proveedor.")
        else:
            nueva_compra = pd.DataFrame(
                [[fecha_compra, detalle_compra, total_inversion]],
                columns=st.session_state.compras.columns,
            )
            st.session_state.compras = pd.concat(
                [st.session_state.compras, nueva_compra], ignore_index=True
            )
            st.sidebar.success("¡Inversión en mercancía guardada con éxito!")

else:
    st.sidebar.subheader("🛍️ Venta o Mensaje a Clienta")
    cliente = st.sidebar.text_input(
        "Nombre de la Clienta", placeholder="Ej. Ana Gómez"
    )
    telefono = st.sidebar.text_input(
        "Teléfono (con código de país)", placeholder="573001234567"
    )
    tipo_movimiento = st.sidebar.selectbox(
        "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
    )
    fecha_venta = st.sidebar.date_input("Fecha")

    if tipo_movimiento == "Venta / Aviso de Pago":
        descripcion = st.sidebar.text_input(
            "Detalle del Producto", placeholder="Ej. Bolso Crossbody Negro"
        )
        precio_venta = st.sidebar.number_input(
            "Precio de Venta Total ($)",
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
        precio_venta = 0.0
        estado = "Promoción 📢"

    if st.sidebar.button("Guardar Venta y Generar WhatsApp"):
        if not cliente or not telefono:
            st.sidebar.error(
                "⚠️ Por favor, ingresa el nombre y el teléfono de la clienta."
            )
        else:
            nueva_venta = pd.DataFrame(
                [[
                    fecha_venta,
                    cliente,
                    telefono,
                    tipo_movimiento,
                    descripcion,
                    precio_venta,
                    estado,
                ]],
                columns=st.session_state.ventas.columns,
            )
            st.session_state.ventas = pd.concat(
                [st.session_state.ventas, nueva_venta], ignore_index=True
            )
            st.sidebar.success("¡Venta registrada con éxito!")

# --- PANEL PRINCIPAL: RESUMEN Y WHATSAPP ---
df_compras = st.session_state.compras
df_ventas = st.session_state.ventas

# Calcular totales generales
total_invertido_compras = (
    df_compras["Inversión Total ($)"].sum() if not df_compras.empty else 0.0
)
df_solo_ventas = (
    df_ventas[df_ventas["Tipo"] == "Venta / Aviso de Pago"]
    if not df_ventas.empty
    else pd.DataFrame()
)
total_ingresos_ventas = (
    df_solo_ventas["Precio Venta ($)"].sum()
    if not df_solo_ventas.empty
    else 0.0
)
balance_general = total_ingresos_ventas - total_invertido_compras

# Tarjetas de Resumen Financiero Global
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("📦 Total Invertido en Compras", f"${total_invertido_compras:,.2f}")
col_m2.metric("💰 Ventas Totales", f"${total_ingresos_ventas:,.2f}")
col_m3.metric(
    "📊 Balance Global (Ventas - Inversión)", f"${balance_general:,.2f}"
)

st.markdown("---")

# Pestañas para organizar la visualización
tab1, tab2 = st.tabs(["💬 Historial de Ventas y WhatsApp", "📦 Registro de Compras Globales"])

with tab1:
    if not df_ventas.empty:
        st.subheader("📋 Clientas y Envíos rápidos por WhatsApp")

        for index, row in df_ventas.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])

                c1.markdown(f"**👤 {row['Cliente']}**")
                c1.caption(f"📱 Tel: `{row['Teléfono']}`")

                c2.markdown(f"**Estado:** {row['Estado']}")

                if row["Tipo"] == "Venta / Aviso de Pago":
                    c3.markdown(
                        f"**Prod:** {row['Descripción']} <br> **Valor:**"
                        f" ${row['Precio Venta ($)']:,.2f}",
                        unsafe_allow_html=True,
                    )
                else:
                    c3.markdown(f"**Promoción:** {row['Descripción']}")

                # Construir mensaje personalizado para WhatsApp
                if "Pago Recibido" in str(row["Estado"]):
                    texto_msj = (
                        f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store"
                        f" para confirmarte que hemos recibido tu pago por"
                        f" ${row['Precio Venta ($)']:,.2f} correspondiente a:"
                        f" *{row['Descripción']}*. ¡Muchas gracias por tu"
                        " compra!"
                    )
                elif "Promoción" in str(row["Estado"]):
                    texto_msj = row["Descripción"]
                else:
                    texto_msj = (
                        f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store"
                        f" para recordarte que tienes un saldo pendiente de"
                        f" ${row['Precio Venta ($)']:,.2f} por:"
                        f" *{row['Descripción']}*."
                    )

                mensaje_codificado = urllib.parse.quote(texto_msj)
                link_wsp = (
                    f"https://wa.me/{row['Teléfono']}?text={mensaje_codificado}"
                )

                c4.markdown(
                    f"[💬 Enviar a WhatsApp]({link_wsp})", unsafe_allow_html=True
                )
                st.markdown("---")

        if st.button("🗑️ Borrar Historial de Ventas"):
            st.session_state.ventas = pd.DataFrame(columns=df_ventas.columns)
            st.rerun()
    else:
        st.info("Aún no hay registros de ventas o mensajes.")

with tab2:
    if not df_compras.empty:
        st.subheader("📋 Historial de Inversiones en Compras Mayoristas")
        st.dataframe(df_compras, use_container_width=True)

        if st.button("🗑️ Borrar Historial de Compras"):
            st.session_state.compras = pd.DataFrame(columns=df_compras.columns)
            st.rerun()
    else:
        st.info(
            "Aún no hay compras registradas. Usa el menú izquierdo para"
            " registrar tus inversiones globales."
        )
