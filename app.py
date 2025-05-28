from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime


server = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="1707",
    database="xp_zone"
)
server.secret_key = 'mensagem'

#rota para tela inicial
@server.route('/')
def index():
    return render_template('index.html')

#rota para tela clientes
@server.route('/clientes', methods=['GET', 'POST'])
def clientes():
    cursor = db.cursor(dictionary=True)

    #busca dos dados para a tabela
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    #onde grava os dados no banco
    if request.method == 'POST':
        nome = request.form['inp-cliente']
        estado = request.form['se-estado']

        cursor = db.cursor()

        cursor.execute("INSERT INTO clientes (nome_clientes, estado_clientes) VALUES (%s, %s)", (nome, estado))
        db.commit()
        cursor.close()

        flash("Cliente adicionado com sucesso!") # Mensagem de sucesso
        return redirect('/clientes' )

    return render_template('clientes.html' , clientes=clientes)

@server.route('/delete_cliente/<int:id>')
def delete_cliente(id):
    cursor = db.cursor()

    cursor.execute("DELETE FROM clientes WHERE idclientes = %s", (id,))
    db.commit()
    cursor.close()  

    flash("Cliente excluído com sucesso!")
    return redirect(url_for("clientes"))

#rota para vendedores
@server.route('/vendedores', methods=['GET', 'POST'])
def vendedores():
    cursor = db.cursor(dictionary=True)

    #busca dos dados para a tabela
    cursor.execute("SELECT * FROM vendedores")
    vendedores = cursor.fetchall()

    #onde grava os dados no banco
    if request.method == 'POST':
        nome_vendedor = request.form['inp-vendedor']

        cursor = db.cursor()

        cursor.execute("INSERT INTO vendedores (nome_vendedores) VALUES (%s)", (nome_vendedor,))
        db.commit()
        cursor.close()

        flash("Vendedor adicionado com sucesso!") # Mensagem de sucesso
        return redirect('/vendedores' )

    return render_template('vendedores.html' , vendedores=vendedores)

@server.route('/delete_vendedor/<int:id>')
def delete_vendedor(id):
    cursor = db.cursor()

    cursor.execute("DELETE FROM vendedores WHERE idvendedores = %s", (id,))
    db.commit()
    cursor.close()

    flash("Vendedor excluído com sucesso!")
    return redirect(url_for("vendedores"))

#rota para produtos
@server.route('/produtos', methods=['GET', 'POST'])
def produtos():
    cursor = db.cursor(dictionary=True)

    #busca dos dados para a tabela
    cursor.execute("SELECT * FROM produtos_servicos")
    produtos = cursor.fetchall()

    #onde grava os dados no banco
    if request.method == 'POST':
        nome_produto = request.form['inp-produto']
        valor = request.form['inp-valor']

        cursor = db.cursor()

        cursor.execute("INSERT INTO produtos_servicos (nome_produtos_servicos, valor_produtos_servicos) VALUES (%s, %s)", (nome_produto, valor))
        db.commit()
        cursor.close()

        flash("Produto adicionado com sucesso!")
        return redirect('/produtos' )

    return render_template('produtos.html' , produtos=produtos)

@server.route('/delete_produto/<int:id>')
def delete_produto(id):
    cursor = db.cursor()

    cursor.execute("DELETE FROM produtos_servicos WHERE idprodutos_servicos = %s", (id,))
    db.commit()
    cursor.close()

    flash("Produto excluído com sucesso!")
    return redirect(url_for("produtos"))

#rota para vendas
@server.route('/vendas', methods=['GET', 'POST'])
def vendas():
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT v.*, 
        ps.nome_produtos_servicos, 
        ps.valor_produtos_servicos,
        c.nome_clientes, 
        ve.nome_vendedores
    FROM vendas v
    JOIN produtos_servicos ps ON v.vendas_produtos_servicos = ps.idprodutos_servicos
    JOIN clientes c ON v.vendas_clientes = c.idclientes
    JOIN vendedores ve ON v.vendas_vendedores = ve.idvendedores
