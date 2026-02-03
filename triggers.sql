-- ============================================================
-- ================== GATILHOS DE VALIDAÇÃO ===================
-- ============================================================

-- Impede novo empréstimo se o usuário já possuir empréstimo atrasado
DELIMITER //
CREATE TRIGGER validacao_emprestimo_atrasado 
BEFORE INSERT ON Emprestimos
FOR EACH ROW
BEGIN	
	DECLARE emprestimo_status VARCHAR(50);
    
    SELECT Status_emprestimo
    INTO emprestimo_status
    FROM Emprestimos	
    WHERE Usuario_id = NEW.Usuario_id
      AND Status_emprestimo = 'atrasado';
    
    IF emprestimo_status IS NOT NULL THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Há um empréstimo atrasado! Conclua-o primeiro.';
	END IF;
END //
DELIMITER ;

-- Impede cadastro de livros com quantidade negativa
DELIMITER //
CREATE TRIGGER validacao_qtd_livro 
BEFORE INSERT ON Livros
FOR EACH ROW		
BEGIN
	IF NEW.Quantidade_disponivel < 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantidade de livros não pode ser negativa';
	END IF;
END //
DELIMITER ;

-- Impede data de devolução prevista anterior à data do empréstimo
DELIMITER //
CREATE TRIGGER validacao_data_devolucao 
BEFORE INSERT ON Emprestimos
FOR EACH ROW
BEGIN
	IF NEW.Data_devolucao_prevista < NEW.Data_emprestimo THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Data de devolução inconsistente';
	END IF;
END //
DELIMITER ;

-- Impede data de devolução real anterior à data do empréstimo
DELIMITER //
CREATE TRIGGER validacao_data_devolucao_real 
BEFORE UPDATE ON Emprestimos
FOR EACH ROW 
BEGIN 
	IF NEW.Data_devolucao_real < NEW.Data_emprestimo THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Data de devolução inconsistente';
	END IF;
END //
DELIMITER ;

-- Impede ano de publicação maior que o ano atual
DELIMITER //
CREATE TRIGGER validacao_ano_publicacao
BEFORE INSERT ON Livros
FOR EACH ROW 
BEGIN 
	IF NEW.Ano_publicacao > YEAR(NOW()) THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Data de publicação inválida';
    END IF;
END //
DELIMITER ;


-- ============================================================
-- ===== GATILHOS DE ATUALIZAÇÃO AUTOMÁTICA PÓS-EVENTO =========
-- ============================================================

-- Atualiza a multa do usuário quando há devolução com atraso
DELIMITER //
CREATE TRIGGER devolucao_atraso_atualizar_multa 
AFTER UPDATE ON Emprestimos
FOR EACH ROW 
BEGIN 
	DECLARE multa INT;
    
    SET multa = calcular_multa(
        NEW.Data_devolucao_prevista,
        NEW.Data_devolucao_real
    );	
    
	IF NEW.Data_devolucao_real IS NOT NULL
       AND NEW.Data_devolucao_real > NEW.Data_devolucao_prevista THEN
        UPDATE Usuarios 
        SET Multa_atual = Multa_atual + multa
        WHERE ID_usuario = NEW.Usuario_id;
    END IF;
END //
DELIMITER ;

-- Aumenta quantidade do livro ao excluir empréstimo não devolvido
DELIMITER //
CREATE TRIGGER aumentar_quantidade_excluir_emprestimo
AFTER DELETE ON Emprestimos
FOR EACH ROW
BEGIN
	IF OLD.Status_emprestimo <> 'devolvido' THEN
		UPDATE Livros
		SET Quantidade_disponivel = Quantidade_disponivel + 1
		WHERE ID_livro = OLD.Livro_id;
	END IF;
END //
DELIMITER ;

-- Cancela empréstimos pendentes ao excluir um livro
DELIMITER //
CREATE TRIGGER excluir_livro_cancelar_emprestimos_pendentes 
BEFORE DELETE ON Livros
FOR EACH ROW 
BEGIN 
	UPDATE Emprestimos 
    SET Status_emprestimo = 'cancelado', Livro_id = NULL
	WHERE Livro_id = OLD.ID_livro
      AND Status_emprestimo = 'pendente';
