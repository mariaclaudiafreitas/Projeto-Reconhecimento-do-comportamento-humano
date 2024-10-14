USE emocao;
CREATE TABLE emocao_contagem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emocao VARCHAR(255) NOT NULL,
    contagem INT NOT NULL
);
SHOW TABLES;
SHOW DATABASES;
SELECT * FROM emocao_contagem;
SELECT DISTINCT emocao FROM emocao_contagem;
SELECT emocao, SUM(contagem) AS total FROM emocao_contagem GROUP BY emocao;


CREATE TABLE confusion_matrix (
	id INT AUTO_INCREMENT PRIMARY KEY,
    emocao VARCHAR(20),
    happy FLOAT,
    sad FLOAT,
    neutral FLOAT
);

SHOW tables;
SELECT * FROM confusion_matrix;
SELECT DISTINCT emocao FROM confusion_matrix;
SELECT emocao, SUM(sad) AS total FROM confusion_matrix GROUP BY emocao;



DROP TABLE confusion_matrix;