"""

    cursor.execute(query)
    vendas = cursor.fetchall()

    # Buscar dados para os selects
    cursor.execute("SELECT * FROM produtos_servicos")
    produtos = cursor.fetchall()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM vendedores")
    vendedores = cursor.fetchall()

    if request.method == 'POST':
        produto_nome = (request.form['inp-produto'])
        cliente_nome = (request.form['inp-cliente'])
        vendedor_nome = (request.form['inp-vendedor'])
        desconto = float(request.form['inp-desconto'])
        data = (request.form['inp-data'])
        departamento = (request.form['se-departamento'])

        data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%Y-%m-%d')


        # Procura o id atraves do nome inserido no input pelo HTML
        cursor.execute("SELECT idprodutos_servicos, valor_produtos_servicos FROM produtos_servicos WHERE nome_produtos_servicos = %s", (produto_nome,))
        produto_row = cursor.fetchone()
        if not produto_row:
            flash("Produto não encontrado.")
            return redirect('/vendas')
        produto_id = produto_row['idprodutos_servicos']

        # Procura o id atraves do nome inserido no input pelo HTML
        cursor.execute("SELECT idclientes FROM clientes WHERE nome_clientes = %s", (cliente_nome,))
        cliente_row = cursor.fetchone()
        if not cliente_row:
            flash("Cliente não encontrado.")
            return redirect('/vendas')
        cliente_id = cliente_row['idclientes']

        # Procura o id atraves do nome inserido no input pelo HTML 
        cursor.execute("SELECT idvendedores FROM vendedores WHERE  nome_vendedores = %s", (vendedor_nome,))
        vendedor_row = cursor.fetchone()
        if not vendedor_row:
            flash("Vendedor não encontrado.")
            return redirect('/vendas')
        vendedor_id = vendedor_row['idvendedores']
        
        valor_produto = float(produto_row['valor_produtos_servicos'])
        valor_final = max(0, valor_produto - desconto)  # Garante que não fique negativo

        # Inserir venda no banco
        cursor.execute("""
            INSERT INTO vendas (vendas_produtos_servicos, vendas_clientes, vendas_vendedores, desconto, valor_final, vendas_departamento, vendas_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (produto_id, cliente_id, vendedor_id, desconto, valor_final, departamento, data_formatada))
        db.commit()
        cursor.close()

        flash("Venda registrada com sucesso!")
        return redirect('/vendas')

    return render_template('vendas.html', produtos=produtos, clientes=clientes, vendedores=vendedores, vendas=vendas)

@server.route('/dashboard')
def dashboard():
    cursor = db.cursor(dictionary=True)

    # Total de vendas
    cursor.execute("SELECT SUM(v.valor_final) AS total FROM vendas v")
    total_vendas = cursor.fetchone()['total'] or 0

    # Vendedor com mais vendas
    cursor.execute("""
        SELECT ve.nome_vendedores, SUM(v.valor_final) AS total_vendido
        FROM vendas v
        JOIN vendedores ve ON v.vendas_vendedores = ve.idvendedores
        GROUP BY ve.nome_vendedores
        ORDER BY total_vendido DESC
        LIMIT 1
    """)
    vendedor_top = cursor.fetchone()
    nome_vendedor = vendedor_top['nome_vendedores'] if vendedor_top else 'Nenhum'
    valor_vendido = vendedor_top['total_vendido'] if vendedor_top else 0

    # Produto mais vendido
    cursor.execute("""
        SELECT ps.nome_produtos_servicos, SUM(v.valor_final) as total 
        FROM vendas v
        JOIN produtos_servicos ps ON v.vendas_produtos_servicos = ps.idprodutos_servicos
        GROUP BY ps.nome_produtos_servicos
        ORDER BY total DESC 
        LIMIT 1
    """)
    produto_top = cursor.fetchone()
    nome_produto = produto_top['nome_produtos_servicos'] if produto_top else 'Nenhum'
    valor_produto = produto_top['total'] if produto_top else 0

    # Estado com mais vendas (assumindo que o campo de estado esteja em clientes)
    cursor.execute("""
        SELECT c.estado_clientes AS estado, SUM(v.valor_final) as total
        FROM vendas v
        JOIN clientes c ON v.vendas_clientes = c.idclientes
        GROUP BY c.estado_clientes
        ORDER BY total DESC
        LIMIT 1
    """)
    estado_top = cursor.fetchone()
    estado = estado_top['estado'] if estado_top else 'Nenhum'
    valor_estado = estado_top['total'] if estado_top else 0

    return render_template(
        'dashboard.html',
        total_vendas=total_vendas,
        nome_vendedor=nome_vendedor,
        valor_vendido=valor_vendido,
        valor_produto=valor_produto,
        nome_produto=nome_produto,
        valor_estado=valor_estado,
        estado=estado
    )

