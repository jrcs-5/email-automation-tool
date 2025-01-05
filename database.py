from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv



class Database:
    def __init__(self):
        load_dotenv()
        db_server = os.getenv("DB_SERVER")
        db_name = os.getenv("DB_NAME")
        
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_server};"
            f"DATABASE={db_name};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes"
        )
        
        self.connection_url = URL.create(
            "mssql+pyodbc", query={"odbc_connect": connection_string}
        )
        
        self.engine = create_engine(self.connection_url)
        self.Session = sessionmaker(bind=self.engine)
        print("Conexión a la base de datos establecida.")
            
    def get_session(self):
        try:
            return self.Session()
        except Exception as e:
            raise Exception(f"Error al iniciar sesión: {e}")
        
    def close(self):
        try:
            self.engine.dispose()
            print("Conexión a la base de datos cerrada.")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

    def test_connection(self):
        try:
            session = self.get_session()
            result = session.execute(text("SELECT name FROM sys.tables")).fetchall()
            print("Tablas en la base de datos:")
            for table in result:
                print(table[0])
            self.close()
        except Exception as e:
            print(f"Error al ejecutar la prueba de conexión: {e}")

    def get_reminders(self):
        """
            Obtiene los recordatorios que deben enviarse en la hora actual.
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT c.Email, t.Asunto, t.Mensaje, m.IdCliente, m.IdTexto
                    FROM Mensaje m
                    JOIN Cliente c ON m.IdCliente = c.IdCliente
                    JOIN Texto t ON m.IdTexto = t.IdTexto
                    WHERE m.Estado = 'pendiente'
                    AND t.Fecha < GETDATE()
                """
                results = session.execute(text(query)).fetchall()
                return results
        except Exception as e:
            print(f"Error al obtener los recordatorios: {e}")
            return []
        
    def get_texts(self):
        """
            Obtiene todos los mensajes
        """
        try:
            with self.get_session() as session:
                query = """
                    SELECT 
                        t.Asunto, 
                        t.Mensaje, 
                        t.Fecha,
                        COUNT(CASE WHEN m.Estado = 'pendiente' THEN 1 END) AS Pendientes,
                        COUNT(CASE WHEN m.Estado = 'fallido' THEN 1 END) AS Fallidos,
                        COUNT(CASE WHEN m.Estado = 'enviado' THEN 1 END) AS Enviados
                    FROM Mensaje m
                    JOIN Texto t ON m.IdTexto = t.IdTexto
                    GROUP BY t.IdTexto, t.Asunto, t.Mensaje, t.Fecha
                    ORDER BY t.Fecha DESC;
                """
                results = session.execute(text(query)).fetchall()
                return results
        except Exception as e:
            print(f"Error al obtener los recordatorios: {e}")
            return []
    
    def mark_as_sent(self, id_cliente, id_texto):
        """
            marca los recordatorios como enviados
        """
        try:
            with self.get_session() as session:
                query = """
                    UPDATE Mensaje
                    SET Estado = 'enviado'
                    WHERE IdCliente = :id_cliente AND IdTexto = :id_texto;
                """
                session.execute(
                    text(query), {"id_cliente": id_cliente, "id_texto": id_texto}
                )
                session.commit()
                print("Estado de recordatorios actualizado correctamente.")
        except Exception as e:
            print(f"Error al actualizar el estado de enviado: {e}")
            
    def mark_as_failed(self, id_cliente, id_texto):
        """
            Marca los recordatorios como fallidos.
        """
        try:
            with self.get_session() as session:
                query = """
                    UPDATE Mensaje
                    SET Estado = 'fallido'
                    WHERE IdCliente = :id_cliente AND IdTexto = :id_texto;
                """
                session.execute(
                    text(query), {"id_cliente": id_cliente, "id_texto": id_texto}
                )
                session.commit()
                print("Estado de recordatorios actualizado a fallido correctamente.")
        except Exception as e:
            print(f"Error al actualizar el estado de fallido: {e}")
        
    def get_clients(self):
        """
            Obtiene todos los clientes de la base de datos
        """
        try:
            with self.get_session() as session:
                query = "SELECT IdCliente, Nombre, Apellido, Email FROM Cliente;"
                results = session.execute(text(query)).fetchall()
                return results
        except Exception as e:
            print(f"Error al obtener los clientes: {e}")
            return []
        
    def add_text(self, subject, message, date):
        """
            Agrega un texto a la base de datos y devuelve el id del mensaje
        """
        try:
            with self.get_session() as session:
                query = """
                    INSERT INTO Texto (Asunto, Mensaje, Fecha)
                    OUTPUT INSERTED.IdTexto
                    VALUES (:asunto, :mensaje, :fecha);
                """
                result = session.execute(
                    text(query), {"asunto": subject, "mensaje": message, "fecha": date}
                ).fetchone()
                id_texto = result[0]  # Obtener el valor de IdTexto
                session.commit()
                return id_texto

        except Exception as e:
            print(f"Error al agregar el mensaje: {e}")
            return None
        
        
        
    def add_reminder(self, clients, id_texto, fecha):
        """
            Agrega los recordatorios a la base de datos
        """
        try:
            with self.get_session() as session:
                query = """
                    INSERT INTO Mensaje (IdCliente, IdTexto, Estado)
                    VALUES (:id_cliente, :id_texto, 'pendiente');
                """
                for client in clients:
                    id_cliente = client[0]
                    session.execute(
                        text(query), {"id_cliente": id_cliente, "id_texto": id_texto, "fecha": fecha}
                    )
                    session.commit()
                print("Recordatorio agregado correctamente.")
        except Exception as e:
            print(f"Error al agregar recordatorio: {e}")
    