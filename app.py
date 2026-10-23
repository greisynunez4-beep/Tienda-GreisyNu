import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y Clientas",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero, Inventario y Clientas")
st.write(
    "Control total: inventario sincronizado, ventas, compras detalladas y"
    " notificaciones por WhatsApp."
)

# Definir las columnas oficiales exactas
COLUMNAS_VENTAS = [
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

COLUMNAS_COMPRAS = [
    "Fecha",
    "Proveedor / Detalle",
    "Cantidad",
    "Inversión Total ($)",
]

COLUMNAS_INVENTARIO = [
    "Producto",
    "Categoría",
    "Stock Actual",
    "Precio Venta Sugerido ($)",
]

# Inicializar o reparar bases de datos en la sesión si faltan columnas
if "compras" not in st.session_state:
    st.session_state.compras = pd.DataFrame(columns=COLUMNAS_COMPRAS)

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=COLUMNAS_VENTAS)
else:
    for col in COLUMNAS_VENTAS:
        if col not in st.session_state.ventas.columns:
            if (
                col == "Total Venta ($)"
                and "Precio Venta ($)" in st.session_state.ventas.columns
            ):
                st.session_state.ventas.rename(
                    columns={"Precio Venta ($)": "Total Venta ($)"},
                    inplace=True,
                )
            else:
                st.session_state.ventas[col] = 0.0 if "($)" in col else ""

if "clientas" not in st.session_state:
    st.session_state.clientas = pd.DataFrame(columns=["Cliente", "Teléfono"])

if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame(columns=COLUMNAS_INVENTARIO)

# --- MENÚ LATERAL: GESTIÓN Y REGISTROS ---
st.sidebar.header("📝 Menú de Gestión")

