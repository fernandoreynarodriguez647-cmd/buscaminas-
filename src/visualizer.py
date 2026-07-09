import matplotlib.pyplot as plt
import networkx as nx

COLORS = ['#4A90D9', '#50C878', '#E74C3C', '#F39C12', '#9B59B6',
          '#1ABC9C', '#E91E63', '#00BCD4', '#FF5722', '#8BC34A']


def dibujar_grafo(grafo, componentes=None, mostrar=True, titulo='Grafo de restricciones del Buscaminas'):
    from src.graph_analysis import metricas_grafo, obtener_componentes
    if grafo.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Grafo vacío — sin casillas frontera',
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        if mostrar:
            plt.show()
        return fig
    pos = nx.spring_layout(grafo, seed=42, k=2.5, iterations=50)
    fig, ax = plt.subplots(figsize=(10, 8))
    if componentes is None:
        componentes = obtener_componentes(grafo)
    for i, comp in enumerate(componentes):
        color = COLORS[i % len(COLORS)]
        nx.draw_networkx_nodes(
            grafo, pos,
            nodelist=list(comp),
            node_color=color,
            node_size=[300 + 100 * grafo.degree(n) for n in comp],
            label=f'Componente {i+1} ({len(comp)} nodos)',
            ax=ax,
            edgecolors='black',
            linewidths=0.5
        )
    nx.draw_networkx_edges(grafo, pos, alpha=0.4, ax=ax, width=1.5)
    nx.draw_networkx_labels(grafo, pos, font_size=7, ax=ax)
    met = metricas_grafo(grafo)
    info = (f'Nodos: {met["nodos"]} | Aristas: {met["aristas"]} | '
            f'Componentes: {met["componentes"]} | Densidad: {met["densidad"]:.3f}')
    ax.set_title(f'{titulo}\n{info}', fontsize=10)
    ax.legend(fontsize=7, loc='upper right')
    ax.axis('off')
    fig.tight_layout()
    if mostrar:
        plt.show()
    return fig


def dibujar_grafo_comparativa(grafo_humano, componentes_h, grafo_bot, componentes_b):
    from src.graph_analysis import metricas_grafo
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    for ax, grafo, comps, titulo in [
        (ax1, grafo_humano, componentes_h, 'Humano'),
        (ax2, grafo_bot, componentes_b, 'Bot')
    ]:
        if grafo.number_of_nodes() == 0:
            ax.text(0.5, 0.5, 'Grafo vacío', ha='center', va='center', fontsize=12)
            ax.axis('off')
            continue
        pos = nx.spring_layout(grafo, seed=42, k=2.0, iterations=50)
        for i, comp in enumerate(comps):
            nx.draw_networkx_nodes(
                grafo, pos,
                nodelist=list(comp),
                node_color=COLORS[i % len(COLORS)],
                node_size=400,
                label=f'Comp {i+1}',
                ax=ax
            )
        nx.draw_networkx_edges(grafo, pos, alpha=0.3, ax=ax)
        nx.draw_networkx_labels(grafo, pos, font_size=6, ax=ax)
        met = metricas_grafo(grafo)
        ax.set_title(f'{titulo} — {met["nodos"]} nodos, {met["aristas"]} aristas, {met["componentes"]} comps')
        ax.axis('off')
    fig.tight_layout()
    return fig
