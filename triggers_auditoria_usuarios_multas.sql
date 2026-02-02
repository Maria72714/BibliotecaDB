DELIMITER //
DROP TRIGGER IF EXISTS log_usuario_insert//
CREATE TRIGGER log_usuario_insert
AFTER INSERT ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Usuarios
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (
        NOW(),
        'INSERT',
        'Usuario',
        NULL,
        NEW.Nome_usuario,
        NEW.ID_usuario
    );
END//

DROP TRIGGER IF EXISTS log_usuario_update//
CREATE TRIGGER log_usuario_update
AFTER UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    IF COALESCE(OLD.Nome_usuario,'') <> COALESCE(NEW.Nome_usuario,'') THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Nome_usuario',
            OLD.Nome_usuario,
            NEW.Nome_usuario,
            NEW.ID_usuario
        );
    END IF;
    IF COALESCE(OLD.Email,'') <> COALESCE(NEW.Email,'') THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Email',
            OLD.Email,
            NEW.Email,
            NEW.ID_usuario
        );
    END IF;
    IF COALESCE(OLD.Numero_telefone,'') <> COALESCE(NEW.Numero_telefone,'') THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Numero_telefone',
            OLD.Numero_telefone,
            NEW.Numero_telefone,
            NEW.ID_usuario
        );
    END IF;
    IF COALESCE(OLD.Data_inscricao,'0000-00-00') <> COALESCE(NEW.Data_inscricao,'0000-00-00') THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Data_inscricao',
            OLD.Data_inscricao,
            NEW.Data_inscricao,
            NEW.ID_usuario
        );
    END IF;
    IF COALESCE(OLD.Multa_atual, 0) <> COALESCE(NEW.Multa_atual, 0) THEN
        INSERT INTO Log_Usuarios
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Multa_atual',
            OLD.Multa_atual,
            NEW.Multa_atual,
            NEW.ID_usuario
        );
        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Multa_atual',
            OLD.Multa_atual,
            NEW.Multa_atual,
            NEW.ID_usuario
        );
    END IF;
END//

DROP TRIGGER IF EXISTS log_usuario_delete//
CREATE TRIGGER log_usuario_delete
AFTER DELETE ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Usuarios
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (
        NOW(),
        'DELETE',
        'Usuario',
        OLD.Nome_usuario,
        NULL,
        OLD.ID_usuario
    );
    IF COALESCE(OLD.Multa_atual, 0) <> 0 THEN
        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'DELETE',
            'Multa_atual',
            OLD.Multa_atual,
            NULL,
            OLD.ID_usuario
        );
    END IF;
END//

DROP TRIGGER IF EXISTS log_multa_insert//
CREATE TRIGGER log_multa_insert
AFTER INSERT ON Multas
FOR EACH ROW
BEGIN
    INSERT INTO Log_Multas
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (
        NOW(),
        'INSERT',
        'Multa',
        NULL,
        COALESCE(NEW.Valor_multa, NEW.Valor, NULL),
        NEW.Usuario_id
    );
END//

DROP TRIGGER IF EXISTS log_multa_update//
CREATE TRIGGER log_multa_update
AFTER UPDATE ON Multas
FOR EACH ROW
BEGIN
    IF COALESCE(OLD.Valor_multa, OLD.Valor, 0) <> COALESCE(NEW.Valor_multa, NEW.Valor, 0) THEN
        INSERT INTO Log_Multas
        (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
        VALUES
        (
            NOW(),
            'UPDATE',
            'Multa',
            COALESCE(OLD.Valor_multa, OLD.Valor, NULL),
            COALESCE(NEW.Valor_multa, NEW.Valor, NULL),
            COALESCE(NEW.Usuario_id, OLD.Usuario_id)
        );
    END IF;
END//

DROP TRIGGER IF EXISTS log_multa_delete//
CREATE TRIGGER log_multa_delete
AFTER DELETE ON Multas
FOR EACH ROW
BEGIN
    INSERT INTO Log_Multas
    (Data_log, Operacao, Campo, Valor_Anterior, Valor_Novo, Usuario_id)
    VALUES
    (
        NOW(),
        'DELETE',
        'Multa',
        COALESCE(OLD.Valor_multa, OLD.Valor, NULL),
        NULL,
        OLD.Usuario_id
    );
END//
DELIMITER ;