# DASHBOARD

import dash
from dash import html, dcc,Dash
import plotly.express as px
import pandas as pd
import mysql.connector

app = Dash(__name__, server=server, routes_pathname_prefix="/dash/")

#======================= Grafico de pizza vendas por produtos ========================
def gerar_vendas_produtos():
    cursor = db.cursor(dictionary=True)
    query = """ 
        SELECT
            ps.nome_produtos_servicos AS Produtos,
            SUM(v.valor_final)           AS Valor
        FROM vendas v
        JOIN produtos_servicos ps
          ON v.vendas_produtos_servicos = ps.idprodutos_servicos
        GROUP BY ps.nome_produtos_servicos
        ORDER BY Valor DESC
        LIMIT 10
    """
    cursor.execute(query)
    vendas = cursor.fetchall()
    df_vendas = pd.DataFrame(vendas)

    # Para o bar chart horizontal, ordenar de forma ascendente para o maior ficar no topo
    df_vendas = df_vendas.sort_values('Valor', ascending=True)

    fig = px.bar(
        df_vendas,
        x='Valor',
        y='Produtos',
        orientation='h',
        title='Top 10 Produtos por Valor de Vendas',
        template='plotly_white',
        color='Valor',
        color_discrete_sequence=px.colors.sequential.Mint_r
    )

    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>',
        marker_line_width=0.5,
        marker_line_color='white',
        showlegend=False
    )

    fig.update_layout(
        title_font=dict(size=20, family="Poppins", color="#3f3f3f"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#3f3f3f", family="Poppins"),
        margin=dict(l=200, r=15, t=80, b=50),
        xaxis_title="Valor em R$",
        yaxis_title=None
    )

    return fig

#======================= Grafico de vendas por vendedores ========================
def gerar_vendas_vendedores():
    cursor = db.cursor(dictionary=True)
    query = """ 
        SELECT
            ve.nome_vendedores AS Vendedores,
            SUM(v.valor_final) AS Valor
        FROM vendas v
        JOIN vendedores ve ON v.vendas_vendedores = ve.idvendedores
        GROUP BY ve.nome_vendedores
    """
    cursor.execute(query)
    vendas = cursor.fetchall()
    df_vendas = pd.DataFrame(vendas)

    # Monta o gráfico de pizza
    fig = px.pie(
        df_vendas,
        names='Vendedores',
        values='Valor',
        title='Valor total de vendas por vendedor',
        hole=0.4,  # remova ou ajuste para donut/pizza cheia
        color_discrete_sequence=px.colors.sequential.Mint_r,
        template='plotly_white'
    )

    # Remove percentuais, mantém só hover e legend
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>'
    )

    # Layout igual ao anterior
    fig.update_layout(
        title_font=dict(size=20, family="Poppins", color="#3f3f3f"),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#3f3f3f", family="Poppins"),
        margin=dict(l=15, r=15, t=80, b=50),
        legend_title_text=None
    )

    return fig


#============================ Grafico de vendas por departamento =========================

