import xmlrpc.client
from exceptions import LoginError, OdooException
import datetime
import traceback


class Odoo(object):
    def __init__(self, dbName='', serverUrl='', username='', password=''):
        self.dbName = dbName
        self.serverUrl = serverUrl
        self.username = username
        self.password = password
        self.authenticate()
        
    def authenticate(self):
        """
        Populates the current instance with models attribute. This attribute 
        will be used for performing tasks on the odoo models.
        """
        self.uid = self._getUid()
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.serverUrl))

    def _getCommon(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(
            self.serverUrl)
        )
        return common

    def _getUid(self):
        common = self._getCommon()
        uid = common.authenticate(self.dbName, self.username, self.password, {})
        if uid is False:
            raise LoginError(
                "It is not possible to log in to Odoo, check username and password"
            )
        return uid

    def obtainDataFromModel(self, model_name="", criteria=list(), attributes=list()):
        ids_list = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            model_name, 'search',
            criteria,
        )

        results = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            model_name, 'read',
            [ids_list], {
                'fields': attributes
            }
        )
        return results

    def obtainFields(self, model_name=""):
        fields_list = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            model_name, 'fields_get',
            [], {'attributes': ['string', 'help', 'type']}
        )
        print(fields_list)
        return fields_list

    def recordCount(self, model_name="", criteria=list()):
        record_count = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            model_name, 'search_count',
            criteria
        )
        print("Total registros: {0}".format(record_count))
        return record_count

    def createNew(self, model_name="", data=dict()):
        try:
            odoo_id = self.models.execute_kw(
                self.dbName, self.uid, self.password,
                model_name, 'create',
                [data]
            )
        except xmlrpc.client.Fault:
            print("No fue posible cargar el registro: {0}".format(data))
            traceback.print_exc()
            raise OdooException
        return odoo_id

    def update(self, model_name="", data=dict(), odoo_id=int()):
        try:
            odoo_id = self.models.execute_kw(
                self.dbName, self.uid, self.password,
                model_name, 'write',
                [[odoo_id], data]
            )
            print("Data actualizada: {0}".format(data))
        except xmlrpc.client.Fault:
            print("No fue posible actualizar el registro {0}".format(odoo_id))
            traceback.print_exc()
            raise OdooException
        return odoo_id

    def addProductToPriceList(self, id_lista, id_producto, precio):
        id_lista = int(id_lista)
        id_producto = int(id_producto)
        precio = float(precio)
        
        MODEL_NAME = "product.pricelist"
        
        data_producto = {
            'product_id': id_producto, 
            'fixed_price': precio, 
            'min_quantity': 1,
            'applied_on': '0_product_variant'
        }
        response = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            MODEL_NAME, 'write', 
            [[id_lista], {'item_ids': [(0, '_', data_producto)]}], {}
        )
        print(response)

    def search(self, model_name="", criteria=list(), fields=dict()):
        response = self.models.execute_kw(
            self.dbName, self.uid, self.password,
            model_name, 'search_read',
            criteria,
            fields
        )
        return response[0]