import pandas as pd
import traceback
import base64
import requests

class CargueProductos(object):
    def __init__(self, odoo, dbconn):
        self.odooConnector = odoo
        self.conn = dbconn
        
    def crearFotos(self):
        query = """SELECT * FROM nuevas_fotos_odoo"""
        dataframe = pd.read_sql(query, self.conn)
        for index, row in dataframe.iterrows():
            odoo_id = self.nuevoProducto(row)
            print("Se ha creado el producto {0}". format(odoo_id))
            self.crearVariantes(row, odoo_id)

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
            'x_rango_yk': str(row['range_yk']),
            'x_fotografo': str(row['artista']).capitalize()
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
        self.valores_attributo = self.obtenerValoresAtributo()

        configuraciones_ids = self._obtenerIdsAtributo(keyword="Configuración", attribute_values=configuraciones)
        
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

    def asignarPrecio(self):
        pass

    def asignarBarcodeVariantes(self):
        data_actualizacion = self.obtenerDataActualizacionVariantes()
        for index, row in data_actualizacion.iterrows():
            try:
                updated_product_product = self.odooConnector.update(
                    model_name="product.product",
                    odoo_id=int(row['odoo_id']),
                    data={
                        'barcode': row['ean'],
                        'default_code': row['ean'],
                        'x_studio_rango_yk': row['range_yk'],
                        'x_studio_tema': row['theme']
                    }
                )
                print("Variante {0} actualizada correctamente".format(
                    row['odoo_id']
                ))
            except:
                continue


    def desactivarReferenciasSinEAN(self):
        productos = self.obtenerVariantesSinEAN()
        for index, row in productos.iterrows():
            try:
                disabled = self.odooConnector.update(
                    model_name='product.product',
                    data={'active': False},
                    odoo_id=int(row['odoo_id'])
                )
                print("Variante {0} deshabilitada".format(row['odoo_id']))
            except:
                print("Error al actualizar variante {0} Traza del error: {1} ".format(
                    row['odoo_id'], traceback.print_exc()
                ))
                continue

