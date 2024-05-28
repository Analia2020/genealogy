import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from networkx.drawing.nx_pydot import graphviz_layout
import json


# Cargar datos desde el archivo JSON
with open('simpsons.json', 'r') as file:
    simpsons = json.load(file)

# Crear un grafo vacío
G = nx.DiGraph()

# Añadir nodos al grafo
for persona in simpsons:
    G.add_node(persona["dni"], foto=persona["foto"], nombre=persona["nombre"], apellido=persona["apellido"], fecha_nacimiento=persona["fecha_nacimiento"])

# Añadir aristas basadas en relaciones de progenitores
for persona in simpsons:
    if persona["dni_padre"]:
        G.add_edge(persona["dni_padre"], persona["dni"], relacion="padre")
    if persona["dni_madre"]:
        G.add_edge(persona["dni_madre"], persona["dni"], relacion="madre")

# Posicionar nodos en el gráfico usando graphviz_layout de pydot
pos = graphviz_layout(G, prog='dot')

# Función para encontrar el ancestro común más reciente (ACMR)
def encontrar_acmr(grafo, persona1, persona2):
    ancestros1 = nx.ancestors(grafo, persona1)
    ancestros2 = nx.ancestors(grafo, persona2)
    ancestros_comunes = ancestros1.intersection(ancestros2)

    return ancestros_comunes

# Diccionario para convertir entre nombre y DNI
nombre_a_dni = {
    "Homer": "11111111A",
    "Marge": "22222222B",
    "Abraham": "33333333C",
    "Mona": "44444444D",
    "Clancy": "55555555E",
    "Jacqueline": "66666666F",
    "Bart": "77777777G",
    "Lisa": "88888888H",
    "Maggie": "99999999I", 
    "Selma": "24242424B",
    "Paty": "25252525B"
}

# Función para cambiar de DNI a nombre
def cambiar_nombre(dni):
    for nombre, dni_valor in nombre_a_dni.items():
        if dni_valor == dni:
            return nombre
    return None  # Devuelve None si no encuentra el DNI en el diccionario

# Función para recorrer el grafo en profundidad (DFS)
def dfs_recorrido(grafo, nodo_inicio):
    visitados = set()
    recorrido = []

    def dfs(nodo):
        if nodo not in visitados:
            visitados.add(nodo)
            recorrido.append(nodo)
            for vecino in grafo.successors(nodo):  # Obtener sucesores en grafo dirigido
                dfs(vecino)

    dfs(nodo_inicio)
    return recorrido

# Iniciar la aplicación Streamlit
st.title("Genealogía aplicada a la familia Simpsons")
st.markdown("Este es un ejemplo interactivo de genealogía usando Streamlit y NetworkX.")

# Dibujar el grafo en Streamlit
fig, ax = plt.subplots(figsize=(12, 8))

# Dibujar nodos y etiquetas de nombres
nx.draw(G, pos, with_labels=False, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold', ax=ax)
labels = {dni: datos['nombre'] for dni, datos in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black', ax=ax)

# Dibujar aristas
nx.draw_networkx_edges(G, pos, arrows=False, edge_color='black', ax=ax)

# Añadir imágenes a los nodos
for dni, (x, y) in pos.items():
    img_path = G.nodes[dni]['foto']
    img = Image.open(img_path)
    img = img.resize((40, 40), Image.LANCZOS)
    imagebox = AnnotationBbox(OffsetImage(img, zoom=1), (x, y), frameon=False)
    ax.add_artist(imagebox)

# Ajustar los márgenes y el diseño
ax.margins(0.05)
plt.tight_layout()

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

# Operación de Ancestro Común Más Reciente (ACMR)
st.header("Ancestro Común Más Reciente")
st.sidebar.markdown("## Ancestro Común Más Reciente (ACMR)")
persona1_acmr = st.sidebar.selectbox("Selecciona la primera persona:", list(nombre_a_dni.keys()))
persona2_acmr = st.sidebar.selectbox("Selecciona la segunda persona:", list(nombre_a_dni.keys()))

# Convertir nombres a DNIs
dni_persona1_acmr = nombre_a_dni[persona1_acmr]
dni_persona2_acmr = nombre_a_dni[persona2_acmr]

# Calcular ACMR
ancestros_comunes_dni = encontrar_acmr(G, dni_persona1_acmr, dni_persona2_acmr)
ancestros_comunes_nombre = [G.nodes[dni]["nombre"] for dni in ancestros_comunes_dni]

# Mostrar resultado de ACMR en Streamlit
st.subheader("Resultado Ancestro Común Más Reciente - Linea ascendente")
if len(ancestros_comunes_nombre) > 0:
    st.write(f"Los ancestros comunes más recientes entre {persona1_acmr} y {persona2_acmr} son:")
    for nombre in ancestros_comunes_nombre:
        st.write(f"- {nombre}")
else:
    st.write(f"No se encontraron ancestros comunes entre {persona1_acmr} y {persona2_acmr}.")

# Operación de Recorrido DFS
st.header("Linea descendente")
st.sidebar.markdown("## Recorrido DFS")
persona_dfs = st.sidebar.selectbox("Selecciona la persona para recorrido DFS:", list(nombre_a_dni.keys()))

# Convertir nombre a DNI
dni_persona_dfs = nombre_a_dni[persona_dfs]

# Realizar recorrido DFS
recorrido_dfs = dfs_recorrido(G, dni_persona_dfs)
recorrido_dfs_nombres = [G.nodes[dni]["nombre"] for dni in recorrido_dfs]

# Mostrar recorrido DFS en Streamlit
st.subheader("Resultado Recorrido DFS")
if len(recorrido_dfs_nombres) > 0:
    st.write(f"Recorrido DFS desde {persona_dfs}:")
    for nombre in recorrido_dfs_nombres:
        st.write(f"- {nombre}")
else:
    st.write(f"No se encontró ningún recorrido DFS desde {persona_dfs}.")

