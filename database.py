import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd

DB_FILE = os.path.join(os.path.dirname(__file__), "ecomcontrol.db")

def get_connection():
    """Retorna uma conexão configurada com o banco SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados e popula com dados iniciais se estiver vazio."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Tabela Clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Tabela Pedidos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_pedido TEXT NOT NULL UNIQUE,
            cliente_id INTEGER NOT NULL,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            valor_total REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'Pendente',
            codigo_rastreio TEXT,
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
        """)
        
        # 3. Tabela Problemas (Ocorrências de Pós-venda)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS problemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            cliente_id INTEGER NOT NULL,
            tipo_problema TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberto',
            prioridade TEXT NOT NULL DEFAULT 'Média',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
        """)
        
        # 4. Tabela Atendimentos (SAC / Suporte)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            pedido_id INTEGER,
            canal TEXT NOT NULL DEFAULT 'WhatsApp',
            assunto TEXT NOT NULL,
            mensagem_cliente TEXT NOT NULL,
            resposta_enviada TEXT,
            status TEXT NOT NULL DEFAULT 'Pendente',
            sentimento TEXT NOT NULL DEFAULT 'Neutro',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL
        )
        """)
        
        # 5. Tabela Respostas Prontas (Canned Responses)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS respostas_prontas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            atalho TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()

    # Verifica se precisa popular dados iniciais
    _seed_initial_data_if_empty()

