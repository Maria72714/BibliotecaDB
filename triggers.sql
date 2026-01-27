-- ==================== GATILHOS DE VALIDAÇÃO ==================== 

-- usuario não pode cadastrar um emprestimo se tiver outro atrasado
delimiter //
create trigger validacao_emprestimo_atrasado -- feito
before insert on Emprestimos
for each row
begin	
	declare emprestimo_status varchar(50);
    
    select Status_emprestimo
    into emprestimo_status
    from Emprestimos	
    where Usuario_id = new.Usuario_id
    and Status_emprestimo = 'atrasado';
    
    if emprestimo_status is not null then
		signal sqlstate "45000"
        set message_text = "Há um empréstimo atrasado! Conclua-o primeiro.";
	end if;
end //
delimiter ;

-- o usuário não pode cadastrar uma quantidade negativa de livros
delimiter //
create trigger validacao_qtd_livro -- feito
before insert on Livros
for each row		
begin
	if new.Quantidade_disponivel < 0 then
		signal sqlstate "45000"
        set message_text = 'Quantidade de livros não pode ser negativa';
	end if;
end //
delimiter ;


-- a data de devolução prevista não pode ser anterior à data do empréstimo
delimiter //
create trigger validacao_data_devolucao -- feito
before insert on Emprestimos
for each row
begin
	if new.Data_devolucao_prevista < new.Data_emprestimo then
		signal sqlstate "45000"
		set message_text = "Data de devolução inconsistente";
	end if;
end //
delimiter ;


-- a data de devolução real não pode ser anterior à data do empréstimo ou à data de devolução prevista
delimiter //
create trigger validacao_data_devolucao_real --feito
before update on Emprestimos
for each row 
begin 
	if new.Data_devolucao_real < NOW() or new.Data_devolucao_real < old.Data_devolucao_prevista then
		signal sqlstate "45000"
		set message_text = "Data de devolução inconsistente";
	end if;
end //
delimiter ;


-- o valor da multa não pode ser negativo
-- ===== TIRA ESSE =====
delimiter //
create trigger validacao_valor_multa
before insert on usuarios
for each row 
begin 
	if new.Multa_atual < 0 then
		signal sqlstate "45000"
		set message_text = "Valor da multa não pode ser negativa";
    end if;
end //
delimiter ;



-- ==================== GATILHOS DE LOG ====================
-- Log INSERT em empréstimos
DELIMITER //
CREATE TRIGGER log_emprestimo_insert --feito
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

-- Log UPDATE de status do empréstimo 
CREATE TRIGGER log_emprestimo_update
AFTER UPDATE ON Emprestimos
FOR EACH ROW
BEGIN
    IF COALESCE(OLD.Status_emprestimo,'') <> COALESCE(NEW.Status_emprestimo,'') THEN
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
    END IF;
END//

-- Log DELETE em empréstimos
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

-- Log INSERT em livros
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

-- Log UPDATE em livros
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
    END IF;
END//
DELIMITER ;


-- Log DELETE em livros
DELIMITER //
CREATE TRIGGER log_livro_delete
AFTER DELETE ON Livros
FOR EACH ROW
BEGIN
    INSERT INTO Log_Livros
    (Data_log, Operacao, Livro_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(), 'DELETE', OLD.ID_livro, 'Livro', OLD.Titulo, NULL);
END//
DELIMITER ;


-- Log INSERT em usuários
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

-- Log UPDATE em usuários
DELIMITER //
CREATE TRIGGER log_usuario_update
AFTER UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    IF OLD.Email <> NEW.Email THEN
        INSERT INTO Log_Usuarios
        VALUES
        (NOW(), 'UPDATE', NEW.ID_usuario, 'Email', OLD.Email, NEW.Email);
    END IF;
END//
DELIMITER ;

-- Log DELETE em usuários
DELIMITER //	
CREATE TRIGGER log_usuario_delete
AFTER DELETE ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Log_Usuarios
    (Data_log, Operacao, Usuario_id, Campo, Valor_Anterior, Valor_Novo)
    VALUES
    (NOW(), 'DELETE', OLD.ID_usuario, 'Usuario', OLD.Nome_usuario, NULL);
END//
DELIMITER ;


-- Log UPDATE de multa
DELIMITER //
CREATE TRIGGER log_multa_update
AFTER UPDATE ON Usuarios
FOR EACH ROW
BEGIN
    IF OLD.Multa_atual <> NEW.Multa_atual THEN
        INSERT INTO Log_Multas
        (Data_log, Usuario_id, Valor_Anterior, Valor_Novo)
        VALUES
        (NOW(), NEW.ID_usuario, OLD.Multa_atual, NEW.Multa_atual);
    END IF;
