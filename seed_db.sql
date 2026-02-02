-- Dados de exemplo
INSERT INTO Generos (Nome_genero) VALUES
('Ficção Científica'),
('Fantasia'),
('Mistério'),
('Não-ficção'),
('Tecnologia');

INSERT INTO Autores (Nome_autor, Nacionalidade, Data_nascimento, Biografia) VALUES
('Isaac Asimov', 'Russo-Americano', '1920-01-02', 'Autor de ficção científica.'),
('J. R. R. Tolkien', 'Britânico', '1892-01-03', 'Autor de fantasia.'),
('Agatha Christie', 'Britânica', '1890-09-15', 'Dama do crime.'),
('Yuval Noah Harari', 'Israelense', '1976-02-24', 'Historiador e autor de não-ficção.'),
('Robert C. Martin', 'Americano', '1952-12-05', 'Tio Bob, autor de Clean Code.');

INSERT INTO Editoras (Nome_editora, Endereco_editora) VALUES
('Editora Alfa', 'Rua A, 123'),
('Editora Beta', 'Av. B, 456'),
('Editora Gama', 'Praça C, 789');

INSERT INTO Livros (Titulo, Autor_id, ISBN, Ano_publicacao, Genero_id, Editora_id, Quantidade_disponivel, Resumo) VALUES
('Fundação', 1, '9780307292063', 1951, 1, 1, 5, 'Clássico da FC.'),
('O Senhor dos Anéis', 2, '9788578270698', 1954, 2, 2, 3, 'Épico de fantasia.'),
('Assassinato no Expresso do Oriente', 3, '9780062073495', 1934, 3, 2, 4, 'Mistério de Hercule Poirot.'),
('Sapiens', 4, '9780062316097', 2011, 4, 3, 6, 'Uma breve história da humanidade.'),
('Clean Code', 5, '9780132350884', 2008, 5, 1, 2, 'Práticas de código limpo.');

INSERT INTO Usuarios (Nome_usuario, Email, Senha, Numero_telefone, Data_inscricao, Multa_atual) VALUES
('Ana Souza', 'ana@example.com', NULL, '11999990001', '2024-01-15', 0.00),
('Bruno Lima', 'bruno@example.com', NULL, '21988880002', '2024-02-10', 5.50),
('Carla Menezes', 'carla@example.com', NULL, '31977770003', '2024-03-05', 0.00);