def _seed_initial_data_if_empty():
    """Popula o banco com dados realistas de exemplo caso esteja sem registros."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM clientes")
        if cursor.fetchone()["count"] > 0:
            return  # Banco já possui dados
        
        # Inserção de Clientes
        clientes = [
            ("Lucas Oliveira Silva", "lucas.oliveira@email.com", "11987654321", "12345678901", "Av. Paulista, 1578, Apto 42", "São Paulo", "SP", "01310200"),
            ("Mariana Souza Costa", "mariana.costa@email.com", "21998765432", "23456789012", "Rua Visconde de Pirajá, 305", "Rio de Janeiro", "RJ", "22410001"),
            ("Carlos Eduardo Rocha", "carlos.rocha@email.com", "31987651234", "34567890123", "Rua dos Aimorés, 1450", "Belo Horizonte", "MG", "30140071"),
            ("Fernanda Alves Lima", "fernanda.lima@email.com", "41991234567", "45678901234", "Rua XV de Novembro, 800", "Curitiba", "PR", "80020310"),
            ("Rafael Mendes Pereira", "rafael.mendes@email.com", "51982345678", "56789012345", "Rua dos Andradas, 900", "Porto Alegre", "RS", "90020005"),
            ("Beatriz Martins Castro", "beatriz.martins@email.com", "71993456789", "67890123456", "Av. Tancredo Neves, 620", "Salvador", "BA", "41820020"),
            ("Gabriel Ribeiro Santos", "gabriel.santos@email.com", "85994567890", "78901234567", "Av. Beira Mar, 2800", "Fortaleza", "CE", "60165121"),
            ("Juliana Barbosa Dias", "juliana.dias@email.com", "61995678901", "89012345678", "SCS Quadra 4, Bloco A", "Brasília", "DF", "70304000")
        ]
        cursor.executemany("""
        INSERT INTO clientes (nome, email, telefone, cpf, endereco, cidade, estado, cep)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, clientes)

        # Inserção de Pedidos
        pedidos = [
            ("PED-2026-1001", 1, "Fone de Ouvido Bluetooth Noise Cancelling Pro", 1, 489.90, "Entregue", "BR293847561AA", (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1002", 2, "Smartwatch Fitness Tracker Pro HR", 1, 329.00, "Entregue", "BR384756291BB", (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1003", 3, "Teclado Mecânico Gamer RGB Switch Brown", 1, 379.50, "Enviado", "BR495867382CC", (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1004", 4, "Cadeira Ergonômica Mesh Office Pro", 1, 1150.00, "Enviado", "BR584930291DD", (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1005", 5, "Monitor Ultrawide 29'' IPS 75Hz", 1, 1299.90, "Pago", "BR694837201EE", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1006", 6, "Kit Mouse Sem Fio + Mousepad Gamer Speed", 2, 199.80, "Pendente", None, (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1007", 7, "Webcam 4K Ultra HD com Microfone Duplo", 1, 420.00, "Entregue", "BR784930219FF", (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1008", 8, "Luminária de Mesa Inteligente LED RGB", 2, 258.00, "Cancelado", None, (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1009", 1, "Carregador Portátil Power Bank 20.000mAh", 2, 278.00, "Entregue", "BR894039281GG", (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
            ("PED-2026-1010", 3, "Suporte Articulado para Monitor Duplo", 1, 245.90, "Pago", None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
        INSERT INTO pedidos (codigo_pedido, cliente_id, produto, quantidade, valor_total, status, codigo_rastreio, data_pedido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pedidos)

        # Inserção de Problemas
        problemas = [
            (3, 3, "Atraso na Entrega", "Objeto parado no centro de distribuição dos Correios há mais de 4 dias sem nova movimentação.", "Em Análise", "Alta", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (7, 7, "Defeito de Fabricação", "Webcam não é reconhecida pelo Windows após 2 semanas de uso moderado.", "Aberto", "Urgente", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (1, 1, "Item Incorreto", "Cliente recebeu a cor branca ao invés da cor preta solicitada.", "Resolvido", "Média", (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")),
            (8, 8, "Cancelamento / Reembolso", "Cliente solicitou cancelamento por arrependimento de compra no prazo de 7 dias.", "Resolvido", "Baixa", (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S")),
            (4, 4, "Atraso na Entrega", "Transportadora não compareceu no endereço para entrega programada.", "Aberto", "Alta", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
        INSERT INTO problemas (pedido_id, cliente_id, tipo_problema, descricao, status, prioridade, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, problemas)

        # Inserção de Atendimentos (SAC)
        atendimentos = [
            (3, 3, "WhatsApp", "Status de envio PED-2026-1003", "Olá! Meu teclado ainda não chegou e o rastreio não atualiza desde terça-feira. Podem verificar por favor?", "Olá Carlos! Já abrimos um protocolo prioritário junto à transportadora para agilizar sua entrega. Te daremos retorno em até 24h.", "Respondido", "Negativo", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (7, 7, "Mercado Livre", "Garantia Webcam PED-2026-1007", "Boa tarde, a câmera parou de funcionar do nada. Preciso dela para trabalho diário. Como funciona a troca?", None, "Pendente", "Crítico", (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
            (2, 2, "Chat", "Dúvida sobre aplicativo do Smartwatch", "Oi pessoal, adorei o relógio! Qual é o nome do app oficial para sincronizar no iPhone?", "Olá Mariana! Que ótimo que gostou! O app oficial é o 'FitPro Health', disponível gratuitamente na App Store. Qualquer dúvida estamos à disposição!", "Fechado", "Positivo", (datetime.now() - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S")),
            (4, 4, "Email", "Prazo Cadeira Office PED-2026-1004", "Recebi mensagem de tentativa de entrega mas havia gente em casa o dia todo. Podem reagendar?", None, "Pendente", "Negativo", (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 5, "Shopee", "Nota Fiscal Monitor PED-2026-1005", "Olá, onde posso fazer o download da DANFE do meu monitor?", "Olá Rafael! A NF-e foi enviada ao seu e-mail cadastrado e também anexada nos detalhes do pedido no app da Shopee. Se precisar, reenviamos aqui!", "Fechado", "Neutro", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
        INSERT INTO atendimentos (cliente_id, pedido_id, canal, assunto, mensagem_cliente, resposta_enviada, status, sentimento, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, atendimentos)

        # Inserção de Respostas Prontas (Canned Responses)
        respostas = [
            ("Rastreamento de Encomenda", "Rastreio", "Olá {nome}, seu pedido {pedido} já foi despachado! Você pode acompanhar a rota pelo código de rastreio: {codigo_rastreio}. Em caso de dúvidas sobre o prazo, estamos à disposição!", "/rastreio"),
            ("Atraso na Entrega - Abertura de Protocolo", "Atraso", "Olá {nome}, lamentamos profundamente pelo imprevisto no prazo do pedido {pedido}. Já abrimos uma solicitação de urgência junto à transportadora responsável para que a entrega seja priorizada imediatamente.", "/atraso"),
            ("Procedimento de Troca por Defeito", "Garantia", "Olá {nome}, sentimos muito pelo problema relatado no seu produto do pedido {pedido}. Todos os nossos produtos possuem garantia. Para agilizar sua troca ou envio para assistência, siga as instruções que enviamos em anexo.", "/troca"),
            ("Confirmação de Reembolso / Estorno", "Financeiro", "Olá {nome}, confirmamos o cancelamento e a solicitação de reembolso referente ao pedido {pedido}. O comprovante da transação financeira foi gerado e o valor será estornado conforme a operadora do seu meio de pagamento.", "/reembolso"),
            ("Saudação Inicial e Acolhimento", "Geral", "Olá {nome}! Tudo bem? Seja muito bem-vindo ao suporte EcomControl. Meu nome é o atendente do SAC e estou aqui para te ajudar com seu pedido {pedido}. Como posso te auxiliar hoje?", "/ola"),
            ("Encerramento com Agradecimento", "Geral", "Ficamos muito felizes em ajudar, {nome}! Se restar qualquer dúvida, basta nos chamar novamente. Desejamos uma excelente experiência com seus produtos!", "/obrigado")
        ]
        cursor.executemany("""
        INSERT INTO respostas_prontas (titulo, categoria, conteudo, atalho)
        VALUES (?, ?, ?, ?)
        """, respostas)

        conn.commit()

# ==========================================
# CRUD - CLIENTES
# ==========================================

def get_clientes(search: str = None) -> list:
    """Retorna lista de clientes com busca opcional."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if search:
            s = f"%{search.strip()}%"
            cursor.execute("""
            SELECT * FROM clientes
            WHERE nome LIKE ? OR email LIKE ? OR telefone LIKE ? OR cpf LIKE ? OR cidade LIKE ?
            ORDER BY id DESC
            """, (s, s, s, s, s))
        else:
            cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_cliente_by_id(cliente_id: int) -> dict:
    """Retorna dados de um cliente específico pelo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_cliente(nome: str, email: str, telefone: str = "", cpf: str = "", endereco: str = "", cidade: str = "", estado: str = "", cep: str = "") -> int:
    """Cadastra um novo cliente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO clientes (nome, email, telefone, cpf, endereco, cidade, estado, cep)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome.strip(), email.strip(), telefone.strip(), cpf.strip(), endereco.strip(), cidade.strip(), estado.strip(), cep.strip()))
        conn.commit()
        return cursor.lastrowid

def update_cliente(cliente_id: int, nome: str, email: str, telefone: str, cpf: str, endereco: str, cidade: str, estado: str, cep: str) -> bool:
    """Atualiza dados cadastrais de um cliente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE clientes
        SET nome = ?, email = ?, telefone = ?, cpf = ?, endereco = ?, cidade = ?, estado = ?, cep = ?
        WHERE id = ?
        """, (nome.strip(), email.strip(), telefone.strip(), cpf.strip(), endereco.strip(), cidade.strip(), estado.strip(), cep.strip(), cliente_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_cliente(cliente_id: int) -> bool:
    """Remove um cliente e seus dados relacionados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==========================================
# CRUD - PEDIDOS
# ==========================================

def get_pedidos(status: str = None, cliente_id: int = None, search: str = None) -> list:
    """Retorna lista de pedidos com filtros dinâmicos e nome do cliente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
        SELECT p.*, c.nome as cliente_nome, c.email as cliente_email, c.telefone as cliente_telefone
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE 1=1
        """
        params = []
        if status and status != "Todos":
            query += " AND p.status = ?"
            params.append(status)
        if cliente_id:
            query += " AND p.cliente_id = ?"
            params.append(cliente_id)
        if search:
            s = f"%{search.strip()}%"
            query += " AND (p.codigo_pedido LIKE ? OR p.produto LIKE ? OR p.codigo_rastreio LIKE ? OR c.nome LIKE ?)"
            params.extend([s, s, s, s])
        
        query += " ORDER BY p.id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_pedido_by_id(pedido_id: int) -> dict:
    """Retorna um pedido específico por ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, c.nome as cliente_nome, c.email as cliente_email, c.telefone as cliente_telefone
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
        """, (pedido_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_pedido_by_codigo(codigo_pedido: str) -> dict:
    """Busca pedido pelo código de rastreamento ou código interno."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, c.nome as cliente_nome, c.email as cliente_email, c.telefone as cliente_telefone
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.codigo_pedido = ? OR p.codigo_rastreio = ?
        """, (codigo_pedido.strip(), codigo_pedido.strip()))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_pedido(codigo_pedido: str, cliente_id: int, produto: str, quantidade: int, valor_total: float, status: str = "Pendente", codigo_rastreio: str = "") -> int:
    """Cria um novo pedido no sistema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO pedidos (codigo_pedido, cliente_id, produto, quantidade, valor_total, status, codigo_rastreio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (codigo_pedido.strip(), cliente_id, produto.strip(), quantidade, float(valor_total), status.strip(), codigo_rastreio.strip() if codigo_rastreio else None))
        conn.commit()
        return cursor.lastrowid

def update_pedido(pedido_id: int, codigo_pedido: str, cliente_id: int, produto: str, quantidade: int, valor_total: float, status: str, codigo_rastreio: str) -> bool:
    """Atualiza dados e status do pedido."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE pedidos
        SET codigo_pedido = ?, cliente_id = ?, produto = ?, quantidade = ?, valor_total = ?, status = ?, codigo_rastreio = ?
        WHERE id = ?
        """, (codigo_pedido.strip(), cliente_id, produto.strip(), quantidade, float(valor_total), status.strip(), codigo_rastreio.strip() if codigo_rastreio else None, pedido_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_pedido(pedido_id: int) -> bool:
    """Remove um pedido."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==========================================
# CRUD - PROBLEMAS
# ==========================================

def get_problemas(status: str = None, prioridade: str = None, search: str = None) -> list:
    """Retorna lista de problemas registrados com dados de cliente e pedido."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
        SELECT pr.*, c.nome as cliente_nome, c.email as cliente_email, p.codigo_pedido, p.produto as pedido_produto
        FROM problemas pr
        JOIN clientes c ON pr.cliente_id = c.id
        LEFT JOIN pedidos p ON pr.pedido_id = p.id
        WHERE 1=1
        """
        params = []
        if status and status != "Todos":
            query += " AND pr.status = ?"
            params.append(status)
        if prioridade and prioridade != "Todas":
            query += " AND pr.prioridade = ?"
            params.append(prioridade)
        if search:
            s = f"%{search.strip()}%"
            query += " AND (pr.tipo_problema LIKE ? OR pr.descricao LIKE ? OR c.nome LIKE ? OR p.codigo_pedido LIKE ?)"
            params.extend([s, s, s, s])
            
        query += " ORDER BY pr.id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_problema_by_id(problema_id: int) -> dict:
    """Retorna um problema específico pelo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT pr.*, c.nome as cliente_nome, c.email as cliente_email, p.codigo_pedido, p.produto as pedido_produto
        FROM problemas pr
        JOIN clientes c ON pr.cliente_id = c.id
        LEFT JOIN pedidos p ON pr.pedido_id = p.id
        WHERE pr.id = ?
        """, (problema_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_problema(cliente_id: int, tipo_problema: str, descricao: str, pedido_id: int = None, status: str = "Aberto", prioridade: str = "Média") -> int:
    """Registra uma nova ocorrência ou problema de pós-venda."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO problemas (cliente_id, pedido_id, tipo_problema, descricao, status, prioridade)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (cliente_id, pedido_id if pedido_id else None, tipo_problema.strip(), descricao.strip(), status.strip(), prioridade.strip()))
        conn.commit()
        return cursor.lastrowid

def update_problema(problema_id: int, tipo_problema: str, descricao: str, status: str, prioridade: str, pedido_id: int = None) -> bool:
    """Atualiza o status e dados de um problema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE problemas
        SET tipo_problema = ?, descricao = ?, status = ?, prioridade = ?, pedido_id = ?
        WHERE id = ?
        """, (tipo_problema.strip(), descricao.strip(), status.strip(), prioridade.strip(), pedido_id if pedido_id else None, problema_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_problema(problema_id: int) -> bool:
    """Remove um registro de problema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM problemas WHERE id = ?", (problema_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==========================================
# CRUD - ATENDIMENTOS
# ==========================================

def get_atendimentos(status: str = None, canal: str = None, search: str = None) -> list:
    """Retorna tickets de atendimento com dados de cliente e pedido."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
        SELECT a.*, c.nome as cliente_nome, c.email as cliente_email, c.telefone as cliente_telefone, p.codigo_pedido
        FROM atendimentos a
        JOIN clientes c ON a.cliente_id = c.id
        LEFT JOIN pedidos p ON a.pedido_id = p.id
        WHERE 1=1
        """
        params = []
        if status and status != "Todos":
            query += " AND a.status = ?"
            params.append(status)
        if canal and canal != "Todos":
            query += " AND a.canal = ?"
            params.append(canal)
        if search:
            s = f"%{search.strip()}%"
            query += " AND (a.assunto LIKE ? OR a.mensagem_cliente LIKE ? OR c.nome LIKE ? OR p.codigo_pedido LIKE ?)"
            params.extend([s, s, s, s])
            
        query += " ORDER BY a.id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_atendimento_by_id(atendimento_id: int) -> dict:
    """Retorna um ticket de atendimento pelo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT a.*, c.nome as cliente_nome, c.email as cliente_email, c.telefone as cliente_telefone, p.codigo_pedido, p.produto as pedido_produto, p.codigo_rastreio
        FROM atendimentos a
        JOIN clientes c ON a.cliente_id = c.id
        LEFT JOIN pedidos p ON a.pedido_id = p.id
        WHERE a.id = ?
        """, (atendimento_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_atendimento(cliente_id: int, canal: str, assunto: str, mensagem_cliente: str, resposta_enviada: str = "", pedido_id: int = None, status: str = "Pendente", sentimento: str = "Neutro") -> int:
    """Cria um novo ticket de atendimento."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO atendimentos (cliente_id, pedido_id, canal, assunto, mensagem_cliente, resposta_enviada, status, sentimento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente_id, pedido_id if pedido_id else None, canal.strip(), assunto.strip(), mensagem_cliente.strip(), resposta_enviada.strip() if resposta_enviada else None, status.strip(), sentimento.strip()))
        conn.commit()
        return cursor.lastrowid

def update_atendimento(atendimento_id: int, canal: str, assunto: str, mensagem_cliente: str, resposta_enviada: str, status: str, sentimento: str, pedido_id: int = None) -> bool:
    """Atualiza ou responde a um ticket de atendimento."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE atendimentos
        SET canal = ?, assunto = ?, mensagem_cliente = ?, resposta_enviada = ?, status = ?, sentimento = ?, pedido_id = ?
        WHERE id = ?
        """, (canal.strip(), assunto.strip(), mensagem_cliente.strip(), resposta_enviada.strip() if resposta_enviada else None, status.strip(), sentimento.strip(), pedido_id if pedido_id else None, atendimento_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_atendimento(atendimento_id: int) -> bool:
    """Remove um ticket de atendimento."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM atendimentos WHERE id = ?", (atendimento_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==========================================
# CRUD - RESPOSTAS PRONTAS
# ==========================================

def get_respostas_prontas(categoria: str = None, search: str = None) -> list:
    """Retorna templates de respostas prontas."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM respostas_prontas WHERE 1=1"
        params = []
        if categoria and categoria != "Todas":
            query += " AND categoria = ?"
            params.append(categoria)
        if search:
            s = f"%{search.strip()}%"
            query += " AND (titulo LIKE ? OR conteudo LIKE ? OR atalho LIKE ?)"
            params.extend([s, s, s])
        query += " ORDER BY categoria ASC, titulo ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_resposta_pronta_by_id(resposta_id: int) -> dict:
    """Retorna um template pelo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM respostas_prontas WHERE id = ?", (resposta_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_resposta_pronta(titulo: str, categoria: str, conteudo: str, atalho: str = "") -> int:
    """Cria um novo template de resposta pronta."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO respostas_prontas (titulo, categoria, conteudo, atalho)
        VALUES (?, ?, ?, ?)
        """, (titulo.strip(), categoria.strip(), conteudo.strip(), atalho.strip() if atalho else None))
        conn.commit()
        return cursor.lastrowid

def update_resposta_pronta(resposta_id: int, titulo: str, categoria: str, conteudo: str, atalho: str) -> bool:
    """Atualiza um template de resposta pronta."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE respostas_prontas
        SET titulo = ?, categoria = ?, conteudo = ?, atalho = ?
        WHERE id = ?
        """, (titulo.strip(), categoria.strip(), conteudo.strip(), atalho.strip() if atalho else None, resposta_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_resposta_pronta(resposta_id: int) -> bool:
    """Remove um template de resposta pronta."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM respostas_prontas WHERE id = ?", (resposta_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==========================================
# BUSCA GLOBAL & MÉTRICAS (KPIS)
# ==========================================

def search_global(query_str: str) -> dict:
    """Executa busca global em todas as entidades do sistema."""
    if not query_str or len(query_str.strip()) < 2:
        return {"clientes": [], "pedidos": [], "problemas": [], "atendimentos": [], "respostas": []}
    
    q = query_str.strip()
    return {
        "clientes": get_clientes(search=q),
        "pedidos": get_pedidos(search=q),
        "problemas": get_problemas(search=q),
        "atendimentos": get_atendimentos(search=q),
        "respostas": get_respostas_prontas(search=q)
    }

def get_kpis() -> dict:
    """Calcula indicadores-chave de desempenho para o dashboard."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Total e faturamento de pedidos
        cursor.execute("""
        SELECT 
            COUNT(*) as total_pedidos,
            COALESCE(SUM(valor_total), 0) as faturamento_total,
            COALESCE(AVG(valor_total), 0) as ticket_medio,
            SUM(CASE WHEN status = 'Entregue' THEN 1 ELSE 0 END) as pedidos_entregues,
            SUM(CASE WHEN status = 'Pendente' THEN 1 ELSE 0 END) as pedidos_pendentes,
            SUM(CASE WHEN status = 'Enviado' THEN 1 ELSE 0 END) as pedidos_enviados,
            SUM(CASE WHEN status = 'Cancelado' THEN 1 ELSE 0 END) as pedidos_cancelados
        FROM pedidos
        """)
        pedidos_kpi = dict(cursor.fetchone())
        
        # Problemas
        cursor.execute("""
        SELECT 
            COUNT(*) as total_problemas,
            SUM(CASE WHEN status = 'Aberto' THEN 1 ELSE 0 END) as problemas_abertos,
            SUM(CASE WHEN status = 'Em Análise' THEN 1 ELSE 0 END) as problemas_analise,
            SUM(CASE WHEN status = 'Resolvido' THEN 1 ELSE 0 END) as problemas_resolvidos,
            SUM(CASE WHEN prioridade = 'Urgente' AND status != 'Resolvido' THEN 1 ELSE 0 END) as problemas_urgentes
        FROM problemas
        """)
        problemas_kpi = dict(cursor.fetchone())
        
        # Atendimentos
        cursor.execute("""
        SELECT 
            COUNT(*) as total_atendimentos,
            SUM(CASE WHEN status = 'Pendente' THEN 1 ELSE 0 END) as atendimentos_pendentes,
            SUM(CASE WHEN status = 'Respondido' THEN 1 ELSE 0 END) as atendimentos_respondidos,
            SUM(CASE WHEN status = 'Fechado' THEN 1 ELSE 0 END) as atendimentos_fechados
        FROM atendimentos
        """)
        atendimentos_kpi = dict(cursor.fetchone())
        
        # Total Clientes
        cursor.execute("SELECT COUNT(*) as total_clientes FROM clientes")
        total_clientes = cursor.fetchone()["total_clientes"]
        
        # Taxa de resolução
        total_prob = problemas_kpi["total_problemas"]
        taxa_resolucao = (problemas_kpi["problemas_resolvidos"] / total_prob * 100) if total_prob > 0 else 100.0

        return {
            **pedidos_kpi,
            **problemas_kpi,
            **atendimentos_kpi,
            "total_clientes": total_clientes,
            "taxa_resolucao": round(taxa_resolucao, 1)
        }