END//

DELIMITER ;




-- ==================== GATILHOS DE ATUALIZAÇÃO AUTOMÁTICA PÓS-EVENTO====================:

-- Devolução com atraso => atualizar multa_atua
 DELIMITER //
 
 
CREATE TRIGGER devolucao_atraso_atualizar_multa 
AFTER UPDATE ON emprestimos
FOR EACH ROW 
BEGIN 
	DECLARE multa INT;
    
    SET multa = calcular_multa(
        NEW.data_devolucao_prevista,
        NEW.data_devolucao_real
    );	
    
	IF NEW.data_devolucao_real IS NOT NULL
		AND NEW.data_devolucao_real <> '0000-00-00'
        AND NEW.data_devolucao_real > NEW.data_devolucao_prevista THEN
        UPDATE Usuarios SET Multa_atual = Multa_atual + multa
        WHERE ID_usuario = NEW.Usuario_id;
		
    END IF;
END //
DELIMITER ;


-- Ao excluir emprestimo => aumentar a quantidade_disponivel

DELIMITER //

CREATE TRIGGER aumentar_quantidade_excluir_emprestimo
AFTER DELETE ON Emprestimos
FOR EACH ROW
BEGIN
	IF OLD.Status_emprestimo <> 'devolvido' THEN
		UPDATE Livros
		SET Quantidade_disponivel = Quantidade_disponivel + 1
		WHERE ID_livro = OLD.Livro_id;
	END IF ;
END //

DELIMITER ;


-- cancelar emprestimos ao excluir o livro
 
 DELIMITER //

CREATE TRIGGER excluir_livro_cancelar_emprestimos_pendentes 
BEFORE DELETE ON livros
FOR EACH ROW 
BEGIN 
	UPDATE Emprestimos SET Status_emprestimo = 'cancelado', Livro_ID = NULL
	WHERE Livro_id = OLD.ID_livro
    AND Status_emprestimo = 'pendente';
    
   
END //
DELIMITER ;

-- Ao devolver livro => aumentar a quantidade_disponivel
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
	END IF ;
END //

DELIMITER ;

-- Ao emprestar o livro => diminuir a quantidade_disponviel

DELIMITER //

CREATE TRIGGER DiminuirEmprestar
AFTER INSERT ON Emprestimos
FOR EACH ROW

BEGIN 
	UPDATE Livros
    SET Quantidade_disponivel = Quantidade_disponivel - 1
    WHERE ID_livro = NEW.Livro_id;

END //

DELIMITER ;



-- ===================== GATILHOS DE GERAÇÃO AUTOMÁTICA DE VALORES ====================:

-- preencher data inscrição

DELIMITER //

CREATE TRIGGER preencher_data_incricao 
BEFORE INSERT ON Usuarios
FOR EACH ROW 
BEGIN 
	SET NEW.Data_inscricao = CURDATE();
END //
DELIMITER ;


 DELIMITER //
 
 
-- Definir o status inicial do emprestimo como "pendente"

DELIMITER //

CREATE TRIGGER definir_emprestimo_pendente
BEFORE INSERT ON Emprestimos
FOR EACH ROW

BEGIN 
	SET NEW.Status_emprestimo = 'pendente';

END //

DELIMITER ;


-- Preencher  a data_devolucao_real automaticamente

DELIMITER //

CREATE TRIGGER definir_devolucao_real
BEFORE UPDATE ON Emprestimos
FOR EACH ROW

BEGIN 
	IF OLD.Status_emprestimo <> 'devolvido'
    AND NEW.Status_emprestimo = 'devolvido' THEN
		SET NEW.Data_devolucao_real = CURDATE();
	END IF;
END //

DELIMITER ;


-- Gerar a Data_devolução_prevista(+7 dias)

DELIMITER //

CREATE TRIGGER definir_devolucao_prevista
BEFORE INSERT ON Emprestimos
FOR EACH ROW

BEGIN 
	
	SET NEW.Data_devolucao_prevista = data_devolucao_prevista(NEW.Data_emprestimo);
	
END //

DELIMITER ;


DELIMITER //
CREATE TRIGGER definir_multa_inicial
BEFORE INSERT ON Usuarios
FOR EACH ROW

BEGIN 
	SET NEW.Multa_atual = 0;
END //

DELIMITER ;



-- ==================== FUNCTIONS ====================
-- FUNÇÕES TRIGGERS
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
       AND data_real <> '0000-00-00'
       AND data_real > data_prevista THEN

        SET dias_atraso = DATEDIFF(data_real, data_prevista);
        SET valor_multa = dias_atraso * 2; 
    END IF;

    RETURN valor_multa;
END//

DELIMITER ;
