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
        COALESCE(OLD.Status_emprestimo,''),
        NULL,
        OLD.Usuario_id,
        OLD.ID_emprestimo
    );
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER log_emprestimo_update_datas
AFTER UPDATE ON Emprestimos
FOR EACH ROW
BEGIN
    IF COALESCE(OLD.Data_devolucao_prevista,'0000-00-00') <> COALESCE(NEW.Data_devolucao_prevista,'0000-00-00') THEN
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
    END IF;
    IF COALESCE(OLD.Data_devolucao_real,'0000-00-00') <> COALESCE(NEW.Data_devolucao_real,'0000-00-00') THEN
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
END //

DELIMITER ;

DELETE FROM Emprestimos WHERE ID_emprestimo = 8;

DROP TRIGGER log_emprestimo_delete;
DROP TRIGGER log_emprestimo_update_datas;
