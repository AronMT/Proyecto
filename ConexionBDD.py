import pandas as pd
import mysql.connector

# Cargar los datasets
laliga_df = pd.read_csv('C:/Users/Aron/Downloads/ProyectoLigas (1)/laliga.csv')
seriea_df = pd.read_csv('C:/Users/Aron/Downloads/ProyectoLigas (1)/seriea.csv')
premier_df = pd.read_csv('C:/Users/Aron/Downloads/ProyectoLigas (1)/premierleague.csv')

# Conexión a la base de datos MySQL
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345',
    database='ligas',
    auth_plugin='mysql_native_password'
)

cursor = connection.cursor()

# Borrar tablas si existen
cursor.execute('DROP TABLE IF EXISTS Equipo_Temporada')
cursor.execute('DROP TABLE IF EXISTS Equipo')
cursor.execute('DROP TABLE IF EXISTS Temporada')
cursor.execute('DROP TABLE IF EXISTS Liga')

# Crear la tabla Liga
cursor.execute('''
CREATE TABLE Liga (
    idLiga INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
)
''')

# Crear la tabla Equipo
cursor.execute('''
CREATE TABLE Equipo (
    idEquipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    idLiga INT,
    FOREIGN KEY (idLiga) REFERENCES Liga(idLiga)
)
''')

# Crear la tabla Temporada
cursor.execute('''
CREATE TABLE Temporada (
    idTemporada INT AUTO_INCREMENT PRIMARY KEY,
    Temporada VARCHAR(255) NOT NULL
)
''')

# Crear la tabla Equipo_Temporada
cursor.execute('''
CREATE TABLE Equipo_Temporada (
    idEquipo_Temporada INT AUTO_INCREMENT PRIMARY KEY,
    JJ INT,
    JG INT,
    JE INT,
    JP INT,
    GF INT,
    GC INT,
    DF INT,
    PTS INT,
    idEquipo INT,
    idTemporada INT,
    FOREIGN KEY (idEquipo) REFERENCES Equipo(idEquipo),
    FOREIGN KEY (idTemporada) REFERENCES Temporada(idTemporada)
)
''')

connection.commit()

# Insertar datos en la tabla Liga
def insert_liga(connection):
    cursor = connection.cursor()
    ligas = ['La Liga', 'Serie A', 'Premier League']
    for liga in ligas:
        cursor.execute('INSERT INTO Liga (nombre) VALUES (%s)', (liga,))
    connection.commit()

insert_liga(connection)

# Insertar datos en la tabla Equipo
def insert_equipo(dataframe, liga, connection):
    cursor = connection.cursor()
    equipos = dataframe['Equipo'].unique()
    for equipo in equipos:
        cursor.execute('''
        INSERT INTO Equipo (nombre, idLiga) 
        VALUES (%s, (SELECT idLiga FROM Liga WHERE nombre=%s))
        ''', (equipo, liga))
    connection.commit()

insert_equipo(laliga_df, 'La Liga', connection)
insert_equipo(seriea_df, 'Serie A', connection)
insert_equipo(premier_df, 'Premier League', connection)

# Insertar datos en la tabla Temporada
def insert_temporada(dataframe, connection):
    cursor = connection.cursor()
    temporadas = dataframe['Temporada'].unique()
    for temporada in temporadas:
        cursor.execute('INSERT INTO Temporada (Temporada) VALUES (%s)', (temporada,))
    connection.commit()

insert_temporada(laliga_df, connection)
insert_temporada(seriea_df, connection)
insert_temporada(premier_df, connection)

# Insertar datos en la tabla Equipo_Temporada
def insert_equipo_temporada(dataframe, connection):
    cursor = connection.cursor()
    for _, row in dataframe.iterrows():
        cursor.execute('''
        INSERT INTO Equipo_Temporada (JJ, JG, JE, JP, GF, GC, DF, PTS, idEquipo, idTemporada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 
                (SELECT idEquipo FROM Equipo WHERE nombre=%s LIMIT 1),
                (SELECT idTemporada FROM Temporada WHERE Temporada=%s LIMIT 1))
        ''', (row['JJ'], row['JG'], row['JE'], row['JP'], row['GF'], row['GC'], row['DF'], row['PTS'], row['Equipo'], row['Temporada']))
    connection.commit()

insert_equipo_temporada(laliga_df, connection)
insert_equipo_temporada(seriea_df, connection)
insert_equipo_temporada(premier_df,connection)

# Cerrar la conexión
connection.close()
