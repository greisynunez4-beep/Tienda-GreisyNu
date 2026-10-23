import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="GreisyNu Store - Control y Clientas",
    page_icon="👜",
    layout="wide",
)

st.title("👜 GreisyNu Store: Control Financiero, Inventario Sincronizado y Clientas")
st.write(
    "Tus compras y ventas actualizan el inventario automáticamente. Edita"
    " abonos, controla créditos y notifica por WhatsApp."
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
        "📦 Ajuste Manual de Inventario",
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
                ) * 1.5  # Sugiere 50% margen
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

elif menu_opcion == "📦 Ajuste Manual de Inventario":
    st.sidebar.subheader("📦 Ajustar Stock Manualmente")
    if st.session_state.inventario.empty:
        st.sidebar.warning("No hay productos en el inventario para ajustar.")
    else:
        prod_lista = list(st.session_state.inventario["Producto"].unique())
        prod_sel = st.sidebar.selectbox("Seleccionar Producto", prod_lista)
        stock_actual = int(
            st.session_state.inventario.loc[
                st.session_state.inventario["Producto"] == prod_sel,
                "Stock Actual",
            ].values[0]
        )
        st.sidebar.info(f"📦 Stock actual: `{stock_actual}`")

        nuevo_stock = st.sidebar.number_input(
            "Nuevo Stock Total",
            min_value=0,
            value=stock_actual,
            step=1,
        )

        if st.sidebar.button("Actualizar Stock Manual"):
            idx_p = st.session_state.inventario.index[
                st.session_state.inventario["Producto"] == prod_sel
            ][0]
            st.session_state.inventario.loc[idx_p, "Stock Actual"] = nuevo_stock
            st.sidebar.success("¡Inventario ajustado correctamente!")
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
            # Opcional: Descontar del inventario lo que se había sumado
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
        st.sidebar.info
