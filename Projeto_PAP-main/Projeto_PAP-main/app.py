from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message 
import secrets
import sqlite3
from database.database import create_connection
from datetime import datetime
import os

# Criar instância do Flask
app = Flask(__name__)

# Configuração do banco de dados
DATABASE = "database/meu_banco.db"

def get_db():
    """Retorna uma conexão com o banco de dados"""
    return create_connection(DATABASE)

def obter_noticias():
    """Obtém todas as notícias do banco de dados"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT IdNot, Titulo, Descricao, Datacria, DataPublic FROM Noticias ORDER BY DataPublic DESC")
        noticias = cursor.fetchall()
        conn.close()
        return noticias
    except sqlite3.Error as e:
        print(f"Erro ao obter notícias: {e}")
        return []

def adicionar_noticia(titulo, descricao, data_criacao=None, data_publicacao=None):
    """Adiciona uma nova notícia ao banco de dados"""
    if data_criacao is None:
        data_criacao = datetime.now().strftime('%Y-%m-%d')
    if data_publicacao is None:
        data_publicacao = data_criacao

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Noticias (Titulo, Descricao, Datacria, DataPublic) 
            VALUES (?, ?, ?, ?)
        """, (titulo, descricao, data_criacao, data_publicacao))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar notícia: {e}")
        return False

def obter_jogos():
    """Obtém todos os jogos ordenados por data"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Jogos ORDER BY Data DESC")
        jogos = cursor.fetchall()
        conn.close()
        return jogos
    except sqlite3.Error as e:
        print(f"Erro ao obter jogos: {e}")
        return []

def adicionar_jogo(data, equipa1, equipa2, pavilhao, tipo):
    """Adiciona um novo jogo ao banco de dados"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Jogos (Data, Equipa1, Equipa2, Pavilhao, Tipo) 
            VALUES (?, ?, ?, ?, ?)
        """, (data, equipa1, equipa2, pavilhao, tipo))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar jogo: {e}")
        return False

def obter_jogos_por_tipo(tipo):
    """Obtém jogos de um tipo específico (Futsal ou Voleibol)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Jogos WHERE Tipo = ? ORDER BY Data DESC", (tipo,))
        jogos = cursor.fetchall()
        conn.close()
        return jogos
    except sqlite3.Error as e:
        print(f"Erro ao obter jogos do tipo {tipo}: {e}")
        return []

# Configuração do Flask
app.config['SECRET_KEY'] = 'your-secret-key-here'  
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'papanoletivo2025@gmail.com'  
#app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # O seu e-mail
app.config['MAIL_PASSWORD'] = 'apve jesy sjsx feun'  
#app.config['MAIL_PASSWORD'] = 'your-app-password'     # A palavra-passe da sua aplicação de e-mail

mail = Mail(app)

reset_tokens = {}

def verificar_utilizador(email, senha):
    """Verifica as credenciais do utilizador"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilizador WHERE Email = ? AND Pdw = ?", (email, senha))
        utilizador = cursor.fetchone()
        conn.close()
        return utilizador
    except sqlite3.Error as e:
        print(f"Erro ao verificar utilizador: {e}")
        return None

def obter_utilizador_por_email(email):
    """Obtém um utilizador pelo email"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilizador WHERE Email = ?", (email,))
        utilizador = cursor.fetchone()
        conn.close()
        return utilizador
    except sqlite3.Error as e:
        print(f"Erro ao obter utilizador: {e}")
        return None

def criar_utilizador(nome, email, senha, categoria="utilizador"):
    """Cria um novo utilizador"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Utilizador (Nome, Email, Pdw, Categoria) 
            VALUES (?, ?, ?, ?)
        """, (nome, email, senha, categoria))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao criar utilizador: {e}")
        return False

def atualizar_categorias_utilizador():
    """Atualiza a categoria 'usuario' para 'utilizador' na base de dados"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Utilizador 
            SET Categoria = 'utilizador' 
            WHERE Categoria = 'usuario'
        """)
        conn.commit()
        conn.close()
        print("Categorias atualizadas com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao atualizar categorias: {e}")

