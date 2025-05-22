from shiny import App, ui, render, reactive
import re
import unicodedata

# Utilitário para IDs válidos
def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]", "", text)
    return text.lower()

# Catálogo fixo
produtos = {
    "Alimentos": {"Arroz": 5.50, "Feijão": 6.00, "Pão": 7.00},
    "Bebidas": {"Leite": 4.20, "Suco": 6.50, "Refrigerante": 8.00},
    "Limpeza": {"Detergente": 3.50, "Desinfetante": 4.90, "Sabão em Pó": 10.00}
}

# Estilo customizado
estilo = ui.tags.style("""
    body {
        background-color: #121212;
        color: #f0f0f0;
        font-family: 'Segoe UI', sans-serif;
        margin: 0;
        padding: 0;
    }
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
    }
    .card {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: scale(1.02);
    }
    .card h4 {
        color: #ffffff;
        font-size: 20px;
        margin-bottom: 10px;
    }
    .card p {
        color: #cccccc;
        font-size: 16px;
        margin-bottom: 12px;
    }
    .btn-success {
        background-color: #28a745;
        border: none;
        color: white;
        font-weight: bold;
        padding: 8px 14px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .btn-success:hover {
        background-color: #218838;
    }
    .btn-warning {
        background-color: #ffc107;
        color: black;
        font-weight: bold;
        padding: 8px 14px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        margin-right: 10px;
        transition: background-color 0.3s ease;
    }
    .btn-warning:hover {
        background-color: #e0a800;
    }
    .table {
        width: 100%;
        margin-top: 16px;
        background-color: #1a1a1a;
        border-collapse: collapse;
    }
    .table th, .table td {
        padding: 12px 16px;
        border: 1px solid #333;
        text-align: left;
    }
    .table th {
        background-color: #2a2a2a;
        color: #f0f0f0;
    }
    .table-striped tr:nth-child(even) {
        background-color: #2a2a2a;
    }
    .total-container {
        background-color: #1a1a1a;
        padding: 16px;
        margin-top: 20px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
    }
""")

app_ui = ui.page_fluid(
    estilo,
    ui.tags.div({"style": "display: flex;"},
        # Área principal com as abas
        ui.tags.div({"style": "flex: 3; padding-right: 20px;"},
            ui.h2("🛒 Supermercado Virtual", style="margin-bottom: 20px;"),
            ui.navset_tab(
                ui.nav_panel("Alimentos", ui.output_ui("ui_alimentos")),
                ui.nav_panel("Bebidas", ui.output_ui("ui_bebidas")),
                ui.nav_panel("Limpeza", ui.output_ui("ui_limpeza"))
            ),
            ui.hr(),
            ui.tags.div({"style": "margin-top: 20px; display: flex; gap: 10px;"},
                ui.input_action_button("limpar_btn", "🧹 Limpar Carrinho", class_="btn-warning"),
                ui.input_action_button("finalizar_btn", "📦 Finalizar Compra", class_="btn-success")
            ),
            ui.output_ui("recibo_ui")
        ),
        # Resumo lateral fixo
        ui.tags.div({"style": "flex: 1; background-color: #1a1a1a; padding: 20px; border-radius: 12px;"},
            ui.h4("🧺 Carrinho"),
            ui.output_ui("carrinho_ui"),
            ui.tags.div({"class": "total-container"},
                ui.h4("💰 Total:"),
                ui.output_text("total")
            )
        )
    )
)

