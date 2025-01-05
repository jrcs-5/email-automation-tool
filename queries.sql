CREATE DATABASE Recordatorios;

USE Recordatorios;

CREATE TABLE Cliente (
    IdCliente INT PRIMARY KEY IDENTITY(1,1),
    Nombre VARCHAR(80) NOT NULL,
    Apellido VARCHAR(80) NOT NULL,
    Email VARCHAR(50) NOT NULL
);

CREATE TABLE Texto (
    IdTexto INT PRIMARY KEY IDENTITY(1,1),
    Asunto VARCHAR(50),
    Mensaje VARCHAR(1000) NOT NULL,
    Fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE Mensaje (
    IdCliente INT REFERENCES Cliente(IdCliente),
    IdTexto INT REFERENCES Texto(IdTexto),
    Estado VARCHAR(20) DEFAULT 'pendiente' CHECK Estado IN ('pendiente', 'enviado', 'fallido'),
    PRIMARY KEY (IdCliente, IdTexto)
);




