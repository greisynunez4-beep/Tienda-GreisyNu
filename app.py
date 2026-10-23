import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y Clientas",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero y Directorio de Clientas")
st.write(
    "Selecciona a tus clientas guardadas al registrar ventas y notifícalas por"
    " WhatsApp."
)

# Inicializar bases de datos en la sesión
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

if "clientas" not in st.session_state:
    # Base de datos independiente para guardar clientas (Nombre y Teléfono)
    st.session_state.clientas = pd.DataFrame(columns=["Cliente", "Teléfono"])

# --- MENÚ LATERAL: REGISTROS ---
st.sidebar.header("📝 Menú de Registro")

menu_opcion = st.sidebar.selectbox(
    "¿Qué deseas hacer?",
    [
        "Registrar Venta o Promoción",
        "Crear / Registrar Nueva Clienta",
        "Registrar Compra / Inversión Global",
    ],
)

if menu_opcion == "Crear / Registrar Nueva Clienta":
    st.sidebar.subheader("👤 Nueva Clienta")
    nueva_cli_nombre = st.sidebar.text_input(
        "Nombre Completo", placeholder="Ej. Ana Gómez"
    )
    nueva_cli_tel = st.sidebar.text_input(
        "Teléfono (con código de país)", placeholder="573001234567"
    )

    if st.sidebar.button("Guardar Clienta"):
        if not nueva_cli_nombre or not nueva_cli_tel:
            st.sidebar.error("⚠️ Por favor, llena ambos campos.")
        else:
            # Verificar si ya existe para no duplicar
            if (
                not st.session_state.clientas.empty
                and nueva_cli_nombre
                in st.session_state.clientas["Cliente"].values
            ):
                st.sidebar.warning("⚠️ Esta clienta ya está registrada.")
            else:
                df_nueva = pd.DataFrame(
                    [[nueva_cli_nombre, nueva_cli_tel]],
                    columns=st.session_state.clientas.columns,
                )
                st.session_state.clientas = pd.concat(
                    [st.session_state.clientas, df_nueva], ignore_index=True
                )
                st.sidebar.success("¡Clienta guardada con éxito!")

elif menu_opcion == "Registrar Compra / Inversión Global":
    st.sidebar.subheader("📦 Inversión en Mercancía")
    fecha_compra = st.sidebar.date_input("Fecha de Compra")
    detalle_compra = st.sidebar.text_input(
        "Proveedor o Detalle",
        placeholder="Ej. Surtido de bolsos mayorista",
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
            st.session_state.compras = st.session_state.compras.sort_values(
                by="Fecha", ascending=False
            )
            st.sidebar.success("¡Inversión guardada con éxito!")

else:  # Registrar Venta o Promoción
    st.sidebar.subheader("🛍️ Venta o Mensaje a Clienta")
    tipo_movimiento = st.sidebar.selectbox(
        "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
    )
    fecha_venta = st.sidebar.date_input("Fecha")

    # Si hay clientas creadas, mostrar selector desplegable
    if not st.session_state.clientas.empty:
        lista_nombres = list(st.session_state.clientas["Cliente"].unique())
        lista_nombres.insert(0, "-- Escribir nueva o seleccionar --")
        cliente_seleccionada = st.sidebar.selectbox(
            "Seleccionar Clienta Guardada", lista_nombres
        )

        if cliente_seleccionada != "-- Escribir nueva o seleccionar --":
            cliente = cliente_seleccionada
            # Buscar su teléfono automáticamente
            telefono = str(
                st.session_state.clientas.loc[
                    st.session_state.clientas["Cliente"] == cliente, "Teléfono"
                ].values[0]
            )
            st.sidebar.info(f"📱 Teléfono cargado: `{telefono}`")
        else:
            cliente = st.sidebar.text_input(
                "Nombre de la Clienta", placeholder="Ej. Ana Gómez"
            )
            telefono = st.sidebar.text_input(
                "Teléfono", placeholder="573001234567"
            )
    else:
        st.sidebar.warning(
            "💡 No tienes clientas guardadas aún. Puedes agregarlas en la"
            " opción 'Crear / Registrar Nueva Clienta' del menú superior."
        )
        cliente = st.sidebar.text_input(
            "Nombre de la Clienta", placeholder="Ej. Ana Gómez"
        )
        telefono = st.sidebar.text_input("Teléfono", placeholder="573001234567")

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
                "⚠️ Por favor, asegúrate de ingresar el nombre y el teléfono."
            )
        else:
            # Registrar venta
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
            st.session_state.ventas = st.session_state.ventas.sort_values(
                by="Fecha", ascending=False
            )

            # Guardar automáticamente la clienta en el directorio si no estaba
            if (
                st.session_state.clientas.empty
                or cliente not in st.session_state.clientas["Cliente"].values
            ):
                nueva_cli = pd.DataFrame(
                    [[cliente, telefono]],
                    columns=st.session_state.clientas.columns,
                )
                st.session_state.clientas = pd.concat(
                    [st.session_state.clientas, nueva_cli], ignore_index=True
                )

            st.sidebar.success("¡Venta registrada con éxito!")

# --- PANEL PRINCIPAL: RESUMEN Y PESTAÑAS ---
df_compras = st.session_state.compras
df_ventas = st.session_state.ventas
df_clientas = st.session_state.clientas

# Calcular totales globales
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

# Pestañas principales
tab1, tab2, tab3 = st.tabs([
    "💬 Historial de Ventas y WhatsApp",
    "👥 Directorio de Clientas",
    "📦 Registro de Compras Detallado",
])

with tab1:
    if not df_ventas.empty:
        st.subheader("📋 Ventas y Avisos Ordenados por Fecha")

        for index, row in df_ventas.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])

                c1.markdown(f"**📅 {row['Fecha']}**")
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
    st.subheader("👥 Base de Datos de Clientas")
    if not df_clientas.empty:
        st.dataframe(df_clientas, use_container_width=True)
        st.success(f"Tienes un total de **{len(df_clientas)} clientas** guardadas.")

        if st.button("🗑️ Borrar Directorio de Clientas"):
            st.session_state.clientas = pd.DataFrame(columns=["Cliente", "Teléfono"])
            st.rerun()
    else:
        st.info(
            "Aún no hay clientas registradas. Se guardarán automáticamente aquí"
            " cuando registres ventas o usando el menú lateral."
        )

with tab3:
    if not df_compras.empty:
        st.subheader("📋 Compras Mayoristas Ordenadas por Fecha")
        st.dataframe(df_compras, use_container_width=True)

        if st.button("🗑️ Borrar Historial de Compras"):
            st.session_state.compras = pd.DataFrame(columns=df_compras.columns)
            st.rerun()
    else:
        st.info(
            "Aún no hay compras registradas. Usa el menú izquierdo para"
            " registrar tus inversiones globales."
        )
