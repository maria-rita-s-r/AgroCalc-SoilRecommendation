import sqlite3

DATABASE = "calculadora_agricola.db"

def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao

def criar_banco_de_dados():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS propriedades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produtor_id INTEGER NOT NULL,
        nome_propriedade TEXT NOT NULL,
        municipio TEXT,
        estado TEXT,
        FOREIGN KEY (produtor_id) REFERENCES produtores(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS talhoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        propriedade_id INTEGER NOT NULL,
        nome_talhao TEXT NOT NULL,
        area_ha REAL NOT NULL,
        FOREIGN KEY (propriedade_id) REFERENCES propriedades(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS culturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cultura TEXT NOT NULL,
        v2_alvo REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS corretivos_calcario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_comercial TEXT NOT NULL,
        prnt_porcento REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fertilizantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_comercial TEXT NOT NULL,
        teor_n REAL DEFAULT 0,
        teor_p2o5 REAL DEFAULT 0,
        teor_k2o REAL DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recomendacoes_solo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        talhao_id INTEGER NOT NULL,
        cultura_id INTEGER NOT NULL,
        calcario_id INTEGER,
        data_coleta TEXT,
        ph REAL,
        v1_atual REAL,
        ctc_t REAL,
        ca REAL,
        mg REAL,
        k REAL,
        p REAL,
        h_al REAL,
        argila REAL,
        nc_ha REAL,
        dose_calcario_ha REAL,
        total_calcario_talhao REAL,
        FOREIGN KEY (talhao_id) REFERENCES talhoes(id) ON DELETE CASCADE,
        FOREIGN KEY (cultura_id) REFERENCES culturas(id) ON DELETE CASCADE,
        FOREIGN KEY (calcario_id) REFERENCES corretivos_calcario(id)
    );
    """)

    conexao.commit()
    conexao.close()
    print("Banco de dados 'calculadora_agricola.db' inicializado com sucesso!")

if __name__ == "__main__":
    criar_banco_de_dados()