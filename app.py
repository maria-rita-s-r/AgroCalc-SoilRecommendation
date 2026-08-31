from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3


app = Flask(__name__)

app.secret_key = "calculadora-agricola-secret-key"

DATABASE = "calculadora_agricola.db"


# ============================================================
# CONEXÃO COM O BANCO
# ============================================================

def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


# ============================================================
# INÍCIO
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# PRODUTORES
# ============================================================

@app.route("/produtores")
def produtores():

    conexao = conectar_banco()

    produtores = conexao.execute("""
        SELECT *
        FROM produtores
        ORDER BY nome
    """).fetchall()

    conexao.close()

    return render_template(
        "produtores.html",
        produtores=produtores
    )


@app.route("/produtores/novo", methods=["GET", "POST"])
def novo_produtor():

    if request.method == "POST":

        nome = request.form.get("nome")
        telefone = request.form.get("telefone")

        if not nome:
            flash("O nome do produtor é obrigatório.")
            return redirect(url_for("novo_produtor"))

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO produtores
            (nome, telefone)
            VALUES (?, ?)
        """, (nome, telefone))

        conexao.commit()
        conexao.close()

        flash("Produtor cadastrado com sucesso!")

        return redirect(url_for("produtores"))

    return render_template("produtor_form.html")


@app.route("/produtores/excluir/<int:id>", methods=["POST"])
def excluir_produtor(id):

    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM produtores
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    flash("Produtor excluído com sucesso.")

    return redirect(url_for("produtores"))


# ============================================================
# PROPRIEDADES
# ============================================================

@app.route("/propriedades")
def propriedades():

    conexao = conectar_banco()

    propriedades = conexao.execute("""
        SELECT
            propriedades.*,
            produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id
        ORDER BY propriedades.nome_propriedade
    """).fetchall()

    conexao.close()

    return render_template(
        "propriedades.html",
        propriedades=propriedades
    )


@app.route("/propriedades/nova", methods=["GET", "POST"])
def nova_propriedade():

    conexao = conectar_banco()

    produtores = conexao.execute("""
        SELECT *
        FROM produtores
        ORDER BY nome
    """).fetchall()

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
            INSERT INTO propriedades
            (
                produtor_id,
                nome_propriedade,
                municipio,
                estado
            )
            VALUES (?, ?, ?, ?)
        """, (
            produtor_id,
            nome_propriedade,
            municipio,
            estado
        ))

        conexao.commit()
        conexao.close()

        flash("Propriedade cadastrada com sucesso!")

        return redirect(url_for("propriedades"))

    conexao.close()

    return render_template(
        "propriedade_form.html",
        produtores=produtores
    )


@app.route("/propriedades/excluir/<int:id>", methods=["POST"])
def excluir_propriedade(id):

    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM propriedades
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    flash("Propriedade excluída com sucesso.")

    return redirect(url_for("propriedades"))


# ============================================================
# TALHÕES
# ============================================================

@app.route("/talhoes")
def talhoes():

    conexao = conectar_banco()

    talhoes = conexao.execute("""
        SELECT
            talhoes.*,
            propriedades.nome_propriedade,
            produtores.nome AS produtor_nome
        FROM talhoes
        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id
        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id
        ORDER BY talhoes.nome_talhao
    """).fetchall()

    conexao.close()

    return render_template(
        "talhoes.html",
        talhoes=talhoes
    )


@app.route("/talhoes/novo", methods=["GET", "POST"])
def novo_talhao():

    conexao = conectar_banco()

    propriedades = conexao.execute("""
        SELECT
            propriedades.id,
            propriedades.nome_propriedade,
            produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id
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
            INSERT INTO talhoes
            (
                propriedade_id,
                nome_talhao,
                area_ha
            )
            VALUES (?, ?, ?)
        """, (
            propriedade_id,
            nome_talhao,
            area_ha
        ))

        conexao.commit()
        conexao.close()

        flash("Talhão cadastrado com sucesso!")

        return redirect(url_for("talhoes"))

    conexao.close()

    return render_template(
        "talhao_form.html",
        propriedades=propriedades
    )


@app.route("/talhoes/excluir/<int:id>", methods=["POST"])
def excluir_talhao(id):

    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM talhoes
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    flash("Talhão excluído com sucesso.")

    return redirect(url_for("talhoes"))


# ============================================================
# CULTURAS
# ============================================================

