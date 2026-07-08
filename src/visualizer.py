import matplotlib.pyplot as plt
import networkx as nx


def dibujar_grafo(grafo, componentes=None, mostrar=True):
    pos = nx.spring_layout(grafo, seed=42)
    fig, ax = plt.subplots(figsize=(8, 6))
    if componentes:
        colores = ['skyblue', 'lightgreen', 'salmon', 'gold', 'plum', 'aquamarine']
        for i, comp in enumerate(componentes):
            nx.draw_networkx_nodes(
                grafo, pos,
                nodelist=list(comp),
                node_color=colores[i % len(colores)],
                node_size=500,
                label=f'Componente {i+1}',
                ax=ax
            )
    else:
        nx.draw_networkx_nodes(grafo, pos, node_color='skyblue', node_size=500, ax=ax)
    nx.draw_networkx_edges(grafo, pos, alpha=0.5, ax=ax)
    nx.draw_networkx_labels(grafo, pos, font_size=8, ax=ax)
    ax.set_title('Grafo de restricciones del Buscaminas')
    ax.legend()
    ax.axis('off')
    if mostrar:
        plt.show()
    return fig