def gerar_vendas_departamento():
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT
            vendas_departamento AS Departamento,
            SUM(valor_final) AS Valor
        FROM vendas
        GROUP BY vendas_departamento
    """
    cursor.execute(query)
    dados = cursor.fetchall()
    df = pd.DataFrame(dados)

    fig = px.pie(
        df, 
        names='Departamento', 
        values='Valor', 
        title='Vendas por Departamento', 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Mint_r,
        template='plotly_white'
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>'
    )
    fig.update_layout(
        title_font=dict(size=20, family="Poppins", color="#3f3f3f"),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#3f3f3f", family="Poppins"),
        margin=dict(l=15, r=15, t=80, b=50),
    )
    return fig

#============================ Grafico de vendas por data =========================

def gerar_vendas_por_data():
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT
            vendas_data AS Data,
            SUM(valor_final) AS Valor
        FROM vendas
        GROUP BY vendas_data
        ORDER BY vendas_data
    """
    cursor.execute(query)
    dados = cursor.fetchall()
    df = pd.DataFrame(dados)

    fig = px.line(
        df,
        x='Data',
        y='Valor',
        title='Vendas por Data',
        markers=True,
        template='plotly_white',
        color_discrete_sequence=px.colors.sequential.Mint_r
    )

    fig.update_traces(
        hovertemplate='Data: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    )

    fig.update_layout(
        title_font=dict(size=20, family="Poppins", color="#3f3f3f"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#3f3f3f", family="Poppins"),
        margin=dict(l=15, r=15, t=80, b=50),
        xaxis_title="Data",
        yaxis_title="Valor em R$"
    )

    return fig


#=========================== Grafico de vendas por Região ==========================

def gerar_mapa_vendas_por_estado():
    import json
    import requests
    import pandas as pd
    import plotly.express as px

    # GeoJSON com nomes dos estados (usaremos siglas com mapeamento)
    url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    geojson_estados = requests.get(url).json()

    # Mapeamento de nomes dos estados para siglas
    estados_siglas = {
        "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
        "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
        "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
        "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
        "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
        "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
        "Sergipe": "SE", "Tocantins": "TO"
    }

    # Adiciona as siglas no GeoJSON
    for feature in geojson_estados["features"]:
        nome_estado = feature["properties"]["name"]
        feature["properties"]["sigla"] = estados_siglas.get(nome_estado, "")

    # Consulta SQL
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT
            c.estado_clientes AS Estado,
            SUM(v.valor_final) AS Valor
        FROM vendas v
        JOIN clientes c ON v.vendas_clientes = c.idclientes
        GROUP BY c.estado_clientes
    """
    cursor.execute(query)
    dados = cursor.fetchall()
    df = pd.DataFrame(dados)
    df['Estado'] = df['Estado'].str.upper().str.strip()
    df_agrupado = df.groupby("Estado", as_index=False)["Valor"].sum()

    # Mapa com todos os estados visíveis
    fig = px.choropleth(
        df_agrupado,
        geojson=geojson_estados,
        locations='Estado',
        featureidkey='properties.sigla',
        color='Estado',
        color_discrete_sequence=px.colors.sequential.Mint_r,
        title='Mapa de Vendas por Estado (UF)',
        range_color=(0, df["Valor"].max() if not df.empty else 1),
        hover_data={'Estado': True, 'Valor': ':,.2f'}
    )

    # Atualizações visuais
    fig.update_geos(
        visible=True,
        fitbounds="geojson",
        showcountries=True,      # mostra divisões dos países
        showcoastlines=True,     # mostra costa
        showland=True,           # mostra massa de terra
        showframe=False,
        projection_type="mercator",  # projeção tradicional
        bgcolor="rgba(0,0,0,0)"
    )


    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font=dict(size=22, family="Poppins", color="#3f3f3f"),
        paper_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",  # cinza claro no fundo
        font=dict(color="#3f3f3f", family="Poppins"),
        coloraxis_colorbar=dict(title="Total de Vendas")
    )

    return fig



#======================= Layout do Dash ========================
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-pizza', figure=gerar_vendas_produtos()),
            dcc.Graph(id='grafico-vendedores', figure=gerar_vendas_vendedores()),
            dcc.Graph(id='grafico-departamento', figure=gerar_vendas_departamento()),
            dcc.Graph(id='grafico-data', figure=gerar_vendas_por_data()),
            dcc.Graph(id='grafico-mapa', figure=gerar_mapa_vendas_por_estado())
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(2, 1fr)",
            "gap": "20px"
        })
    ])
])


#final do codigo
if __name__ == '__main__':
    server.run(debug=True)