@app.route("/culturas")
def culturas():

    conexao = conectar_banco()

    culturas = conexao.execute("""
        SELECT *
        FROM culturas
        ORDER BY nome_cultura
    """).fetchall()

    conexao.close()

    return render_template(
        "culturas.html",
        culturas=culturas
    )


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

        conexao.execute("""
            INSERT INTO culturas
            (
                nome_cultura,
                v2_alvo
            )
            VALUES (?, ?)
        """, (
            nome_cultura,
            v2_alvo
        ))

        conexao.commit()
        conexao.close()

        flash("Cultura cadastrada com sucesso!")

        return redirect(url_for("culturas"))

    return render_template("cultura_form.html")


# ============================================================
# CALCÁRIOS
# ============================================================

@app.route("/calcarios")
def calcarios():

    conexao = conectar_banco()

    calcarios = conexao.execute("""
        SELECT *
        FROM corretivos_calcario
        ORDER BY nome_comercial
    """).fetchall()

    conexao.close()

    return render_template(
        "calcarios.html",
        calcarios=calcarios
    )


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

        conexao.execute("""
            INSERT INTO corretivos_calcario
            (
                nome_comercial,
                prnt_porcento
            )
            VALUES (?, ?)
        """, (
            nome_comercial,
            prnt
        ))

        conexao.commit()
        conexao.close()

        flash("Calcário cadastrado com sucesso!")

        return redirect(url_for("calcarios"))

    return render_template("calcario_form.html")


# ============================================================
# FERTILIZANTES
# ============================================================

@app.route("/fertilizantes")
def fertilizantes():

    conexao = conectar_banco()

    fertilizantes = conexao.execute("""
        SELECT *
        FROM fertilizantes
        ORDER BY nome_comercial
    """).fetchall()

    conexao.close()

    return render_template(
        "fertilizantes.html",
        fertilizantes=fertilizantes
    )


