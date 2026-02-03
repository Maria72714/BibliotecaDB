-- ============================================================
-- ======================= GATILHOS DE LOG ====================
-- ============================================================



-- ============================================================
-- LOG DE EMPRÉSTIMOS
-- ============================================================

-- Registra a criação de um novo empréstimo
DELIMITER //
CREATE TRIGGER log_emprestimo_insert 
AFTER INSERT ON Emprestimos
FOR EACH ROW
BEGIN
    INSERT INTO Log_Emprestimos
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id, Emprestimo_id)
    VALUES
    (
        NOW(),
        'INSERT',
        'Emprestimo',
        NULL,
        COALESCE(NEW.Status_emprestimo, 'pendente'),
        NEW.Usuario_id,
        NEW.ID_emprestimo
    );
END//
DELIMITER ;

-- Registra alterações relevantes em campos do empréstimo
DELIMITER //
CREATE TRIGGER log_emprestimo_update 
AFTER UPDATE ON Emprestimos
FOR EACH ROW
BEGIN
    IF NOT (OLD.Status_emprestimo <=> NEW.Status_emprestimo) THEN
        INSERT INTO Log_Emprestimos
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id,Emprestimo_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Status_emprestimo',
            OLD.Status_emprestimo,
            NEW.Status_emprestimo,
            NEW.Usuario_id,
            NEW.ID_emprestimo
        );

    ELSEIF NOT (OLD.Data_devolucao_prevista <=> NEW.Data_devolucao_prevista) THEN
        INSERT INTO Log_Emprestimos
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id, Emprestimo_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Data_devolucao_prevista',
            OLD.Data_devolucao_prevista,
            NEW.Data_devolucao_prevista,
            NEW.Usuario_id,
            NEW.ID_emprestimo
        );
    
    ELSEIF NOT (OLD.Data_devolucao_real <=> NEW.Data_devolucao_real) THEN
        INSERT INTO Log_Emprestimos
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id, Emprestimo_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Data_devolucao_real',
            OLD.Data_devolucao_real,
            NEW.Data_devolucao_real,
            NEW.Usuario_id,
            NEW.ID_emprestimo
        );
    END IF;
END//
DELIMITER ;

-- Registra a exclusão de um empréstimo
DELIMITER //
CREATE TRIGGER log_emprestimo_delete 
AFTER DELETE ON Emprestimos
FOR EACH ROW
BEGIN
    INSERT INTO Log_Emprestimos
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id, Emprestimo_id)
    VALUES
    (
        NOW(),
        'DELETE',
        'Emprestimo',
        OLD.Status_emprestimo,
        NULL,
        OLD.Usuario_id,
        OLD.ID_emprestimo
    );
END//
DELIMITER ;


-- ============================================================
-- LOG DE LIVROS
-- ============================================================

-- Registra a criação de um novo livro
DELIMITER //
CREATE TRIGGER log_livro_insert 
AFTER INSERT ON Livros
FOR EACH ROW
BEGIN
    INSERT INTO Log_Livros
    (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(), 'INSERT', NEW.ID_livro, 'Livro', NULL, NEW.Titulo);
END//
DELIMITER ;

-- Registra alterações relevantes nos dados do livro
DELIMITER //
CREATE TRIGGER log_livro_update 
AFTER UPDATE ON Livros
FOR EACH ROW
BEGIN
    IF OLD.Quantidade_disponivel <> NEW.Quantidade_disponivel THEN
        INSERT INTO Log_Livros
        (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), 'UPDATE', NEW.ID_livro, 'Quantidade_disponivel', OLD.Quantidade_disponivel, NEW.Quantidade_disponivel);

    ELSEIF OLD.Titulo <> NEW.Titulo THEN
        INSERT INTO Log_Livros
        (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), 'UPDATE', NEW.ID_livro, 'Titulo', OLD.Titulo, NEW.Titulo);

    ELSEIF OLD.ISBN <> NEW.ISBN THEN
        INSERT INTO Log_Livros
        (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), 'UPDATE', NEW.ID_livro, 'ISBN', OLD.ISBN, NEW.ISBN);

    ELSEIF OLD.Ano_publicacao <> NEW.Ano_publicacao THEN
        INSERT INTO Log_Livros
        (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), 'UPDATE', NEW.ID_livro, 'Ano_publicacao', OLD.Ano_publicacao, NEW.Ano_publicacao);

     ELSEIF OLD.Resumo <> NEW.Resumo THEN
        INSERT INTO Log_Livros
        (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), 'UPDATE', NEW.ID_livro, 'Resumo', OLD.Resumo, NEW.Resumo);
    END IF;
END//
DELIMITER ;

-- Registra a exclusão de um livro
DELIMITER //
CREATE TRIGGER log_livro_delete 
BEFORE DELETE ON Livros
FOR EACH ROW
BEGIN
    INSERT INTO Log_Livros
    (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(), 'DELETE', OLD.ID_livro, 'Livro', OLD.Titulo, NULL);
END//
DELIMITER ;