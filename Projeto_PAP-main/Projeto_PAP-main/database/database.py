import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Cria uma conexão com o banco de dados SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conexão com SQLite estabelecida: {db_file}")
        return conn
    except Error as e:
        print(f"Erro ao conectar com o banco: {e}")
    
    return conn

def create_tables(conn):
    """Cria todas as tabelas do banco de dados"""
    try:
        c = conn.cursor()

        # Tabela Utilizador
        print("Criando tabela Utilizador...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS Utilizador (
            IdUtil INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome VARCHAR(20),
            Email VARCHAR(45) NOT NULL,
            Pdw VARCHAR(20) NOT NULL,
            Categoria VARCHAR(45)
        )
        ''')
        print("Tabela Utilizador criada.")

        # Tabela Jogos
        print("Criando tabela Jogos...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS Jogos (
            IdJogo INTEGER PRIMARY KEY AUTOINCREMENT,
            Data DATE NOT NULL,
            Equipa1 VARCHAR(45) NOT NULL,
            Equipa2 VARCHAR(45) NOT NULL,
            Pavilhao VARCHAR(45),
            Tipo VARCHAR(45)
        )
        ''')
        print("Tabela Jogos criada.")

        # Tabela Noticias
        print("Criando tabela Noticias...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS Noticias (
            IdNot INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo VARCHAR(45) NOT NULL,
            Descricao VARCHAR(45),
            Datacria DATE NOT NULL,
            DataPublic DATE
        )
        ''')
        print("Tabela Noticias criada.")

        # Tabela de relacionamento UtilNoti
        print("Criando tabela UtilNoti...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS UtilNoti (
            IdUtil INTEGER NOT NULL,
            IdNot INTEGER NOT NULL,
            Data DATE,
            PRIMARY KEY (IdUtil, IdNot),
            FOREIGN KEY (IdUtil) REFERENCES Utilizador (IdUtil),
            FOREIGN KEY (IdNot) REFERENCES Noticias (IdNot)
        )
        ''')
        print("Tabela UtilNoti criada.")

        # Tabela Comentarios
        print("Criando tabela Comentarios...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS Comentarios (
            IdComentario INTEGER PRIMARY KEY AUTOINCREMENT,
            IdNot INTEGER NOT NULL,
            IdUtil INTEGER NOT NULL,
            Comentario TEXT NOT NULL,
            DataComentario DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdNot) REFERENCES Noticias (IdNot),
            FOREIGN KEY (IdUtil) REFERENCES Utilizador (IdUtil)
        )
        ''')
        print("Tabela Comentarios criada.")

        # Tabela RespostasComentarios
        print("Criando tabela RespostasComentarios...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS RespostasComentarios (
            IdResposta INTEGER PRIMARY KEY AUTOINCREMENT,
            IdComentarioOriginal INTEGER NOT NULL,
            IdUtil INTEGER NOT NULL,
            Resposta TEXT NOT NULL,
            DataResposta DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdComentarioOriginal) REFERENCES Comentarios (IdComentario),
            FOREIGN KEY (IdUtil) REFERENCES Utilizador (IdUtil)
        )
        ''')
        print("Tabela RespostasComentarios criada.")

        # Tabela VotosNoticias
        print("Criando tabela VotosNoticias...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS VotosNoticias (
            IdVoto INTEGER PRIMARY KEY AUTOINCREMENT,
            IdNot INTEGER NOT NULL,
            IdUtil INTEGER NOT NULL,
            Voto INTEGER NOT NULL, -- 1 para like, -1 para dislike
            DataVoto DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdNot) REFERENCES Noticias (IdNot),
            FOREIGN KEY (IdUtil) REFERENCES Utilizador (IdUtil),
            UNIQUE(IdNot, IdUtil)
        )
        ''')
        print("Tabela VotosNoticias criada.")

        print("Todas as tabelas foram criadas com sucesso!")
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")

def main():
    database = "database/meu_banco.db"
    
    # Criar conexão com o banco
    conn = create_connection(database)
    
    if conn is not None:
        # Criar tabelas
        create_tables(conn)
        
        # Fechar conexão
        conn.close()
    else:
        print("Erro! Não foi possível estabelecer conexão com o banco.")

if __name__ == '__main__':
    main()
