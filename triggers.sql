-- ======== GATILHOS DE VALIDAÇÃO ======== 

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
create trigger validacao_data_devolucao_real
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



