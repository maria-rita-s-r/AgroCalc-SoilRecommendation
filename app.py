from flask import Flask, render_template, request, redirect, url_for, flash
# Importa do seu arquivo bancoDB.py
from bancoDB import conectar_banco, criar_banco_de_dados

app = Flask(__name__)
app.secret_key = "calculadora-agricola-secret-key"

# Inicializa o banco ao iniciar o aplicativo
criar_banco_de_dados()

@app.route("/")
def index():
    return render_template("index.html")

# --- PRODUTORES ---
@app.route("/produtores")
def produtores():
    conexao = conectar_banco()
    produtores = conexao.execute("SELECT * FROM produtores ORDER BY nome").fetchall()
    conexao.close()
    return render_template("produtores.html", produtores=produtores)

@app.route("/produtores/novo", methods=["GET", "POST"])
def novo_produtor():
    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")

        if not nome:
            flash("O nome do produtor é obrigatório.")
            return redirect(url_for("novo_produtor"))

        conexao = conectar_banco()
        conexao.execute("INSERT INTO produtores (nome, telefone) VALUES (?, ?)", (nome, telefone))
        conexao.commit()
        conexao.close()

        flash("Produtor cadastrado com sucesso!")
        return redirect(url_for("produtores"))

    return render_template("produtor_form.html")

@app.route("/produtores/editar/<int:id>", methods=["GET", "POST"])
def editar_produtor(id):
    conexao = conectar_banco()
    produtor = conexao.execute("SELECT * FROM produtores WHERE id = ?", (id,)).fetchone()

    if not produtor:
        conexao.close()
        flash("Produtor não encontrado.")
        return redirect(url_for("produtores"))

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")

        if not nome:
            conexao.close()
            flash("O nome do produtor é obrigatório.")
            return redirect(url_for("editar_produtor", id=id))

        conexao.execute("UPDATE produtores SET nome = ?, telefone = ? WHERE id = ?", (nome, telefone, id))
        conexao.commit()
        conexao.close()

        flash("Produtor atualizado com sucesso!")
        return redirect(url_for("produtores"))

    conexao.close()
    return render_template("produtor_form.html", produtor=produtor)