# Atualizar categorias de utilizador existentes
atualizar_categorias_utilizador()

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        # Obter a última notícia
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT IdNot, Titulo, Descricao, Datacria, DataPublic FROM Noticias ORDER BY DataPublic DESC LIMIT 1")
        ultima_noticia = cursor.fetchone()

        # Obter o próximo jogo de futsal
        cursor.execute("""
            SELECT * FROM Jogos 
            WHERE Tipo = 'Futsal' AND Data >= date('now') 
            ORDER BY Data ASC LIMIT 1
        """)
        proximo_jogo_futsal = cursor.fetchone()

        # Obter o próximo jogo de voleibol
        cursor.execute("""
            SELECT * FROM Jogos 
            WHERE Tipo = 'Voleibol' AND Data >= date('now') 
            ORDER BY Data ASC LIMIT 1
        """)
        proximo_jogo_voleibol = cursor.fetchone()

        # Obter todos os jogos do mês atual
        cursor.execute("""
            SELECT Data, Tipo FROM Jogos 
            WHERE strftime('%Y-%m', Data) = strftime('%Y-%m', 'now')
            ORDER BY Data ASC
        """)
        jogos_do_mes = cursor.fetchall()

        conn.close()

        if request.method == 'POST':
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            email = request.form['email']
            
            if password != confirm_password:
                return "As palavras-passe não coincidem!"
            
            return f"Registo realizado com sucesso para {name}!"
            
        return render_template("home.html", 
                             ultima_noticia=ultima_noticia,
                             proximo_jogo_futsal=proximo_jogo_futsal,
                             proximo_jogo_voleibol=proximo_jogo_voleibol,
                             jogos_do_mes=jogos_do_mes)
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return render_template("home.html", 
                             ultima_noticia=None,
                             proximo_jogo_futsal=None,
                             proximo_jogo_voleibol=None,
                             jogos_do_mes=[])

@app.route('/contato')
def contato():
    return render_template("contato.html")

