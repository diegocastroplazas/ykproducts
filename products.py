import pandas as pd
import traceback
import base64
import requests
import uuid

class CargueProductos(object):
    def __init__(self, odoo, dbconn):
        self.odooConnector = odoo
        self.conn = dbconn

    def crearFotos(self):
        query = """SELECT * FROM cargue_product_template"""
        dataframe = pd.read_sql(query, self.conn)
        for index, row in dataframe.iterrows():
            try:
                odoo_id = self.nuevoProducto(row)
                print("Se ha creado el producto {0}". format(odoo_id))
                self.crearVariantes(row, odoo_id)
            except:
                traceback.print_exc() 
                continue

    def _getKeyName(self, valor):
        valor = valor.replace('(', '')
        valor = valor.replace(')', '')

        return valor.replace(" ", "_").lower()

    def nuevoProducto(self, row):
        image = self._get_as_base64(row['image_url'])
        image_send = image.decode('ascii')
        data_product = {
            'name': row['nombre'],
            'sale_ok': 1,
            'purchase_ok': 1,
            'type': 'product',
            'categ_id': 2,
            'image': image_send,
            'x_studio_rango_yk_1': str(row['range_yk']),
            'x_studio_artista_1': str(row['artista']).capitalize(),
            'x_studio_tema_1': str(row['tema'])
        }
        return self.odooConnector.createNew(model_name='product.template', data=data_product)

    def obtenerValoresAtributo(self):
        query = """SELECT * FROM odoo_product_attribute_value"""
        dataframe = pd.read_sql(query, self.conn)
        return dataframe

    def _obtenerIdsAtributo(self, keyword="", attribute_values=list()):
        attribute_ids = list()
        for value in attribute_values:
            filtered = self.valores_attributo.query('display_name=="{0}: {1}"'.format(keyword,value))
            try:
                id_ = filtered['odoo_id'].values[0]
                attribute_ids.append(int(id_))
            except IndexError:
                continue
        return attribute_ids

    def _get_as_base64(self, url):
        return base64.b64encode(requests.get(url).content)

    def crearVariantes(self, row=dict(), template_id=1):
        configuraciones = str(row['configuraciones']).split(',')
        
        '''
        self.valores_attributo = self.obtenerValoresAtributo()
        configuraciones_ids = self._obtenerIdsAtributo(keyword="Configuración", attribute_values=configuraciones)
        '''
        configuraciones_ids = list()
        for id_conf in configuraciones:
            configuraciones_ids.append(int(id_conf))

        product_line = self.odooConnector.createNew(
            model_name="product.template.attribute.line",
            data={
                'product_tmpl_id': template_id,
                'attribute_id': 4,
                'value_ids': [[6,0,configuraciones_ids]]
            }
        )
        
        updated_product = self.odooConnector.update(
            model_name="product.template",
            odoo_id=template_id,
            data={'active': True}
        )
        print(updated_product)

    def modificarVariantes(self):

        '''
        data={
                        'x_studio_formato': self._getKeyName(row['category']),
                        'x_studio_montaje': self._getKeyName(row['framing']),
                        'x_studio_acabado': self._getKeyName(row['finishing']),
                        'default_code': row['ean'],
                        'barcode': row['ean']
                    },
        '''
        query = """SELECT * FROM actualizacion_variantes"""
        dataframe = pd.read_sql(query, self.conn)
        for index, row in dataframe.iterrows():
            try:
                self.agregarPrecio(row)
                print("Precio agregado para ")
                self.odooConnector.update(
                    model_name='product.product', 
                    data={
                        'default_code': row['ean'],
                        'barcode': row['ean']
                    },
                    odoo_id=int(row['odoo_id'])
                )
                print("Variante actualizada")
            except:
                continue

    def agregarPrecio(self, data):
        id_producto = self.odooConnector.search(
            model_name='product.template.attribute.value',
            criteria=[[['product_tmpl_id', '=', int(data['product_tmpl_id'])], ['product_attribute_value_id', '=', int(data['value_id'])]]],
            fields={'fields': ['id']}
        )
        response = self.odooConnector.update(
            model_name='product.template.attribute.value',
            data={'price_extra': float(data['colombia']/1.19)},
            odoo_id=int(id_producto['id'])
        )
        print(response)

    def deshabilitarVariantes(self):

        query = """select * from odoo_product_product opp where opp.barcode in (select distinct ean from first_order)"""
        dataframe = pd.read_sql(query, self.conn)
        for index, row in dataframe.iterrows():
            nuevo_ean = str(row['default_code']) + 'nousar' + uuid.uuid4().hex.upper()[0:6]
            try:
                self.odooConnector.update(
                    model_name='product.product', 
                    data={
                        'default_code': nuevo_ean,
                        'barcode': nuevo_ean
                    },
                    odoo_id=int(row['odoo_id'])
                )
                print("Variante {0} actualizada".format(row['odoo_id']))
            except:
                continue


    def agregarConfiguracionesFaltantes(self):
        '''
        
            try:
                odoo_id = row['odoo_id']
                # self.crearVariantes(row, odoo_id)

                updated_product = self.odooConnector.update(
                    model_name="product.template",
                    odoo_id=odoo_id,
                    data={'active': True}
                )
                print("Actualizado producto {0}".format(updated_product))
            except:
                traceback.print_exc() 
                continue
        '''

        query = """SELECT * FROM configuraciones_faltantes"""
        dataframe = pd.read_sql(query, self.conn)

        for index, row in dataframe.iterrows():
            template_id = int(row['product_templ_id'])
            odoo_id = int(row['line_id'])
            configuraciones = str(row['configuraciones']).split(',')

            conf_ids = list()
            for conf in configuraciones:
                conf_ids.append(int(conf))

            self.odooConnector.update(
                model_name="product.template.attribute.line",
                odoo_id=odoo_id,
                data = {'value_ids': [[6,0,conf_ids]]}
            )

            updated_product = self.odooConnector.update(
                model_name="product.template",
                odoo_id=template_id,
                data={'active': True}
            )
            print(updated_product)
