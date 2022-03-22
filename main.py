from class_ApSystems import ApSystems
import configparser
import mysql.connector

config = configparser.ConfigParser()
config.read('config.ini')
config_main = config['main']
config_database = config['database']

mydb = mysql.connector.connect(host=config_database["host"],
                               port=int(config_database["port"]),
                               user=config_database["user"],
                               passwd=config_database["pwd"])
cur_mysql = mydb.cursor(dictionary=True)

conexao = ApSystems(config_main["domain"], config_main["useragent"], config_main["username"], config_main["password"])
if conexao.is_logged():
    retorno = conexao.get_power(20220224)
    for linha in retorno['power']:
        sql_insert = 'INSERT INTO solar.power (time, power) VALUES (%s, %s);'
        cur_mysql.execute(sql_insert, (retorno['power'][linha]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                                       retorno['power'][linha]['power']))
    mydb.commit()

    for panel in retorno['ecu_power']:
        for linha in retorno['ecu_power'][panel]:
            sql_insert = 'INSERT INTO solar.power_panel (time, power) VALUES (%s, %s);'
            cur_mysql.execute(sql_insert, (retorno['power'][linha]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                                           retorno['power'][linha]['power']))
