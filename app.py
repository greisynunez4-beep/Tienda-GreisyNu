import os
import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y Clientas",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero, Inventario y Utilidad Real")
st.write(
    "Control absoluto de inventario, ventas, abonos, cuentas por cobrar y"
    " utilidad (Ventas Totales - Compras)."
)

# Definir archivos de persistencia local
ARCH_VENTAS = "ventas.csv"
ARCH_COMPRAS = "compras.csv"
ARCH_CLIENTAS = "clientas.csv"
ARCH_INVENTARIO = "inventario.csv"

COLUMNAS_VENTAS = [
    "Fecha",
    "Cliente",
    "Teléfono",
    "Tipo",
    "Descripción",
    "Cantidad",
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


# Funciones para cargar y guardar datos sin que se borren
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            # Asegurar que todas las columnas existan
            for col in columnas:
                if col not in df.columns:
                    df[col] = (
                        0.0 if "($)" in col else (1 if col == "Cantidad" else "")
                    )
            return df
        except Exception:
            return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)


def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)


# Cargar bases de datos desde los archivos CSV locales
if "ventas" not in st.session_state:
    st.session_state.ventas = cargar_datos(ARCH_VENTAS, COLUMNAS_VENTAS)

if "compras" not in st.session_state:
    st.session_state.compras = cargar_datos(ARCH_COMPRAS, COLUMNAS_COMPRAS)

if "clientas" not in st.session_state:
    st.session_state.clientas = cargar_datos(ARCH_CLIENTAS, ["Cliente", "Teléfono"])

