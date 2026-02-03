-- ============================================================
-- ======================= GATILHOS DE LOG ====================
-- ============================================================


-- ============================================================
-- LOG DE USUÁRIOS
-- ============================================================

-- Registra a criação de um novo usuário
DELIMITER //
CREATE TRIGGER log_usuario_insert 
AFTER INSERT ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Usuarios
    (Data_log, Operacao, Usuario_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(), 'INSERT', NEW.ID_usuario, 'Usuario', NULL, NEW.Nome_usuario);
END//
DELIMITER ;

-- Registra alterações relevantes nos dados do usuário
DELIMITER //
CREATE TRIGGER log_usuario_update
AFTER UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    IF NOT (OLD.Nome_usuario <=> NEW.Nome_usuario) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Nome_usuario',OLD.Nome_usuario,NEW.Nome_usuario,NEW.ID_usuario);

    ELSEIF NOT (OLD.Email <=> NEW.Email) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Email',OLD.Email,NEW.Email,NEW.ID_usuario);

    ELSEIF NOT (OLD.Numero_telefone <=> NEW.Numero_telefone) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Numero_telefone',OLD.Numero_telefone,NEW.Numero_telefone,NEW.ID_usuario);

    ELSEIF NOT (OLD.Data_inscricao <=> NEW.Data_inscricao) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Data_inscricao',OLD.Data_inscricao,NEW.Data_inscricao,NEW.ID_usuario);

    ELSEIF NOT (OLD.Multa_atual <=> NEW.Multa_atual) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Multa_atual',OLD.Multa_atual,NEW.Multa_atual,NEW.ID_usuario);

        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Multa_atual',OLD.Multa_atual,NEW.Multa_atual,NEW.ID_usuario);
    END IF;
END//
DELIMITER ;

-- Registra a exclusão de um usuário e sua multa, se existir
DELIMITER //
CREATE TRIGGER log_usuario_delete
AFTER DELETE ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Usuarios
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (NOW(),'DELETE','Usuario',OLD.Nome_usuario,NULL,OLD.ID_usuario);

    IF COALESCE(OLD.Multa_atual, 0) <> 0 THEN
        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'DELETE','Multa_atual',OLD.Multa_atual,NULL,OLD.ID_usuario);
    END IF;
END //
DELIMITER ;


-- ============================================================
-- LOG DE MULTAS
-- ============================================================

-- Registra a criação de uma multa
DELIMITER //
CREATE TRIGGER log_multa_insert
AFTER INSERT ON Usuarios    
FOR EACH ROW
BEGIN
    INSERT INTO Log_Multas
    (Data_log, Operacao, Usuario_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(),'INSERT', NEW.ID_usuario, 'Multa', NULL, COALESCE(NEW.Multa_atual, NULL));
END//
DELIMITER ;

-- Registra atualização do valor da multa
DELIMITER //
CREATE TRIGGER log_multa_update
AFTER UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    IF COALESCE(OLD.Multa_atual, 0) <> COALESCE(NEW.Multa_atual, 0) THEN
        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (NOW(),'UPDATE','Multa',COALESCE(OLD.Multa_atual, NULL),
         COALESCE(NEW.Multa_atual, NULL),
         NEW.ID_usuario);
    END IF;
END//
DELIMITER ;

-- Registra a exclusão de uma multa
DELIMITER //
CREATE TRIGGER log_multa_delete
AFTER DELETE ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Multas
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (NOW(),'DELETE','Multa',COALESCE(OLD.Multa_atual, NULL),NULL,OLD.ID_usuario);
END//
DELIMITER ;