menu_opcion = st.sidebar.selectbox(
    "¿Qué deseas hacer?",
    [
        "Registrar Venta o Promoción",
        "📦 Control de Inventario (Entradas/Salidas)",
        "✏️ Editar Venta o Abonar Saldo",
        "Crear / Registrar Nueva Clienta",
        "Registrar Compra / Inversión Global",
        "🗑️ Eliminar Compra Equivocada",
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
    st.sidebar.subheader("📦 Inversión y Entrada a Inventario")
    fecha_compra = st.sidebar.date_input("Fecha de Compra")
    detalle_compra = st.sidebar.text_input(
        "Nombre del Producto o Detalle",
        placeholder="Ej. Bolso Crossbody Negro",
    )
    cantidad_comprada = st.sidebar.number_input(
        "Cantidad Comprada", min_value=1, value=5, step=1
    )
    total_inversion = st.sidebar.number_input(
        "Costo Total de la Compra ($)",
        min_value=0.0,
        value=200000.0,
        step=10000.0,
    )

    if st.sidebar.button("Guardar Compra y Actualizar Stock"):
        if not detalle_compra:
            st.sidebar.error("⚠️ Por favor, ingresa el detalle del producto.")
        else:
            # 1. Registrar en la tabla de compras
            nueva_compra = pd.DataFrame(
                [[fecha_compra, detalle_compra, cantidad_comprada, total_inversion]],
                columns=COLUMNAS_COMPRAS,
            )
            st.session_state.compras = pd.concat(
                [st.session_state.compras, nueva_compra], ignore_index=True
            )
            st.session_state.compras = st.session_state.compras.sort_values(
                by="Fecha", ascending=False
            )

            # 2. Actualizar Inventario Automáticamente (Suma stock)
            if (
                not st.session_state.inventario.empty
                and detalle_compra
                in st.session_state.inventario["Producto"].values
            ):
                idx_p = st.session_state.inventario.index[
                    st.session_state.inventario["Producto"] == detalle_compra
                ][0]
                st.session_state.inventario.loc[idx_p, "Stock Actual"] += (
                    cantidad_comprada
                )
            else:
                precio_sug_def = (
                    total_inversion / cantidad_comprada
                ) * 1.5  # Margen sugerido
                nuevo_prod = pd.DataFrame(
                    [[detalle_compra, "General", cantidad_comprada, precio_sug_def]],
                    columns=COLUMNAS_INVENTARIO,
                )
                st.session_state.inventario = pd.concat(
                    [st.session_state.inventario, nuevo_prod], ignore_index=True
                )

            st.sidebar.success(
                "¡Compra guardada y stock actualizado con éxito!"
            )

elif menu_opcion == "📦 Control de Inventario (Entradas/Salidas)":
    st.sidebar.subheader("📦 Gestión de Stock")
    tipo_inv = st.sidebar.radio(
        "Operación",
        [
            "Nuevo Producto / Registrar Entrada",
            "Registrar Salida / Venta de Stock",
        ],
    )

    if tipo_inv == "Nuevo Producto / Registrar Entrada":
        prod_nombre = st.sidebar.text_input(
            "Nombre del Producto", placeholder="Ej. Bolso Crossbody Negro"
        )
        prod_cat = st.sidebar.selectbox(
            "Categoría", ["Bolsos 👜", "Zapatos 👠", "Accesorios ✨", "Otros"]
        )
        cantidad_inc = st.sidebar.number_input(
            "Cantidad que ingresa", min_value=1, value=5, step=1
        )
        precio_sug = st.sidebar.number_input(
            "Precio de Venta Sugerido ($)",
            min_value=0.0,
            value=60000.0,
            step=1000.0,
        )

        if st.sidebar.button("Guardar Entrada en Inventario"):
            if not prod_nombre:
                st.sidebar.error("⚠️ Ingresa el nombre del producto.")
            else:
                if (
                    not st.session_state.inventario.empty
                    and prod_nombre
                    in st.session_state.inventario["Producto"].values
                ):
                    idx_p = st.session_state.inventario.index[
                        st.session_state.inventario["Producto"] == prod_nombre
                    ][0]
                    st.session_state.inventario.loc[idx_p, "Stock Actual"] += (
                        cantidad_inc
                    )
                    st.session_state.inventario.loc[
                        idx_p, "Precio Venta Sugerido ($)"
                    ] = precio_sug
                    st.sidebar.success(
                        f"¡Stock actualizado! Se sumaron {cantidad_inc} unidades"
                        f" a `{prod_nombre}`."
                    )
                else:
                    nuevo_prod = pd.DataFrame(
                        [[prod_nombre, prod_cat, cantidad_inc, precio_sug]],
                        columns=COLUMNAS_INVENTARIO,
                    )
                    st.session_state.inventario = pd.concat(
                        [st.session_state.inventario, nuevo_prod],
                        ignore_index=True,
                    )
                    st.sidebar.success(
                        f"¡Nuevo producto `{prod_nombre}` registrado con"
                        f" éxito!"
                    )

    else:
        if st.session_state.inventario.empty:
            st.sidebar.warning(
                "No hay productos en el inventario para descontar."
            )
        else:
            prod_lista = list(st.session_state.inventario["Producto"].unique())
            prod_salida = st.sidebar.selectbox(
                "Seleccionar Producto", prod_lista
            )
            stock_actual = int(
                st.session_state.inventario.loc[
                    st.session_state.inventario["Producto"] == prod_salida,
                    "Stock Actual",
                ].values[0]
            )
            st.sidebar.info(f"📦 Stock disponible actual: `{stock_actual}`")

            cant_salida = st.sidebar.number_input(
                "Cantidad a retirar / vender",
                min_value=1,
                max_value=max(1, stock_actual),
                value=1,
                step=1,
            )

            if st.sidebar.button("Registrar Salida de Stock"):
                idx_p = st.session_state.inventario.index[
                    st.session_state.inventario["Producto"] == prod_salida
                ][0]
                if cant_salida > stock_actual:
                    st.sidebar.error("⚠️ No hay suficiente stock disponible.")
                else:
                    st.session_state.inventario.loc[
                        idx_p, "Stock Actual"
                    ] -= cant_salida
                    st.sidebar.success(
                        f"¡Salida registrada! Se descontaron {cant_salida}"
                        f" unidades de `{prod_salida}`."
                    )
                    st.rerun()

elif menu_opcion == "🗑️ Eliminar Compra Equivocada":
    st.sidebar.subheader("🗑️ Eliminar Compra")
    if st.session_state.compras.empty:
        st.sidebar.warning("No hay compras registradas para eliminar.")
    else:
        opciones_compras = []
        for idx, row in st.session_state.compras.iterrows():
            opciones_compras.append(
                f"{idx}: [{row['Fecha']}] {row['Proveedor / Detalle']} (Cant: {row['Cantidad']}) - ${row['Inversión Total ($)']}"
            )

        compra_a_borrar_str = st.sidebar.selectbox(
            "Selecciona la compra a eliminar", opciones_compras
        )
        idx_borrar = int(compra_a_borrar_str.split(":")[0])

        if st.sidebar.button("Eliminar Compra Seleccionada"):
            prod_afectado = st.session_state.compras.loc[
                idx_borrar, "Proveedor / Detalle"
            ]
            cant_afectada = int(
                st.session_state.compras.loc[idx_borrar, "Cantidad"]
            )

            if (
                not st.session_state.inventario.empty
                and prod_afectado
                in st.session_state.inventario["Producto"].values
            ):
                idx_p = st.session_state.inventario.index[
                    st.session_state.inventario["Producto"] == prod_afectado
                ][0]
                st.session_state.inventario.loc[idx_p, "Stock Actual"] = max(
                    0,
                    st.session_state.inventario.loc[idx_p, "Stock Actual"]
                    - cant_afectada,
                )

            st.session_state.compras = st.session_state.compras.drop(
                idx_borrar
            ).reset_index(drop=True)
            st.sidebar.success("¡Compra eliminada y stock descontado!")
            st.rerun()

elif menu_opcion == "✏️ Editar Venta o Abonar Saldo":
    st.sidebar.subheader("✏️ Editar Registro de Venta")
    if st.session_state.ventas.empty:
        st.sidebar.warning("No hay ventas registradas para editar.")
    else:
        opciones_ventas = []
        for idx, row in st.session_state.ventas.iterrows():
            opciones_ventas.append(
                f"{idx}: {row['Cliente']} - {row['Descripción']} (${row['Total Venta ($)']})"
            )

        venta_seleccionada_str = st.sidebar.selectbox(
            "Selecciona la venta a modificar", opciones_ventas
        )
        idx_edit = int(venta_seleccionada_str.split(":")[0])

        reg_actual = st.session_state.ventas.loc[idx_edit]

        nuevo_total = st.sidebar.number_input(
            "Total Venta ($)",
            min_value=0.0,
            value=float(reg_actual["Total Venta ($)"]),
            step=1000.0,
        )
        nuevo_abono = st.sidebar.number_input(
            "Abono Actualizado ($)",
            min_value=0.0,
            value=float(reg_actual["Abono ($)"]),
            step=1000.0,
        )

        nuevo_credito = max(0.0, nuevo_total - nuevo_abono)
        st.sidebar.info(f"📉 Nuevo Crédito Pendiente: ${nuevo_credito:,.2f}")

        if nuevo_credito == 0:
            nuevo_estado = "Pagado Completo 🟢"
        elif nuevo_abono > 0:
            nuevo_estado = "Abono / Parcial 🟡"
        else:
            nuevo_estado = "Crédito Pendiente 🔴"

        st.sidebar.write(f"**Nuevo Estado:** {nuevo_estado}")

        if st.sidebar.button("Actualizar Venta"):
            st.session_state.ventas.loc[idx_edit, "Total Venta ($)"] = (
                nuevo_total
            )
            st.session_state.ventas.loc[idx_edit, "Abono ($)"] = nuevo_abono
            st.session_state.ventas.loc[idx_edit, "Crédito Pendiente ($)"] = (
                nuevo_credito
            )
            st.session_state.ventas.loc[idx_edit, "Estado"] = nuevo_estado
            st.sidebar.success("¡Venta actualizada con éxito!")
            st.rerun()

else:  # Registrar Venta o Promoción
    st.sidebar.subheader("🛍️ Venta o Mensaje a Clienta")
    tipo_movimiento = st.sidebar.selectbox(
        "Acción", ["Venta / Aviso de Pago", "Promoción de Temporada"]
    )
    fecha_venta = st.sidebar.date_input("Fecha")

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
            "💡 No tienes clientas guardadas aún. Puedes agregarlas en la opción"
            " 'Crear / Registrar Nueva Clienta'."
        )
        cliente = st.sidebar.text_input(
            "Nombre de la Clienta", placeholder="Ej. Ana Gómez"
        )
        telefono = st.sidebar.text_input("Teléfono", placeholder="573001234567")

    if tipo_movimiento == "Venta / Aviso de Pago":
        descripcion = st.sidebar.text_input(
            "Detalle del Producto Vendido",
            placeholder="Ej. Bolso Crossbody Negro",
        )
        cantidad_vendida = st.sidebar.number_input(
            "Cantidad Vendida", min_value=1, value=1, step=1
        )
        total_venta = st.sidebar.number_input(
            "Total Venta ($)", min_value=0.0, value=50000.0, step=1000.0
        )
        abono = st.sidebar.number_input(
            "Abono Realizado ($)", min_value=0.0, value=50000.0, step=1000.0
        )

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
        cantidad_vendida = 0
        total_venta = 0.0
        abono = 0.0
        credito_pendiente = 0.0
        estado = "Promoción 📢"

    if st.sidebar.button("Guardar Venta y Descontar Stock"):
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
                columns=COLUMNAS_VENTAS,
            )
            st.session_state.ventas = pd.concat(
                [st.session_state.ventas, nueva_venta], ignore_index=True
            )
            st.session_state.ventas = st.session_state.ventas.sort_values(
                by="Fecha", ascending=False
            )

            # Descontar stock automáticamente
            if tipo_movimiento == "Venta / Aviso de Pago" and cantidad_vendida > 0:
                if (
                    not st.session_state.inventario.empty
                    and descripcion
                    in st.session_state.inventario["Producto"].values
                ):
                    idx_p = st.session_state.inventario.index[
                        st.session_state.inventario["Producto"] == descripcion
                    ][0]
                    st.session_state.inventario.loc[idx_p, "Stock Actual"] = max(
                        0,
                        st.session_state.inventario.loc[idx_p, "Stock Actual"]
                        - cantidad_vendida,
                    )

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

            st.sidebar.success("¡Venta registrada y stock descontado con éxito!")