def server(input, output, session):
    carrinho = reactive.Value([])
    recibo = reactive.Value(None)
    cliques = {}

    # Produtos - Alimentos
    @output
    @render.ui
    def ui_alimentos():
        cards = []
        for nome, preco in produtos["Alimentos"].items():
            sid = slugify(nome)
            full_id = f"alimentos_{sid}"
            cliques[full_id] = 0
            cards.append(ui.tags.div({"class": "card"},
                ui.tags.h4(nome),
                ui.tags.p(f"Preço: R$ {preco:.2f}"),
                ui.input_numeric(f"qtd_{full_id}", "Quantidade", 1, min=1),
                ui.input_action_button(f"btn_{full_id}", "Adicionar", class_="btn-success")
            ))
        return ui.tags.div({"class": "grid"}, *cards)

    # Produtos - Bebidas
    @output
    @render.ui
    def ui_bebidas():
        cards = []
        for nome, preco in produtos["Bebidas"].items():
            sid = slugify(nome)
            full_id = f"bebidas_{sid}"
            cliques[full_id] = 0
            cards.append(ui.tags.div({"class": "card"},
                ui.tags.h4(nome),
                ui.tags.p(f"Preço: R$ {preco:.2f}"),
                ui.input_numeric(f"qtd_{full_id}", "Quantidade", 1, min=1),
                ui.input_action_button(f"btn_{full_id}", "Adicionar", class_="btn-success")
            ))
        return ui.tags.div({"class": "grid"}, *cards)

    # Produtos - Limpeza
    @output
    @render.ui
    def ui_limpeza():
        cards = []
        for nome, preco in produtos["Limpeza"].items():
            sid = slugify(nome)
            full_id = f"limpeza_{sid}"
            cliques[full_id] = 0
            cards.append(ui.tags.div({"class": "card"},
                ui.tags.h4(nome),
                ui.tags.p(f"Preço: R$ {preco:.2f}"),
                ui.input_numeric(f"qtd_{full_id}", "Quantidade", 1, min=1),
                ui.input_action_button(f"btn_{full_id}", "Adicionar", class_="btn-success")
            ))
        return ui.tags.div({"class": "grid"}, *cards)

    # Monitorar cliques e adicionar ao carrinho
    @reactive.effect
    def monitorar_clicks():
        for categoria, lista in produtos.items():
            for nome in lista:
                sid = slugify(nome)
                id_base = f"{categoria.lower()}_{sid}"
                if input[f"btn_{id_base}"]() > cliques.get(id_base, 0):
                    cliques[id_base] = input[f"btn_{id_base}"]()
                    qtd = input[f"qtd_{id_base}"]()
                    preco = produtos[categoria][nome]
                    subtotal = qtd * preco
                    carrinho.set(carrinho() + [(nome, qtd, preco, subtotal)])
                    recibo.set(None)

    # Carrinho
    @output
    @render.ui
    def carrinho_ui():
        itens = carrinho()
        if not itens:
            return ui.p("Carrinho vazio.")
        linhas = [ui.tags.tr(
            ui.tags.td(prod), ui.tags.td(qtd),
            ui.tags.td(f"R$ {unit:.2f}"), ui.tags.td(f"R$ {sub:.2f}")
        ) for prod, qtd, unit, sub in itens]
        return ui.tags.table(
            {"class": "table table-striped"},
            ui.tags.thead(ui.tags.tr(
                ui.tags.th("Produto"), ui.tags.th("Qtd"),
                ui.tags.th("Preço"), ui.tags.th("Subtotal")
            )),
            ui.tags.tbody(*linhas)
        )

    # Total
    @output
    @render.text
    def total():
        return f"R$ {sum(sub for _, _, _, sub in carrinho()):.2f}"

    # Recibo
    @output
    @render.ui
    def recibo_ui():
        itens = recibo()
        if not itens:
            return ui.p("⬆️ Finalize a compra para gerar o recibo.")
        lista = [ui.tags.li(f"{qtd}x {prod} — R$ {sub:.2f}") for prod, qtd, _, sub in itens]
        total_valor = sum(sub for _, _, _, sub in itens)
        return ui.tags.div(
            ui.h4("🧾 Recibo da Compra"),
            ui.tags.ul(*lista),
            ui.tags.p(f"💵 Total: R$ {total_valor:.2f}", style="font-weight: bold;")
        )

    # Limpar carrinho
    @reactive.effect
    def limpar():
        if input.limpar_btn() > 0:
            carrinho.set([])
            recibo.set(None)

    # Finalizar compra
    @reactive.effect
    def finalizar():
        if input.finalizar_btn() > 0:
            recibo.set(list(carrinho()))

# Inicialização
app = App(app_ui, server)