END //
DELIMITER ;

-- Aumenta quantidade do livro ao marcar empréstimo como devolvido
DELIMITER //
CREATE TRIGGER aumentar_quantidade_devolver_emprestimo
AFTER UPDATE ON Emprestimos
FOR EACH ROW
BEGIN
	IF OLD.Status_emprestimo <> 'devolvido'
	   AND NEW.Status_emprestimo = 'devolvido' THEN
		UPDATE Livros
		SET Quantidade_disponivel = Quantidade_disponivel + 1
		WHERE ID_livro = OLD.Livro_id;
	END IF;
END //
DELIMITER ;

-- Diminui quantidade do livro ao realizar empréstimo
DELIMITER //
CREATE TRIGGER diminuir_quantidade_emprestar_livro
AFTER INSERT ON Emprestimos
FOR EACH ROW
BEGIN 
	UPDATE Livros
    SET Quantidade_disponivel = Quantidade_disponivel - 1
    WHERE ID_livro = NEW.Livro_id;
END //
DELIMITER ;


-- ============================================================
-- ========= GATILHOS DE GERAÇÃO AUTOMÁTICA DE VALORES =========
-- ============================================================

-- Define data de inscrição do usuário automaticamente
DELIMITER //
CREATE TRIGGER preencher_data_incricao 
BEFORE INSERT ON Usuarios
FOR EACH ROW 
BEGIN 
	SET NEW.Data_inscricao = CURDATE();
END //
DELIMITER ;

-- Define status inicial do empréstimo como pendente
DELIMITER //
CREATE TRIGGER definir_emprestimo_pendente 
BEFORE INSERT ON Emprestimos
FOR EACH ROW
BEGIN 
	SET NEW.Status_emprestimo = 'pendente';
END //
DELIMITER ;

-- Preenche data de devolução real e ajusta status automaticamente
DELIMITER //
CREATE TRIGGER definir_devolucao_real
BEFORE UPDATE ON Emprestimos
FOR EACH ROW
BEGIN 
	IF OLD.Status_emprestimo <> 'devolvido'
       AND NEW.Status_emprestimo = 'devolvido' THEN
		SET NEW.Data_devolucao_real = CURDATE();
    ELSEIF NEW.Data_devolucao_real IS NOT NULL
       AND OLD.Data_devolucao_real IS NULL THEN
        SET NEW.Status_emprestimo = 'devolvido';
	END IF;
END //
DELIMITER ;

-- Define data de devolução prevista automaticamente (+30 dias)
DELIMITER //
CREATE TRIGGER definir_devolucao_prevista
BEFORE INSERT ON Emprestimos
FOR EACH ROW
BEGIN 
	SET NEW.Data_devolucao_prevista = data_devolucao_prevista(NEW.Data_emprestimo);
END //
DELIMITER ;

-- Inicializa multa do usuário com valor zero
DELIMITER //
CREATE TRIGGER definir_multa_inicial
BEFORE INSERT ON Usuarios
FOR EACH ROW
BEGIN 
	SET NEW.Multa_atual = 0;
END //
DELIMITER ;






-- ============================================================
-- =========                 FUNÇÕES                    =========
-- ============================================================

-- 1. Definir a data de devolução prevista
DELIMITER //

CREATE FUNCTION data_devolucao_prevista(data_emprestimo DATE)
RETURNS DATE

BEGIN
	DECLARE nova_data DATE;
    SET nova_data = data_emprestimo + INTERVAL 30 DAY;
    
    
    RETURN nova_data;
END//

DELIMITER ;


-- 2. calcular multa

DELIMITER //

CREATE FUNCTION calcular_multa(data_prevista DATE,data_real DATE)
RETURNS INT

BEGIN
    DECLARE dias_atraso INT;
    DECLARE valor_multa INT;

    SET dias_atraso = 0;
    SET valor_multa = 0;

    IF data_real IS NOT NULL
       AND data_real > data_prevista THEN

        SET dias_atraso = DATEDIFF(data_real, data_prevista);
        SET valor_multa = dias_atraso * 2; 
    END IF;

    RETURN valor_multa;
END//

DELIMITER ;