# --- PANEL PRINCIPAL: RESUMEN Y PESTAÑAS ---
df_compras = st.session_state.compras
df_ventas = st.session_state.ventas
df_clientas = st.session_state.clientas
df_inventario = st.session_state.inventario

total_invertido_compras = (
    df_compras["Inversión Total ($)"].sum() if not df_compras.empty else 0.0
)

if not df_ventas.empty and "Total Venta ($)" in df_ventas.columns:
    df_solo_ventas = df_ventas[df_ventas["Tipo"] == "Venta / Aviso de Pago"]
    total_ingresos_ventas = (
        df_solo_ventas["Total Venta ($)"].sum()
        if not df_solo_ventas.empty
        else 0.0
    )
    total_abonos_recibidos = (
        df_solo_ventas["Abono ($)"].sum() if not df_solo_ventas.empty else 0.0
    )
    total_creditos_pendientes = (
        df_solo_ventas["Crédito Pendiente ($)"].sum()
        if not df_solo_ventas.empty
        else 0.0
    )
else:
    total_ingresos_ventas = 0.0
    total_abonos_recibidos = 0.0
    total_creditos_pendientes = 0.0

# Fórmula de Utilidad: Ventas Totales menos Abonos
utilidad_obtenida = total_ingresos_ventas - total_abonos_recibidos