if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_datos(
        ARCH_INVENTARIO, COLUMNAS_INVENTARIO
    )

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
                    columns=["Cliente", "Teléfono"],
                )
                st.session_state.clientas = pd.concat(
                    [st.session_state.clientas, df_nueva], ignore_index=True
                )
                guardar_datos(st.session_state.clientas, ARCH_CLIENTAS)
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
            nueva_compra = pd.DataFrame(
                [[str(fecha_compra), detalle_compra, cantidad_comprada, total_inversion]],
                columns=COLUMNAS_COMPRAS,
            )
            st.session_state.compras = pd.concat(
                [st.session_state.compras, nueva_compra], ignore_index=True
            )
            st.session_state.compras = st.session_state.compras.sort_values(
                by="Fecha", ascending=False
            )
            guardar_datos(st.session_state.compras, ARCH_COMPRAS)

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
                precio_sug_def = (total_inversion / cantidad_comprada) * 1.5
                nuevo_prod = pd.DataFrame(
                    [[detalle_compra, "General", cantidad_comprada, precio_sug_def]],
                    columns=COLUMNAS_INVENTARIO,
                )
                st.session_state.inventario = pd.concat(
                    [st.session_state.inventario, nuevo_prod], ignore_index=True
                )

            guardar_datos(st.session_state.inventario, ARCH_INVENTARIO)
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
                else:
                    nuevo_prod = pd.DataFrame(
                        [[prod_nombre, prod_cat, cantidad_inc, precio_sug]],
                        columns=COLUMNAS_INVENTARIO,
                    )
                    st.session_state.inventario = pd.concat(
                        [st.session_state.inventario, nuevo_prod],
                        ignore_index=True,
                    )

                guardar_datos(st.session_state.inventario, ARCH_INVENTARIO)
                st.sidebar.success(
                    f"¡Stock actualizado para `{prod_nombre}`!"
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
                "Cantidad a retirar",
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
                    guardar_datos(st.session_state.inventario, ARCH_INVENTARIO)
                    st.sidebar.success("¡Salida registrada con éxito!")
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
                guardar_datos(st.session_state.inventario, ARCH_INVENTARIO)

            st.session_state.compras = st.session_state.compras.drop(
                idx_borrar
            ).reset_index(drop=True)
            guardar_datos(st.session_state.compras, ARCH_COMPRAS)
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
            guardar_datos(st.session_state.ventas, ARCH_VENTAS)
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
        if st.session_state.inventario.empty:
            st.sidebar.warning(
                "⚠️ No tienes productos en el inventario. Agrega productos"
                " primero en 'Control de Inventario'."
            )
            descripcion = st.sidebar.text_input(
                "Detalle del Producto", placeholder="Ej. Bolso"
            )
            cantidad_vendida = st.sidebar.number_input(
                "Cantidad", min_value=1, value=1
            )
            total_venta = st.sidebar.number_input(
                "Total Venta ($)", min_value=0.0, value=50000.0, step=1000.0
            )
        else:
            lista_prods = list(st.session_state.inventario["Producto"].unique())
            producto_elegido = st.sidebar.selectbox(
                "Seleccionar Producto del Inventario", lista_prods
            )

            fila_prod = st.session_state.inventario.loc[
                st.session_state.inventario["Producto"] == producto_elegido
            ].iloc[0]
            stock_disp = int(fila_prod["Stock Actual"])
            precio_sug = float(fila_prod["Precio Venta Sugerido ($)"])

            st.sidebar.info(
                f"📦 Stock Disponible: **{stock_disp}** | 💲 Precio Sugerido:"
                f" **${precio_sug:,.2f}**"
            )

            descripcion = producto_elegido
            cantidad_vendida = st.sidebar.number_input(
                "Cantidad a Vender",
                min_value=1,
                max_value=max(1, stock_disp),
                value=1,
                step=1,
            )
            total_venta = st.sidebar.number_input(
                "Total Venta ($)",
                min_value=0.0,
                value=float(precio_sug * cantidad_vendida),
                step=1000.0,
            )

        abono = st.sidebar.number_input(
            "Abono Realizado por la Clienta ($)",
            min_value=0.0,
            value=float(total_venta),
            step=1000.0,
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
                    str(fecha_venta),
                    cliente,
                    telefono,
                    tipo_movimiento,
                    descripcion,
                    cantidad_vendida,
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
            guardar_datos(st.session_state.ventas, ARCH_VENTAS)

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
                    guardar_datos(st.session_state.inventario, ARCH_INVENTARIO)

            if (
                st.session_state.clientas.empty
                or cliente not in st.session_state.clientas["Cliente"].values
            ):
                nueva_cli = pd.DataFrame(
                    [[cliente, telefono]],
                    columns=["Cliente", "Teléfono"],
                )
                st.session_state.clientas = pd.concat(
                    [st.session_state.clientas, nueva_cli], ignore_index=True
                )
                guardar_datos(st.session_state.clientas, ARCH_CLIENTAS)

            st.sidebar.success("¡Venta registrada y guardada con éxito!")

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

utilidad_obtenida = total_ingresos_ventas - total_invertido_compras

# Tarjetas de Resumen Financiero Global (5 tarjetas)
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("📦 Inversión Compras", f"${total_invertido_compras:,.2f}")
col_m2.metric("💰 Ventas Totales", f"${total_ingresos_ventas:,.2f}")
col_m3.metric("📥 Abonos Recibidos", f"${total_abonos_recibidos:,.2f}")
col_m4.metric("⚠️ Crédito Pendiente", f"${total_creditos_pendientes:,.2f}")
col_m5.metric("📈 Utilidad Obtenida", f"${utilidad_obtenida:,.2f}")

st.markdown("---")

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Historial de Ventas y WhatsApp",
    "💳 Cuentas por Cobrar",
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
                        f"**Prod:** {row['Descripción']} (Cant:"
                        f" {row.get('Cantidad', 1)}) <br> **Total:**"
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
                st.markdown("---")

        if st.button("🗑️ Borrar Historial de Ventas"):
            st.session_state.ventas = pd.DataFrame(columns=COLUMNAS_VENTAS)
            guardar_datos(st.session_state.ventas, ARCH_VENTAS)
            st.rerun()
    else:
        st.info("Aún no hay registros de ventas o mensajes.")

with tab2:
    st.subheader("💳 Cuentas por Cobrar Pendientes por Clienta")
