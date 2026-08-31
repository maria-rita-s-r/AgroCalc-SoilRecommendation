from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "calculadora_agricola.db"


def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


@app.route("/")
def index():
    conexao = conectar_banco()

    produtores = conexao.execute(
        "SELECT * FROM produtores ORDER BY nome"
    ).fetchall()

    propriedades = conexao.execute(
        "SELECT * FROM propriedades ORDER BY nome_propriedade"
    ).fetchall()

    talhoes = conexao.execute(
        "SELECT * FROM talhoes ORDER BY nome_talhao"
    ).fetchall()

    conexao.close()

    return render_template(
        "index.html",
        produtores=produtores,
        propriedades=propriedades,
        talhoes=talhoes
    )


# =========================================================
# PRODUTORES
# =========================================================

@app.route("/produtores")
def produtores():
    conexao = conectar_banco()

    lista = conexao.execute("""
        SELECT *
        FROM produtores
        ORDER BY nome
    """).fetchall()

    conexao.close()

    return render_template("produtores.html", produtores=lista)


@app.route("/produtores/novo", methods=["GET", "POST"])
def novo_produtor():

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO produtores (nome, telefone)
            VALUES (?, ?)
        """, (nome, telefone))

        conexao.commit()
        conexao.close()

        return redirect(url_for("produtores"))

    return render_template("produtor_form.html")


@app.route("/produtores/excluir/<int:id>")
def excluir_produtor(id):

    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM produtores WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("produtores"))


# =========================================================
# PROPRIEDADES
# =========================================================

@app.route("/propriedades")
def propriedades():

    conexao = conectar_banco()

    lista = conexao.execute("""
        SELECT
            propriedades.id,
            propriedades.nome_propriedade,
            propriedades.municipio,
            propriedades.estado,
            produtores.nome AS produtor_nome
        FROM propriedades
        INNER JOIN produtores
            ON propriedades.produtor_id = produtores.id
        ORDER BY propriedades.nome_propriedade
    """).fetchall()

    conexao.close()

    return render_template(
        "propriedades.html",
        propriedades=lista
    )


@app.route("/propriedades/novo", methods=["GET", "POST"])
def nova_propriedade():

    conexao = conectar_banco()

    produtores = conexao.execute("""
        SELECT *
        FROM produtores
        ORDER BY nome
    """).fetchall()

    if request.method == "POST":

        produtor_id = request.form["produtor_id"]
        nome = request.form["nome_propriedade"]
        municipio = request.form["municipio"]
        estado = request.form["estado"]

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
            nome,
            municipio,
            estado
        ))

        conexao.commit()
        conexao.close()

        return redirect(url_for("propriedades"))

    conexao.close()

    return render_template(
        "propriedade_form.html",
        produtores=produtores
    )


@app.route("/propriedades/excluir/<int:id>")
def excluir_propriedade(id):

    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM propriedades WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("propriedades"))


# =========================================================
# TALHÕES
# =========================================================

@app.route("/propriedades/<int:propriedade_id>/talhoes")
def talhoes(propriedade_id):

    conexao = conectar_banco()

    propriedade = conexao.execute("""
        SELECT *
        FROM propriedades
        WHERE id = ?
    """, (propriedade_id,)).fetchone()

    lista = conexao.execute("""
        SELECT *
        FROM talhoes
        WHERE propriedade_id = ?
        ORDER BY nome_talhao
    """, (propriedade_id,)).fetchall()

    conexao.close()

    return render_template(
        "talhoes.html",
        propriedade=propriedade,
        talhoes=lista
    )


@app.route(
    "/propriedades/<int:propriedade_id>/talhoes/novo",
    methods=["GET", "POST"]
)
def novo_talhao(propriedade_id):

    conexao = conectar_banco()

    propriedade = conexao.execute("""
        SELECT *
        FROM propriedades
        WHERE id = ?
    """, (propriedade_id,)).fetchone()

    if request.method == "POST":

        nome = request.form["nome_talhao"]
        area = request.form["area_ha"]

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
            nome,
            area
        ))

        conexao.commit()
        conexao.close()

        return redirect(
            url_for(
                "talhoes",
                propriedade_id=propriedade_id
            )
        )

    conexao.close()

    return render_template(
        "talhao_form.html",
        propriedade=propriedade
    )


# =========================================================
# LAUDOS DE SOLO
# =========================================================

@app.route("/talhoes/<int:talhao_id>/laudo/novo", methods=["GET", "POST"])
def novo_laudo(talhao_id):

    conexao = conectar_banco()

    talhao = conexao.execute("""
        SELECT *
        FROM talhoes
        WHERE id = ?
    """, (talhao_id,)).fetchone()

    if request.method == "POST":

        data_coleta = request.form["data_coleta"]
        ph = request.form["ph"]
        v1 = request.form["v1_atual"]
        ctc = request.form["ctc_t"]

        ca = request.form["ca"] or None
        mg = request.form["mg"] or None
        k = request.form["k"] or None
        p = request.form["p"] or None
        h_al = request.form["h_al"] or None
        argila = request.form["argila"] or None

        conexao.execute("""
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
            ph,
            v1,
            ctc,
            ca,
            mg,
            k,
            p,
            h_al,
            argila
        ))

        conexao.commit()
        conexao.close()

        return redirect(
            url_for(
                "index"
            )
        )

    conexao.close()

    return render_template(
        "laudo_form.html",
        talhao=talhao
    )


if __name__ == "__main__":
    app.run(debug=True)