@app.route('/pp/<name>')
def pp(name):
    return render_template("pp.html", name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        utilizador = verificar_utilizador(email, password)
        if utilizador:
            session['user_id'] = utilizador[0]
            session['user_name'] = utilizador[1]
            session['user_email'] = utilizador[2]
            session['user_category'] = utilizador[4]
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email ou senha incorretos!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('register'))
            
        if obter_utilizador_por_email(email):
            flash('Este email já está registrado!', 'error')
            return redirect(url_for('register'))
            
        if criar_utilizador(nome, email, password):
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao realizar registro!', 'error')
            
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Verificar se o email existe no banco de dados
        utilizador = obter_utilizador_por_email(email)
        if not utilizador:
            flash('Email não encontrado no sistema.', 'error')
            return render_template('forgot_password.html', email=email)
        
        # Gerar token
        token = secrets.token_urlsafe(32)
        reset_tokens[token] = email
        
        reset_link = url_for('reset_password', token=token, _external=True)
        
        # Enviar e-mail
        try:
            msg = Message('Redefinição de Palavra-passe - Madeira Ativa',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f'''Para redefinir sua palavra-passe, clique no link abaixo:
{reset_link}

Se você não solicitou a redefinição de palavra-passe, ignore este e-mail.

Atenciosamente,
Equipe Madeira Ativa'''
            mail.send(msg)
            flash('Link de redefinição de palavra-passe enviado para o seu e-mail!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            flash('Erro ao enviar o e-mail. Por favor, tente novamente.', 'error')
            return render_template('forgot_password.html', email=email)
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if token not in reset_tokens:
        flash('Link de redefinição inválido ou expirado.', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('As palavras-passe não coincidem.', 'error')
            return redirect(url_for('reset_password', token=token))
        
        try:
            # Atualizar a palavra-passe na base de dados
            email = reset_tokens[token]
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE Utilizador SET Pdw = ? WHERE Email = ?", (new_password, email))
            conn.commit()
            conn.close()
            
            # Remover o token usado
            del reset_tokens[token]
            
            flash('Palavra-passe redefinida com sucesso! Pode agora fazer login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            print(f"Erro ao atualizar senha: {e}")
            flash('Erro ao redefinir a palavra-passe. Por favor, tente novamente.', 'error')
            return redirect(url_for('reset_password', token=token))
        
    return render_template('reset_password.html')

def obter_comentarios(id_noticia):
    """Obtém todos os comentários de uma notícia específica."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.IdComentario, c.Comentario, c.DataComentario, u.Nome
            FROM Comentarios c
            JOIN Utilizador u ON c.IdUtil = u.IdUtil
            WHERE c.IdNot = ?
            ORDER BY c.DataComentario ASC
        ''', (id_noticia,))
        comentarios = cursor.fetchall()
        conn.close()
        return comentarios
    except sqlite3.Error as e:
        print(f"Erro ao obter comentários: {e}")
        return []

def adicionar_comentario(id_noticia, id_util, comentario):
    print(f"[DEBUG] Inserindo comentário: id_noticia={id_noticia}, id_util={id_util}, comentario={comentario}")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Comentarios (IdNot, IdUtil, Comentario) VALUES (?, ?, ?)
        ''', (id_noticia, id_util, comentario))
        conn.commit()
        conn.close()
        print("[DEBUG] Comentário inserido com sucesso!")
        return True
    except sqlite3.Error as e:
        print(f"[ERRO] Erro ao adicionar comentário: {e}")
        return False

@app.route('/noticias/<int:id>/comentario', methods=['POST'])
def comentar_noticia(id):
    print(f"[DEBUG] Rota comentar_noticia chamada para noticia {id}")
    if 'user_id' not in session:
        print("[ERRO] Utilizador não autenticado!")
        flash('Precisa de estar autenticado para comentar.', 'error')
        return redirect(url_for('noticias'))
    comentario = request.form.get('comentario')
    print(f"[DEBUG] Comentário recebido: {comentario}")
    if not comentario:
        print("[ERRO] Comentário vazio!")
        flash('O comentário não pode estar vazio.', 'error')
        return redirect(url_for('noticias'))
    if adicionar_comentario(id, session['user_id'], comentario):
        flash('Comentário adicionado com sucesso!', 'success')
    else:
        flash('Erro ao adicionar comentário.', 'error')
    return redirect(url_for('noticias'))

@app.route('/noticias', methods=['GET', 'POST'])
def noticias():
    try:
        if request.method == 'POST':
            print("[DEBUG] Método POST recebido na rota /noticias")
            print(f"[DEBUG] Dados do formulário: {request.form}")
            if 'user_id' not in session or session['user_category'] not in ['admin', 'noticias']:
                flash('Acesso negado!', 'error')
                return redirect(url_for('noticias'))
                
            titulo = request.form['Titulo']
            descricao = request.form['Descricao']
            data_criacao = request.form['Datacria']
            data_publicacao = request.form['DataPublic']
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Noticias (Titulo, Descricao, Datacria, DataPublic) 
                VALUES (?, ?, ?, ?)
            ''', (titulo, descricao, data_criacao, data_publicacao))
            conn.commit()
            conn.close()
            
            flash('Notícia adicionada com sucesso!', 'success')
            return redirect(url_for('noticias'))
            
        # GET request
        lista_noticias = obter_noticias()
        # Buscar comentários para cada notícia
        comentarios_dict = {}
        for noticia in lista_noticias:
            comentarios_dict[noticia[0]] = obter_comentarios(noticia[0])
        return render_template('noticias.html', noticias=lista_noticias, comentarios_dict=comentarios_dict)
    except Exception as e:
        print(f"Erro na rota /noticias: {e}")
        flash('Erro ao processar a requisição', 'error')
        return render_template('noticias.html', noticias=[], comentarios_dict={})

@app.route('/voleibol', methods=['GET', 'POST'])
def voleibol():
    try:
        if request.method == 'POST':
            data = request.form['Data']
            equipa1 = request.form['Equipa1']
            equipa2 = request.form['Equipa2']
            pavilhao = request.form['Pavilhao']
            tipo = request.form['Tipo']
            
            if adicionar_jogo(data, equipa1, equipa2, pavilhao, tipo):
                flash('Jogo adicionado com sucesso!', 'success')
            else:
                flash('Erro ao adicionar jogo', 'error')
            return redirect(url_for('voleibol'))
            
        lista_jogos = obter_jogos_por_tipo('Voleibol')
        return render_template('voleibol.html', jogos=lista_jogos)
    except Exception as e:
        print(f"Erro na rota /voleibol: {e}")
        flash('Erro ao processar a requisição', 'error')
        return render_template('voleibol.html', jogos=[])

@app.route('/futsal', methods=['GET', 'POST'])
def futsal():
    try:
        if request.method == 'POST':
            data = request.form['Data']
            equipa1 = request.form['Equipa1']
            equipa2 = request.form['Equipa2']
            pavilhao = request.form['Pavilhao']
            tipo = request.form['Tipo']
            
            if adicionar_jogo(data, equipa1, equipa2, pavilhao, tipo):
                flash('Jogo adicionado com sucesso!', 'success')
            else:
                flash('Erro ao adicionar jogo', 'error')
            return redirect(url_for('futsal'))
            
        lista_jogos = obter_jogos_por_tipo('Futsal')
        return render_template('futsal.html', jogos=lista_jogos)
    except Exception as e:
        print(f"Erro na rota /futsal: {e}")
        flash('Erro ao processar a requisição', 'error')
        return render_template('futsal.html', jogos=[])

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if 'user_id' not in session or session['user_category'] not in ['admin', 'noticias']:
        flash('Acesso negado!', 'error')
        return redirect(url_for('noticias'))

    if request.method == 'POST':
        titulo = request.form['Titulo']
        descricao = request.form['Descricao']
        data_criacao = request.form['Datacria']
        data_publicacao = request.form['DataPublic']
        
        if adicionar_noticia(titulo, descricao, data_criacao, data_publicacao):
            flash('Notícia adicionada com sucesso!', 'success')
            return redirect(url_for('noticias'))
        else:
            flash('Erro ao adicionar notícia', 'error')
            
    lista_noticias = obter_noticias()
    return render_template('novo.html', noticias=lista_noticias)

@app.route('/noticias/<int:id>', methods=['POST'])
def editar_noticia(id):
    if request.form.get('_method') == 'PUT':
        if 'user_id' not in session or session['user_category'] not in ['admin', 'noticias']:
            flash('Acesso negado!', 'error')
            return redirect(url_for('noticias'))
            
        titulo = request.form['Titulo']
        descricao = request.form['Descricao']
        data_criacao = request.form['Datacria']
        data_publicacao = request.form['DataPublic']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Noticias 
                SET Titulo = ?, Descricao = ?, Datacria = ?, DataPublic = ?
                WHERE IdNot = ?
            """, (titulo, descricao, data_criacao, data_publicacao, id))
            conn.commit()
            conn.close()
            flash('Notícia atualizada com sucesso!', 'success')
        except sqlite3.Error as e:
            flash('Erro ao atualizar notícia!', 'error')
            print(f"Erro ao atualizar notícia: {e}")
            
    return redirect(url_for('noticias'))

@app.route('/noticias/excluir/<int:id>', methods=['POST'])
def excluir_noticia(id):
    if 'user_id' not in session or session['user_category'] not in ['admin', 'noticias']:
        flash('Acesso negado!', 'error')
        return redirect(url_for('noticias'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Noticias WHERE IdNot = ?", (id,))
        conn.commit()
        conn.close()
        flash('Notícia excluída com sucesso!', 'success')
    except sqlite3.Error as e:
        flash('Erro ao excluir notícia!', 'error')
        print(f"Erro ao excluir notícia: {e}")
        
    return redirect(url_for('noticias'))

@app.route('/futsal/<int:id>', methods=['POST'])
def editar_jogo_futsal(id):
    if request.form.get('_method') == 'PUT':
        if 'user_id' not in session or session['user_category'] != 'admin':
            flash('Acesso negado!', 'error')
            return redirect(url_for('futsal'))
            
        data = request.form['Data']
        equipa1 = request.form['Equipa1']
        equipa2 = request.form['Equipa2']
        pavilhao = request.form['Pavilhao']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Jogos 
                SET Data = ?, Equipa1 = ?, Equipa2 = ?, Pavilhao = ?
                WHERE IdJogo = ? AND Tipo = 'Futsal'
            """, (data, equipa1, equipa2, pavilhao, id))
            conn.commit()
            conn.close()
            flash('Jogo atualizado com sucesso!', 'success')
        except sqlite3.Error as e:
            flash('Erro ao atualizar jogo!', 'error')
            print(f"Erro ao atualizar jogo: {e}")
            
    return redirect(url_for('futsal'))

@app.route('/voleibol/<int:id>', methods=['POST'])
def editar_jogo_voleibol(id):
    if request.form.get('_method') == 'PUT':
        if 'user_id' not in session or session['user_category'] != 'admin':
            flash('Acesso negado!', 'error')
            return redirect(url_for('voleibol'))
            
        data = request.form['Data']
        equipa1 = request.form['Equipa1']
        equipa2 = request.form['Equipa2']
        pavilhao = request.form['Pavilhao']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Jogos 
                SET Data = ?, Equipa1 = ?, Equipa2 = ?, Pavilhao = ?
                WHERE IdJogo = ? AND Tipo = 'Voleibol'
            """, (data, equipa1, equipa2, pavilhao, id))
            conn.commit()
            conn.close()
            flash('Jogo atualizado com sucesso!', 'success')
        except sqlite3.Error as e:
            flash('Erro ao atualizar jogo!', 'error')
            print(f"Erro ao atualizar jogo: {e}")
            
    return redirect(url_for('voleibol'))

@app.route('/jogos/excluir/<int:id>', methods=['POST'])
def excluir_jogo(id):
    if 'user_id' not in session or session['user_category'] != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('home'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Primeiro, verificamos o tipo do jogo para redirecionar corretamente
        cursor.execute("SELECT Tipo FROM Jogos WHERE IdJogo = ?", (id,))
        jogo = cursor.fetchone()
        
        if not jogo:
            flash('Jogo não encontrado!', 'error')
            return redirect(url_for('home'))
            
        tipo_jogo = jogo[0]
        
        # Agora excluímos o jogo
        cursor.execute("DELETE FROM Jogos WHERE IdJogo = ?", (id,))
        conn.commit()
        conn.close()
        
        flash('Jogo excluído com sucesso!', 'success')
        
        # Redirecionamos para a página correta com base no tipo do jogo
        if tipo_jogo == 'Futsal':
            return redirect(url_for('futsal'))
        else:
            return redirect(url_for('voleibol'))
            
    except sqlite3.Error as e:
        flash('Erro ao excluir jogo!', 'error')
        print(f"Erro ao excluir jogo: {e}")
        return redirect(url_for('home'))

def obter_respostas_comentario(id_comentario):
    """Obtém todas as respostas para um comentário específico."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.IdResposta, r.Resposta, r.DataResposta, u.Nome
            FROM RespostasComentarios r
            JOIN Utilizador u ON r.IdUtil = u.IdUtil
            WHERE r.IdComentarioOriginal = ?
            ORDER BY r.DataResposta ASC
        ''', (id_comentario,))
        respostas = cursor.fetchall()
        conn.close()
        return respostas
    except sqlite3.Error as e:
        print(f"Erro ao obter respostas: {e}")
        return []

def adicionar_resposta_comentario(id_comentario_original, id_util, resposta):
    """Adiciona uma resposta a um comentário existente."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO RespostasComentarios (IdComentarioOriginal, IdUtil, Resposta) VALUES (?, ?, ?)
        ''', (id_comentario_original, id_util, resposta))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar resposta: {e}")
        return False

@app.route('/noticias/comentario/<int:id_comentario>/resposta', methods=['POST'])
def responder_comentario(id_comentario):
    if 'user_id' not in session:
        flash('Precisa de estar autenticado para responder.', 'error')
        return redirect(url_for('noticias'))
    resposta = request.form.get('resposta')
    if not resposta:
        flash('A resposta não pode estar vazia.', 'error')
        return redirect(url_for('noticias'))
    if adicionar_resposta_comentario(id_comentario, session['user_id'], resposta):
        flash('Resposta adicionada com sucesso!', 'success')
    else:
        flash('Erro ao adicionar resposta.', 'error')
    return redirect(url_for('noticias'))

@app.route('/noticias/comentario/<int:id_comentario>/excluir', methods=['POST'])
def excluir_comentario(id_comentario):
    if 'user_id' not in session:
        flash('Precisa de estar autenticado para excluir o comentário.', 'error')
        return redirect(url_for('noticias'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Permite excluir se for admin, editor ou o próprio autor
        cursor.execute("DELETE FROM Comentarios WHERE IdComentario = ? AND (IdUtil = ? OR ? IN (SELECT 1 FROM Utilizador WHERE IdUtil = ? AND Categoria IN ('admin', 'noticias'))) ", (id_comentario, session['user_id'], session['user_id'], session['user_id']))
        if cursor.rowcount == 0:
            flash('Não tem permissão para excluir este comentário.', 'error')
        else:
            conn.commit()
            flash('Comentário excluído com sucesso!', 'success')
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao excluir comentário: {e}")
        flash('Erro ao excluir comentário!', 'error')
    return redirect(url_for('noticias'))

@app.route('/noticias/comentario/<int:id_comentario>/editar', methods=['POST'])
def editar_comentario(id_comentario):
    if 'user_id' not in session:
        flash('Precisa de estar autenticado para editar o comentário.', 'error')
        return redirect(url_for('noticias'))
    novo_comentario = request.form.get('novo_comentario')
    if not novo_comentario:
        flash('O comentário não pode estar vazio.', 'error')
        return redirect(url_for('noticias'))
    id_noticia = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Buscar o IdNot da notícia deste comentário
        cursor.execute("SELECT IdNot FROM Comentarios WHERE IdComentario = ?", (id_comentario,))
        row = cursor.fetchone()
        id_noticia = row[0] if row else None
        # Só permite editar se for o autor do comentário
        cursor.execute("UPDATE Comentarios SET Comentario = ? WHERE IdComentario = ? AND IdUtil = ?", (novo_comentario, id_comentario, session['user_id']))
        if cursor.rowcount == 0:
            flash('Não tem permissão para editar este comentário.', 'error')
        else:
            conn.commit()
            flash('Comentário editado com sucesso!', 'success')
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao editar comentário: {e}")
        flash('Erro ao editar comentário!', 'error')
    # Redireciona para a notícia correta se possível
    if id_noticia:
        return redirect(url_for('noticia', id=id_noticia))
    return redirect(url_for('noticias'))

@app.route('/noticias/<int:id>/votar', methods=['POST'])
def votar_noticia(id):
    if 'user_id' not in session:
        flash('Precisa de estar autenticado para votar.', 'error')
        return redirect(url_for('noticias'))
    voto = request.form.get('voto')
    if voto not in ['1', '-1']:
        flash('Voto inválido.', 'error')
        return redirect(url_for('noticias'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Verificar se o utilizador já votou nesta notícia
        cursor.execute("SELECT Voto FROM VotosNoticias WHERE IdNot = ? AND IdUtil = ?", (id, session['user_id']))
        row = cursor.fetchone()
        if row:
            # Atualizar o voto existente
            cursor.execute("UPDATE VotosNoticias SET Voto = ? WHERE IdNot = ? AND IdUtil = ?", (int(voto), id, session['user_id']))
            print(f"Voto atualizado: {voto} para notícia {id} pelo utilizador {session['user_id']}")
        else:
            # Inserir novo voto
            cursor.execute("INSERT INTO VotosNoticias (IdNot, IdUtil, Voto) VALUES (?, ?, ?)", (id, session['user_id'], int(voto)))
            print(f"Novo voto inserido: {voto} para notícia {id} pelo utilizador {session['user_id']}")
        conn.commit()
        conn.close()
        flash('Voto registrado com sucesso!', 'success')
    except sqlite3.Error as e:
        print(f"Erro ao votar: {e}")
        flash('Erro ao registrar voto!', 'error')
    return redirect(url_for('noticias'))

@app.route('/noticias/<int:id>/votos', methods=['GET'])
def obter_votos_noticia(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM VotosNoticias WHERE IdNot = ? AND Voto = 1", (id,))
        likes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM VotosNoticias WHERE IdNot = ? AND Voto = -1", (id,))
        dislikes = cursor.fetchone()[0]
        conn.close()
        return jsonify({'likes': likes, 'dislikes': dislikes})
    except sqlite3.Error as e:
        print(f"Erro ao obter votos: {e}")
        return jsonify({'error': 'Erro ao obter votos'}), 500

# Garantir que a pasta templates existe
if not os.path.exists('templates'):
    os.makedirs('templates')

if __name__ == '__main__':
    app.run(debug=True)