# Tarjetas de Resumen Financiero Global (5 tarjetas)
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("📦 Inversión Compras", f"${total_invertido_compras:,.2f}")
col_m2.metric("💰 Ventas Totales", f"${total_ingresos_ventas:,.2f}")
col_m3.metric("📥 Abonos Recibidos", f"${total_abonos_recibidos:,.2f}")
col_m4.metric("⚠️ Crédito Pendiente", f"${total_creditos_pendientes:,.2f}")
col_m5.metric("📈 Utilidad Obtenida", f"${utilidad_obtenida:,.2f}")

st.markdown("---")

# Pestañas principales organizadas para mostrar TODO el detalle
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Historial de Ventas y WhatsApp",
    "📦 Control de Inventario (Stock)",
    "👥 Directorio de Clientas",
    "📦 Registro de Compras Detallado",
])

with tab1:
    if not df_ventas.empty:
        st.subheader("📋 Ventas, Abonos y Créditos Ordenados por Fecha")

        for index, row in df_ventas.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])

                c1.markdown(f"**📅 {row['Fecha']}**")
                c1.markdown(f"**👤 {row['Cliente']}**")
                c1.caption(f"📱 Tel: `{row['Teléfono']}`")

                c2.markdown(f"**Estado:** {row['Estado']}")

                if row["Tipo"] == "Venta / Aviso de Pago":
                    c3.markdown(
                        f"**Prod:** {row['Descripción']} <br> **Total:**"
                        f" ${row['Total Venta ($)']:,.2f} <br> **Abono:**"
                        f" ${row['Abono ($)']:,.2f} <br> **Pendiente:**"
                        f" 🔴 ${row['Crédito Pendiente ($)']:,.2f}",
                        unsafe_allow_html=True,
                    )
                else:
                    c3.markdown(f"**Promoción:** {row['Descripción']}")

                if "Pagado Completo" in str(row["Estado"]):
                    texto_msj = (
                        f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store"
                        f" para confirmarte que hemos recibido tu pago total por"
                        f" ${row['Total Venta ($)']:,.2f} correspondiente a:"
                        f" *{row['Descripción']}*. ¡Muchas gracias por tu"
                        " compra!"
                    )
                elif "Abono" in str(row["Estado"]):
                    texto_msj = (
                        f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store"
                        f" para confirmarte tu abono de ${row['Abono ($)']:,.2f}."
                        f" El total de tu compra es ${row['Total Venta ($)']:,.2f}"
                        f" y te queda un saldo pendiente de"
                        f" ${row['Crédito Pendiente ($)']:,.2f} por:"
                        f" *{row['Descripción']}*. ¡Gracias!"
                    )
                elif "Promoción" in str(row["Estado"]):
                    texto_msj = row["Descripción"]
                else:
                    texto_msj = (
                        f"¡Hola {row['Cliente']}! 👜 Te escribo de GreisyNu Store"
                        f" para recordarte que tienes un saldo pendiente de"
                        f" ${row['Crédito Pendiente ($)']:,.2f} por tu compra"
                        f" de: *{row['Descripción']}*."
                    )

                mensaje_codificado = urllib.parse.quote(texto_msj)
                link_wsp = (
                    f"https://wa.me/{row['Teléfono']}?text={mensaje_codificado}"
                )

                c4.markdown(
                    f"[💬 Enviar a WhatsApp]({link_wsp})", unsafe_allow_html=True
                )
                st.
