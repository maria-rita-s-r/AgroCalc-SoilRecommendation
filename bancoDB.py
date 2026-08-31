import sqlite3

def criar_banco_de_dados():
    # Conecta ou cria o arquivo do banco de dados SQLite
    conexao = sqlite3.connect("calculadora_agricola.db")
    cursor = conexao.cursor()

    # Ativa o suporte a Chaves Estrangeiras (Foreign Keys)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tabela de Produtores / Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT
    );
    """)

    # 2. Tabela de Propriedades (Fazendas)
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

    # 3. Tabela de Talhões (Áreas de Cultivo)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS talhoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        propriedade_id INTEGER NOT NULL,
        nome_talhao TEXT NOT NULL,
        area_ha REAL NOT NULL,
        FOREIGN KEY (propriedade_id) REFERENCES propriedades(id) ON DELETE CASCADE
    );
    """)

    # 4. Tabela de Entradas da Análise de Solo (Laudos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laudos_solo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        talhao_id INTEGER NOT NULL,
        data_coleta DATE,
        ph REAL NOT NULL,
        v1_atual REAL NOT NULL,
        ctc_t REAL NOT NULL,
        ca REAL,
        mg REAL,
        k REAL,
        p REAL,
        h_al REAL,
        argila REAL,
        FOREIGN KEY (talhao_id) REFERENCES talhoes(id) ON DELETE CASCADE
    );
    """)

    # 5. Tabela de Culturas e Alvos Agronômicos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS culturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cultura TEXT NOT NULL,
        v2_alvo REAL NOT NULL
    );
    """)

    # 6. Tabela de Insumos (Calcário e Adubos)
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

    # 7. Tabela do Histórico de Recomendações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recomendacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        laudo_id INTEGER NOT NULL,
        cultura_id INTEGER NOT NULL,
        calcario_id INTEGER NOT NULL,
        nc_ha REAL NOT NULL,
        dose_calcario_ha REAL NOT NULL,
        total_calcario_talhao REAL NOT NULL,
        dose_n_ha REAL,
        dose_p2o5_ha REAL,
        dose_k2o_ha REAL,
        data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (laudo_id) REFERENCES laudos_solo(id),
        FOREIGN KEY (cultura_id) REFERENCES culturas(id),
        FOREIGN KEY (calcario_id) REFERENCES corretivos_calcario(id)
    );
    """)

    # Salva as alterações no banco de dados e fecha a conexão
    conexao.commit()
    conexao.close()
    print("Banco de dados 'calculadora_agricola.db' criado com sucesso!")

# Executa a função para criar o banco de dados
if __name__ == "__main__":
    criar_banco_de_dados()