@app.route("/fertilizantes/novo", methods=["GET", "POST"])
def novo_fertilizante():

    if request.method == "POST":

        nome_comercial = request.form.get("nome_comercial")

        teor_n = request.form.get("teor_n") or 0
        teor_p2o5 = request.form.get("teor_p2o5") or 0
        teor_k2o = request.form.get("teor_k2o") or 0

        try:

            teor_n = float(teor_n)
            teor_p2o5 = float(teor_p2o5)
            teor_k2o = float(teor_k2o)

        except ValueError:

            flash("Os teores devem ser números.")

            return redirect(
                url_for("novo_fertilizante")
            )

        if not nome_comercial:

            flash("Informe o nome comercial.")

            return redirect(
                url_for("novo_fertilizante")
            )

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO fertilizantes
            (
                nome_comercial,
                teor_n,
                teor_p2o5,
                teor_k2o
            )
            VALUES (?, ?, ?, ?)
        """, (
            nome_comercial,
            teor_n,
            teor_p2o5,
            teor_k2o
        ))

        conexao.commit()
        conexao.close()

        flash(
            "Fertilizante cadastrado com sucesso!"
        )

        return redirect(
            url_for("fertilizantes")
        )

    return render_template(
        "fertilizante_form.html"
    )


# ============================================================
# CALCULADORA DE SOLO
# ============================================================

@app.route("/solo/calculadora")
def calculadora_solo():

    conexao = conectar_banco()

    talhoes = conexao.execute("""
        SELECT
            talhoes.id,
            talhoes.nome_talhao,
            talhoes.area_ha,
            propriedades.nome_propriedade
        FROM talhoes
        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id
        ORDER BY talhoes.nome_talhao
    """).fetchall()

    culturas = conexao.execute("""
        SELECT *
        FROM culturas
        ORDER BY nome_cultura
    """).fetchall()

    conexao.close()

    return render_template(
        "solo/calculadora.html",
        talhoes=talhoes,
        culturas=culturas
    )


# ============================================================
# FORMULÁRIO DO LAUDO
# ============================================================

@app.route("/solo/formulario")
def formulario_solo():

    talhao_id = request.args.get("talhao_id")
    cultura_id = request.args.get("cultura_id")

    if not talhao_id or not cultura_id:

        flash(
            "Selecione o talhão e a cultura."
        )

        return redirect(
            url_for("calculadora_solo")
        )

    conexao = conectar_banco()

    talhao = conexao.execute("""
        SELECT
            talhoes.*,
            propriedades.nome_propriedade,
            produtores.nome AS produtor_nome
        FROM talhoes
        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id
        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id
        WHERE talhoes.id = ?
    """, (
        talhao_id,
    )).fetchone()

    cultura = conexao.execute("""
        SELECT *
        FROM culturas
        WHERE id = ?
    """, (
        cultura_id,
    )).fetchone()

    conexao.close()

    if not talhao or not cultura:

        flash("Dados não encontrados.")

        return redirect(
            url_for("calculadora_solo")
        )

    return render_template(
        "solo/formulario.html",
        talhao=talhao,
        cultura=cultura
    )


# ============================================================
# PROCESSAR CÁLCULO
# ============================================================

@app.route("/solo/calcular", methods=["POST"])
def calcular_solo():

    talhao_id = request.form.get("talhao_id")
    cultura_id = request.form.get("cultura_id")

    data_coleta = request.form.get("data_coleta")

    campos = [
        "ph",
        "v1_atual",
        "ctc_t",
        "ca",
        "mg",
        "k",
        "p",
        "h_al",
        "argila"
    ]

    valores = {}

    try:

        for campo in campos:

            valor = request.form.get(campo)

            if valor:
                valores[campo] = float(valor)
            else:
                valores[campo] = None

    except ValueError:

        flash(
            "Verifique os valores informados."
        )

        return redirect(
            url_for(
                "formulario_solo",
                talhao_id=talhao_id,
                cultura_id=cultura_id
            )
        )

    if valores["ph"] is None:
        flash("O pH é obrigatório.")

        return redirect(
            url_for(
                "formulario_solo",
                talhao_id=talhao_id,
                cultura_id=cultura_id
            )
        )

    if valores["v1_atual"] is None:
        flash("A V1 atual é obrigatória.")

        return redirect(
            url_for(
                "formulario_solo",
                talhao_id=talhao_id,
                cultura_id=cultura_id
            )
        )

    if valores["ctc_t"] is None:
        flash("A CTC T é obrigatória.")

        return redirect(
            url_for(
                "formulario_solo",
                talhao_id=talhao_id,
                cultura_id=cultura_id
            )
        )

    conexao = conectar_banco()

    cultura = conexao.execute("""
        SELECT *
        FROM culturas
        WHERE id = ?
    """, (
        cultura_id,
    )).fetchone()

    talhao = conexao.execute("""
        SELECT
            talhoes.*,
            propriedades.nome_propriedade
        FROM talhoes
        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id
        WHERE talhoes.id = ?
    """, (
        talhao_id,
    )).fetchone()

    if not cultura or not talhao:

        conexao.close()

        flash("Cultura ou talhão não encontrados.")

        return redirect(
            url_for("calculadora_solo")
        )

    # ========================================================
    # NECESSIDADE DE CALCÁRIO
    # ========================================================

    v2_alvo = cultura["v2_alvo"]

    nc_ha = (
        valores["ctc_t"] *
        (v2_alvo - valores["v1_atual"])
    ) / 100

    if nc_ha < 0:
        nc_ha = 0

    # ========================================================
    # CALCÁRIO
    # ========================================================

    calcario = conexao.execute("""
        SELECT *
        FROM corretivos_calcario
        ORDER BY id
        LIMIT 1
    """).fetchone()

    if not calcario:

        conexao.close()

        flash(
            "Cadastre pelo menos um calcário antes de realizar o cálculo."
        )

        return redirect(
            url_for("calculadora_solo")
        )

    prnt = calcario["prnt_porcento"]

    if prnt > 0:

        dose_calcario_ha = (
            nc_ha * 100
        ) / prnt

    else:

        dose_calcario_ha = nc_ha

    total_calcario_talhao = (
        dose_calcario_ha *
        talhao["area_ha"]
    )

    # ========================================================
    # RECOMENDAÇÃO DE FERTILIZANTES
    # ========================================================
    #
    # Será implementada de acordo com a metodologia
    # agronômica adotada no projeto.
    #

    dose_n_ha = None
    dose_p2o5_ha = None
    dose_k2o_ha = None

    # ========================================================
    # SALVAR LAUDO
    # ========================================================

    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO laudos_solo
        (
            talhao_id,
            data_coleta,
            ph,
            v1_atual,
            ctc_t,
            ca,
            mg,
            k,
            p,
            h_al,
            argila
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        talhao_id,
        data_coleta,
        valores["ph"],
        valores["v1_atual"],
        valores["ctc_t"],
        valores["ca"],
        valores["mg"],
        valores["k"],
        valores["p"],
        valores["h_al"],
        valores["argila"]
    ))

    laudo_id = cursor.lastrowid

    # ========================================================
    # SALVAR RECOMENDAÇÃO
    # ========================================================

    cursor.execute("""
        INSERT INTO recomendacoes
        (
            laudo_id,
            cultura_id,
            calcario_id,
            nc_ha,
            dose_calcario_ha,
            total_calcario_talhao,
            dose_n_ha,
            dose_p2o5_ha,
            dose_k2o_ha
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        laudo_id,
        cultura_id,
        calcario["id"],
        nc_ha,
        dose_calcario_ha,
        total_calcario_talhao,
        dose_n_ha,
        dose_p2o5_ha,
        dose_k2o_ha
    ))

    recomendacao_id = cursor.lastrowid

    conexao.commit()
    conexao.close()

    return redirect(
        url_for(
            "resultado_solo",
            recomendacao_id=recomendacao_id
        )
    )


