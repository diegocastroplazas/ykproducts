"""
Este programa configura los campos diferentes que deben crearse con Odoo Studio
para el nuevo esquema de productos.
"""

import pandas as pd
import psycopg2
import yaml

from odoolib import Odoo
from products import CargueProductos

def leerConfiguracion():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    ambiente = cfg['config']['env']
    return cfg['config'][ambiente]

def obtenerAtributos(nombre_campo, conn):
    query = """SELECT DISTINCT {} FROM price_audit""".format(nombre_campo)
    dataframe = pd.read_sql(query, conn)
    campos = list()
    for index, row in dataframe.iterrows():
        valor = str(row[nombre_campo])
        valor = valor.replace('(', '')
        valor = valor.replace(')', '')
        campos.append((valor.replace(" ", "_").lower(), valor))

    print("-"*100)
    print(campos)


def main():
    config = leerConfiguracion()
    db_conn = psycopg2.connect(
        user=config['db']['user'],
        password=config['db']['secret'],
        database=config['db']['dbname'],
        host=config['db']['host'],
        port="5432"
    )
    # obtenerAtributos('tema', db_conn)
    
    odoo = Odoo(
       dbName=config['odoo']['dbname'],
       serverUrl=config['odoo']['url'],
       username=config['odoo']['user'],
       password=config['odoo']['secret'] 
    )
    p = CargueProductos(odoo, db_conn)
    #p.crearAtributos()
    #p.crearFotos()
    # p.modificarVariantes()
    # p.deshabilitarVariantes()
    p.agregarConfiguracionesFaltantes()

if __name__ == "__main__":

    main()