@app.route("/produtores/excluir/<int:id>", methods=["POST"])
def excluir_produtor(id):
    conexao = conectar_banco()
    conexao.execute("DELETE FROM produtores WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    flash("Produtor excluído com sucesso.")
    return redirect(url_for("produtores"))

# --- PROPRIEDADES ---
@app.route("/propriedades")
def propriedades():
    conexao = conectar_banco()
    propriedades = conexao.execute("""
        SELECT propriedades.*, produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores ON propriedades.produtor_id = produtores.id
        ORDER BY propriedades.nome_propriedade
    """).fetchall()
    conexao.close()
    return render_template("propriedades.html", propriedades=propriedades)

@app.route("/propriedades/nova", methods=["GET", "POST"])
def nova_propriedade():
    conexao = conectar_banco()
    produtores = conexao.execute("SELECT * FROM produtores ORDER BY nome").fetchall()

    if request.method == "POST":
        produtor_id = request.form.get("produtor_id")
        nome_propriedade = request.form.get("nome_propriedade")
        municipio = request.form.get("municipio")
        estado = request.form.get("estado")

        if not produtor_id or not nome_propriedade:
            conexao.close()
            flash("Produtor e propriedade são obrigatórios.")
            return redirect(url_for("nova_propriedade"))

        conexao.execute("""
            INSERT INTO propriedades (produtor_id, nome_propriedade, municipio, estado)
            VALUES (?, ?, ?, ?)
        """, (produtor_id, nome_propriedade, municipio, estado))
        conexao.commit()
        conexao.close()

        flash("Propriedade cadastrada com sucesso!")
        return redirect(url_for("propriedades"))

    conexao.close()
    return render_template("propriedade_form.html", produtores=produtores)

@app.route("/propriedades/editar/<int:id>", methods=["GET", "POST"])
def editar_propriedade(id):
    conexao = conectar_banco()
    propriedade = conexao.execute("SELECT * FROM propriedades WHERE id = ?", (id,)).fetchone()

    if not propriedade:
        conexao.close()
        flash("Propriedade não encontrada.")
        return redirect(url_for("propriedades"))

    if request.method == "POST":
        produtor_id = request.form.get("produtor_id")
        nome_propriedade = request.form.get("nome_propriedade")
        municipio = request.form.get("municipio")
        estado = request.form.get("estado")

        if not produtor_id or not nome_propriedade:
            conexao.close()
            flash("Produtor e propriedade são obrigatórios.")
            return redirect(url_for("editar_propriedade", id=id))

        conexao.execute("""
            UPDATE propriedades
            SET produtor_id = ?, nome_propriedade = ?, municipio = ?, estado = ?
            WHERE id = ?
        """, (produtor_id, nome_propriedade, municipio, estado, id))
        conexao.commit()
        conexao.close()

        flash("Propriedade atualizada com sucesso!")
        return redirect(url_for("propriedades"))

    produtores = conexao.execute("SELECT * FROM produtores ORDER BY nome").fetchall()
    conexao.close()
    return render_template("propriedade_form.html", propriedade=propriedade, produtores=produtores)

@app.route("/propriedades/excluir/<int:id>", methods=["POST"])
def excluir_propriedade(id):
    conexao = conectar_banco()
    conexao.execute("DELETE FROM propriedades WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    flash("Propriedade excluída com sucesso.")
    return redirect(url_for("propriedades"))

# --- TALHÕES ---
@app.route("/talhoes")
def talhoes():
    conexao = conectar_banco()
    talhoes = conexao.execute("""
        SELECT talhoes.*, propriedades.nome_propriedade, produtores.nome AS produtor_nome
        FROM talhoes
        INNER JOIN propriedades ON talhoes.propriedade_id = propriedades.id
        INNER JOIN produtores ON propriedades.produtor_id = produtores.id
        ORDER BY talhoes.nome_talhao
    """).fetchall()
    conexao.close()
    return render_template("talhoes.html", talhoes=talhoes)

@app.route("/talhoes/novo", methods=["GET", "POST"])
def novo_talhao():
    conexao = conectar_banco()
    propriedades = conexao.execute("""
        SELECT propriedades.id, propriedades.nome_propriedade, produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores ON propriedades.produtor_id = produtores.id
        ORDER BY propriedades.nome_propriedade
    """).fetchall()

    if request.method == "POST":
        propriedade_id = request.form.get("propriedade_id")
        nome_talhao = request.form.get("nome_talhao")
        area_ha = request.form.get("area_ha")

        try:
            area_ha = float(area_ha)
        except (ValueError, TypeError):
            conexao.close()
            flash("Informe uma área válida.")
            return redirect(url_for("novo_talhao"))

        if not propriedade_id or not nome_talhao:
            conexao.close()
            flash("Preencha todos os campos obrigatórios.")
            return redirect(url_for("novo_talhao"))

        conexao.execute("""
            INSERT INTO talhoes (propriedade_id, nome_talhao, area_ha)
            VALUES (?, ?, ?)
        """, (propriedade_id, nome_talhao, area_ha))
        conexao.commit()
        conexao.close()

        flash("Talhão cadastrado com sucesso!")
        return redirect(url_for("talhoes"))

    conexao.close()
    return render_template("talhao_form.html", propriedades=propriedades)

@app.route("/talhoes/editar/<int:id>", methods=["GET", "POST"])
def editar_talhao(id):
    conexao = conectar_banco()
    talhao = conexao.execute("SELECT * FROM talhoes WHERE id = ?", (id,)).fetchone()

    if not talhao:
        conexao.close()
        flash("Talhão não encontrado.")
        return redirect(url_for("talhoes"))

    if request.method == "POST":
        propriedade_id = request.form.get("propriedade_id")
        nome_talhao = request.form.get("nome_talhao")
        area_ha = request.form.get("area_ha")

        try:
            area_ha = float(area_ha)
        except (ValueError, TypeError):
            conexao.close()
            flash("Informe uma área válida.")
            return redirect(url_for("editar_talhao", id=id))

        if not propriedade_id or not nome_talhao:
            conexao.close()
            flash("Preencha todos os campos obrigatórios.")
            return redirect(url_for("editar_talhao", id=id))

        conexao.execute("""
            UPDATE talhoes
            SET propriedade_id = ?, nome_talhao = ?, area_ha = ?
            WHERE id = ?
        """, (propriedade_id, nome_talhao, area_ha, id))
        conexao.commit()
        conexao.close()

        flash("Talhão atualizado com sucesso!")
        return redirect(url_for("talhoes"))

    propriedades = conexao.execute("""
        SELECT propriedades.id, propriedades.nome_propriedade, produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores ON propriedades.produtor_id = produtores.id
        ORDER BY propriedades.nome_propriedade
    """).fetchall()
    conexao.close()
    return render_template("talhao_form.html", talhao=talhao, propriedades=propriedades)

@app.route("/talhoes/excluir/<int:id>", methods=["POST"])
def excluir_talhao(id):
    conexao = conectar_banco()
    conexao.execute("DELETE FROM talhoes WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    flash("Talhão excluído com sucesso.")
    return redirect(url_for("talhoes"))

# --- CULTURAS ---
@app.route("/culturas")
def culturas():
    conexao = conectar_banco()
    culturas = conexao.execute("SELECT * FROM culturas ORDER BY nome_cultura").fetchall()
    conexao.close()
    return render_template("culturas.html", culturas=culturas)

@app.route("/culturas/nova", methods=["GET", "POST"])
def nova_cultura():
    if request.method == "POST":
        nome_cultura = request.form.get("nome_cultura")
        v2_alvo = request.form.get("v2_alvo")

        try:
            v2_alvo = float(v2_alvo)
        except (ValueError, TypeError):
            flash("Informe um V2 alvo válido.")
            return redirect(url_for("nova_cultura"))

        if not nome_cultura:
            flash("Informe o nome da cultura.")
            return redirect(url_for("nova_cultura"))

        conexao = conectar_banco()
        conexao.execute("INSERT INTO culturas (nome_cultura, v2_alvo) VALUES (?, ?)", (nome_cultura, v2_alvo))
        conexao.commit()
        conexao.close()

        flash("Cultura cadastrada com sucesso!")
        return redirect(url_for("culturas"))

    return render_template("cultura_form.html")

# --- CALCÁRIOS ---
@app.route("/calcarios")
def calcarios():
    conexao = conectar_banco()
    calcarios = conexao.execute("SELECT * FROM corretivos_calcario ORDER BY nome_comercial").fetchall()
    conexao.close()
    return render_template("calcarios.html", calcarios=calcarios)

@app.route("/calcarios/novo", methods=["GET", "POST"])
def novo_calcario():
    if request.method == "POST":
        nome_comercial = request.form.get("nome_comercial")
        prnt = request.form.get("prnt_porcento")

        try:
            prnt = float(prnt)
        except (ValueError, TypeError):
            flash("Informe um PRNT válido.")
            return redirect(url_for("novo_calcario"))

        if not nome_comercial:
            flash("Informe o nome comercial.")
            return redirect(url_for("novo_calcario"))

        conexao = conectar_banco()
        conexao.execute("INSERT INTO corretivos_calcario (nome_comercial, prnt_porcento) VALUES (?, ?)", (nome_comercial, prnt))
        conexao.commit()
        conexao.close()

        flash("Calcário cadastrado com sucesso!")
        return redirect(url_for("calcarios"))

    return render_template("calcario_form.html")

# --- FERTILIZANTES ---
@app.route("/fertilizantes")
def fertilizantes():
    conexao = conectar_banco()
    fertilizantes = conexao.execute("SELECT * FROM fertilizantes ORDER BY nome_comercial").fetchall()
    conexao.close()
    return render_template("fertilizantes.html", fertilizantes=fertilizantes)

@app.route("/fertilizantes/novo", methods=["GET", "POST"])
def novo_fertilizante():
    if request.method == "POST":
        nome_comercial = request.form.get("nome_comercial")
        teor_n = float(request.form.get("teor_n") or 0)
        teor_p2o5 = float(request.form.get("teor_p2o5") or 0)
        teor_k2o = float(request.form.get("teor_k2o") or 0)

        if not nome_comercial:
            flash("Informe o nome comercial.")
            return redirect(url_for("novo_fertilizante"))

        conexao = conectar_banco()
        conexao.execute("""
            INSERT INTO fertilizantes (nome_comercial, teor_n, teor_p2o5, teor_k2o)
            VALUES (?, ?, ?, ?)
        """, (nome_comercial, teor_n, teor_p2o5, teor_k2o))
        conexao.commit()
        conexao.close()

        flash("Fertilizante cadastrado com sucesso!")
        return redirect(url_for("fertilizantes"))

    return render_template("fertilizante_form.html")

# --- MÓDULO DE SOLO ---
@app.route("/solo/calculadora")
def calculadora_solo():
    conexao = conectar_banco()
    talhoes = conexao.execute("""
        SELECT talhoes.id, talhoes.nome_talhao, talhoes.area_ha, propriedades.nome_propriedade
        FROM talhoes
        INNER JOIN propriedades ON talhoes.propriedade_id = propriedades.id
        ORDER BY talhoes.nome_talhao
    """).fetchall()
    culturas = conexao.execute("SELECT * FROM culturas ORDER BY nome_cultura").fetchall()
    conexao.close()
    return render_template("solo/calculadora.html", talhoes=talhoes, culturas=culturas)

@app.route("/solo/formulario")
def formulario_solo():
    talhao_id = request.args.get("talhao_id") or request.args.get("talhao id")
    cultura_id = request.args.get("cultura_id") or request.args.get("cultura id")

    if not talhao_id or not cultura_id:
        flash("Selecione o talhão e a cultura.")
        return redirect(url_for("calculadora_solo"))

    conexao = conectar_banco()
    talhao = conexao.execute("""
        SELECT talhoes.*, propriedades.nome_propriedade, produtores.nome AS produtor_nome
        FROM talhoes
        INNER JOIN propriedades ON talhoes.propriedade_id = propriedades.id
        INNER JOIN produtores ON propriedades.produtor_id = produtores.id
        WHERE talhoes.id = ?
    """, (talhao_id,)).fetchone()

    cultura = conexao.execute("SELECT * FROM culturas WHERE id = ?", (cultura_id,)).fetchone()
    conexao.close()

    if not talhao or not cultura:
        flash("Dados não encontrados.")
        return redirect(url_for("calculadora_solo"))

    return render_template("solo/formulario.html", talhao=talhao, cultura=cultura)

@app.route("/solo/calcular", methods=["POST"])
def calcular_solo():
    talhao_id = request.form.get("talhao_id")
    cultura_id = request.form.get("cultura_id")
    data_coleta = request.form.get("data_coleta")

    campos = ["ph", "v1_atual", "ctc_t", "ca", "mg", "k", "p", "h_al", "argila"]
    valores = {}

    try:
        for campo in campos:
            valor = request.form.get(campo)
            valores[campo] = float(valor) if valor and valor.strip() != "" else None
    except ValueError:
        flash("Verifique os valores informados. Utilize apenas números.")
        return redirect(url_for("formulario_solo", talhao_id=talhao_id, cultura_id=cultura_id))

    if valores["ph"] is None or valores["v1_atual"] is None or valores["ctc_t"] is None:
        flash("Os campos pH, V1 atual e CTC T são obrigatórios.")
        return redirect(url_for("formulario_solo", talhao_id=talhao_id, cultura_id=cultura_id))

    conexao = conectar_banco()
    cultura = conexao.execute("SELECT * FROM culturas WHERE id = ?", (cultura_id,)).fetchone()
    talhao = conexao.execute("SELECT * FROM talhoes WHERE id = ?", (talhao_id,)).fetchone()
    calcario = conexao.execute("SELECT * FROM corretivos_calcario ORDER BY id DESC LIMIT 1").fetchone()

    if not cultura or not talhao:
        conexao.close()
        flash("Talhão ou cultura não encontrados.")
        return redirect(url_for("calculadora_solo"))

    v2_alvo = cultura["v2_alvo"]
    v1_atual = valores["v1_atual"]
    ctc = valores["ctc_t"]
    prnt = calcario["prnt_porcento"] if (calcario and calcario["prnt_porcento"] > 0) else 100.0
    calcario_id = calcario["id"] if calcario else None
    area_ha = talhao["area_ha"]

    # NC = ((V2 - V1) * CTC) / 100
    nc_ha = max(0.0, ((v2_alvo - v1_atual) * ctc) / 100.0)
    dose_calcario_ha = nc_ha * (100.0 / prnt)
    total_talhao = dose_calcario_ha * area_ha

    cursor = conexao.execute("""
        INSERT INTO recomendacoes_solo (
            talhao_id, cultura_id, calcario_id, data_coleta,
            ph, v1_atual, ctc_t, ca, mg, k, p, h_al, argila,
            nc_ha, dose_calcario_ha, total_calcario_talhao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        talhao_id, cultura_id, calcario_id, data_coleta,
        valores["ph"], valores["v1_atual"], valores["ctc_t"],
        valores["ca"], valores["mg"], valores["k"], valores["p"],
        valores["h_al"], valores["argila"],
        nc_ha, dose_calcario_ha, total_talhao
    ))

    recomendacao_id = cursor.lastrowid
    conexao.commit()
    conexao.close()

    return redirect(url_for("resultado_solo", recomendacao_id=recomendacao_id))

@app.route("/solo/resultado/<int:recomendacao_id>")
def resultado_solo(recomendacao_id):
    conexao = conectar_banco()
    recomendacao = conexao.execute("""
        SELECT r.*, t.nome_talhao, t.area_ha, c.nome_cultura, p.nome_propriedade, 
               prod.nome AS produtor_nome, cc.nome_comercial
        FROM recomendacoes_solo r
        JOIN talhoes t ON r.talhao_id = t.id
        JOIN propriedades p ON t.propriedade_id = p.id
        JOIN produtores prod ON p.produtor_id = prod.id
        JOIN culturas c ON r.cultura_id = c.id
        LEFT JOIN corretivos_calcario cc ON r.calcario_id = cc.id
        WHERE r.id = ?
    """, (recomendacao_id,)).fetchone()
    conexao.close()

    if not recomendacao:
        flash("Recomendação não encontrada.")
        return redirect(url_for("calculadora_solo"))

    return render_template("solo/resultado.html", recomendacao=recomendacao)

@app.route("/solo/recomendacoes")
def recomendacoes_solo():
    conexao = conectar_banco()
    recomendacoes = conexao.execute("""
        SELECT r.*, t.nome_talhao, c.nome_cultura, p.nome_propriedade, 
               prod.nome AS produtor_nome, cc.nome_comercial
        FROM recomendacoes_solo r
        JOIN talhoes t ON r.talhao_id = t.id
        JOIN propriedades p ON t.propriedade_id = p.id
        JOIN produtores prod ON p.produtor_id = prod.id
        JOIN culturas c ON r.cultura_id = c.id
        LEFT JOIN corretivos_calcario cc ON r.calcario_id = cc.id
        ORDER BY r.id DESC
    """).fetchall()
    conexao.close()
    return render_template("solo/recomendacaos.html", recomendacoes=recomendacoes)

@app.route("/solo/documento/<int:recomendacao_id>")
def documento_solo(recomendacao_id):
    conexao = conectar_banco()
    documento = conexao.execute("""
        SELECT r.*, t.nome_talhao, t.area_ha, c.nome_cultura, p.nome_propriedade, 
               p.municipio, p.estado, prod.nome AS produtor_nome, prod.telefone, cc.nome_comercial
        FROM recomendacoes_solo r
        JOIN talhoes t ON r.talhao_id = t.id
        JOIN propriedades p ON t.propriedade_id = p.id
        JOIN produtores prod ON p.produtor_id = prod.id
        JOIN culturas c ON r.cultura_id = c.id
        LEFT JOIN corretivos_calcario cc ON r.calcario_id = cc.id
        WHERE r.id = ?
    """, (recomendacao_id,)).fetchone()
    conexao.close()

    if not documento:
        flash("Documento não encontrado.")
        return redirect(url_for("recomendacoes_solo"))

    return render_template("solo/documentacao.html", documento=documento)

if __name__ == "__main__":
    app.run(debug=True)