# ============================================================
# RESULTADO
# ============================================================

@app.route("/solo/resultado/<int:recomendacao_id>")
def resultado_solo(recomendacao_id):

    conexao = conectar_banco()

    recomendacao = conexao.execute("""
        SELECT
            recomendacoes.*,

            culturas.nome_cultura,

            corretivos_calcario.nome_comercial,

            laudos_solo.ph,
            laudos_solo.v1_atual,
            laudos_solo.ctc_t,

            talhoes.nome_talhao,
            talhoes.area_ha

        FROM recomendacoes

        INNER JOIN culturas
            ON recomendacoes.cultura_id = culturas.id

        INNER JOIN corretivos_calcario
            ON recomendacoes.calcario_id = corretivos_calcario.id

        INNER JOIN laudos_solo
            ON recomendacoes.laudo_id = laudos_solo.id

        INNER JOIN talhoes
            ON laudos_solo.talhao_id = talhoes.id

        WHERE recomendacoes.id = ?
    """, (
        recomendacao_id,
    )).fetchone()

    conexao.close()

    if not recomendacao:

        flash("Recomendação não encontrada.")

        return redirect(
            url_for("recomendacoes_solo")
        )

    return render_template(
        "solo/resultado.html",
        recomendacao=recomendacao
    )


# ============================================================
# ADMINISTRAÇÃO / RECOMENDAÇÕES
# ============================================================

@app.route("/solo/recomendacoes")
def recomendacoes_solo():

    conexao = conectar_banco()

    recomendacoes = conexao.execute("""
        SELECT
            recomendacoes.*,

            culturas.nome_cultura,

            corretivos_calcario.nome_comercial,

            laudos_solo.data_coleta,

            talhoes.nome_talhao,

            propriedades.nome_propriedade,

            produtores.nome AS produtor_nome

        FROM recomendacoes

        INNER JOIN culturas
            ON recomendacoes.cultura_id = culturas.id

        INNER JOIN corretivos_calcario
            ON recomendacoes.calcario_id = corretivos_calcario.id

        INNER JOIN laudos_solo
            ON recomendacoes.laudo_id = laudos_solo.id

        INNER JOIN talhoes
            ON laudos_solo.talhao_id = talhoes.id

        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id

        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id

        ORDER BY recomendacoes.data_calculo DESC
    """).fetchall()

    conexao.close()

    return render_template(
        "solo/recomendacoes.html",
        recomendacoes=recomendacoes
    )


# ============================================================
# DOCUMENTAÇÃO
# ============================================================

@app.route("/solo/documento/<int:recomendacao_id>")
def documento_solo(recomendacao_id):

    conexao = conectar_banco()

    documento = conexao.execute("""
        SELECT

            recomendacoes.*,

            culturas.nome_cultura,

            corretivos_calcario.nome_comercial,

            laudos_solo.data_coleta,
            laudos_solo.ph,
            laudos_solo.v1_atual,
            laudos_solo.ctc_t,
            laudos_solo.ca,
            laudos_solo.mg,
            laudos_solo.k,
            laudos_solo.p,
            laudos_solo.h_al,
            laudos_solo.argila,

            talhoes.nome_talhao,
            talhoes.area_ha,

            propriedades.nome_propriedade,
            propriedades.municipio,
            propriedades.estado,

            produtores.nome AS produtor_nome,
            produtores.telefone

        FROM recomendacoes

        INNER JOIN culturas
            ON recomendacoes.cultura_id = culturas.id

        INNER JOIN corretivos_calcario
            ON recomendacoes.calcario_id = corretivos_calcario.id

        INNER JOIN laudos_solo
            ON recomendacoes.laudo_id = laudos_solo.id

        INNER JOIN talhoes
            ON laudos_solo.talhao_id = talhoes.id

        INNER JOIN propriedades
            ON talhoes.propriedade_id = propriedades.id

        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id

        WHERE recomendacoes.id = ?
    """, (
        recomendacao_id,
    )).fetchone()

    conexao.close()

    if not documento:

        flash("Documento não encontrado.")

        return redirect(
            url_for("recomendacoes_solo")
        )

    return render_template(
        "solo/documentacao.html",
        documento=documento
    )


# ============================================================
# EXECUTAR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)