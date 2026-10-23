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
    "Registra ventas, abonos, créditos pendientes y notifica a tus clientas por"
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
            "Total Venta ($)",
            "Abono ($)",
            "Crédito Pendiente ($)",
            "Estado",
        ]
    )

if "clientas" not in st.session_state:
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

    # Selección de clienta guardada
    if not st.session_state.clientas.empty:
        lista_nombres = list(st.session_state.clientas["Cliente"].unique())
        lista_nombres.insert(0, "-- Escribir nueva o seleccionar --")
        cliente_seleccionada = st.sidebar.selectbox(
            "Seleccionar Clienta Guardada", lista_nombres
        )

        if cliente_seleccionada != "-- Escribir nueva o seleccionar --":
            cliente = cliente_seleccionada
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
            " opción 'Crear / Registrar Nueva Clienta'."
        )
        cliente = st.sidebar.text_input(
            "Nombre de la Clienta", placeholder="Ej. Ana Gómez"
        )
        telefono = st.sidebar.text_input("Teléfono", placeholder="573001234567")

    if tipo_movimiento == "Venta / Aviso de Pago":
        descripcion = st.sidebar.text_input(
            "Detalle del Producto", placeholder="Ej. Bolso Crossbody Negro"
        )
        total_venta = st.sidebar.number_input(
            "Total Venta ($)", min_value=0.0, value=50000.0, step=1000.0
        )
        abono = st.sidebar.number_input(
            "Abono Realizado ($)", min_value=0.0, value=50000.0, step=1000.0
        )

        # Calcular crédito pendiente automáticamente
        credito_pendiente = max(0.0, total_venta - abono)
        st.sidebar.info(f"📉 Crédito Pendiente: ${credito_pendiente:,.2f}")

        if credito_pendiente == 0:
            estado = "Pagado Completo 🟢"
        elif abono > 0:
            estado = "Abono / Parcial 🟡"
        else:
            estado = "Crédito Pendiente 🔴"
    else:
        descripcion = st.sidebar.text_area(
            "Texto de la Promoción",
            value=(
                "¡Hola! 👋 Te escribo de GreisyNu Store. Tenemos nuevos bolsos y"
                " accesorios disponibles. ¿Te gustaría ver el catálogo?"
            ),
        )
        total_venta = 0.0
        abono = 0.0
        credito_pendiente = 0.0
        estado = "Promoción 📢"

    if st.sidebar.button("Guardar Venta y Generar WhatsApp"):
        if not cliente or not telefono:
            st.sidebar.error(
                "⚠️ Por favor, asegúrate de ingresar el nombre y el teléfono."
            )
        else:
            nueva_venta = pd.DataFrame(
                [[
                    fecha_venta,
                    cliente,
                    telefono,
                    tipo_movimiento,
                    descripcion,
                    total_venta,
                    abono,
                    credito_pendiente,
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

            # Guardar automáticamente la clienta si no estaba
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
total_
