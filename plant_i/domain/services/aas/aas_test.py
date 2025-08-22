
import json
from basyx.aas import model

from basyx.aas.model import datatypes

import basyx.aas.adapter.json
import basyx.aas.adapter.xml

from basyx.aas.adapter.aasx import AASXWriter, DictSupplementaryFileContainer

class AASTest():
    def __init__(self):
        return


    def test(self):

        admin = model.AdministrativeInformation()
        admin.version = '1'
        admin.revision = '0'


        submodel_display_name = model.MultiLanguageNameType({'ko-KR': 'Simple Submodel'})

        submodel = model.Submodel(
            id_='https://acplt.org/Simple_Submodel',
            submodel_element={
                model.Property(
                    id_short='ExampleProperty',
                    value_type=datatypes.String,
                    value='exampleValue',
                    semantic_id=model.ExternalReference((model.Key( type_=model.KeyTypes.GLOBAL_REFERENCE, value='http://acplt.org/Properties/SimpleProperty' ),)),            
                )},
            administration = admin,
            display_name = submodel_display_name

        )


        asset = model.AssetInformation(global_asset_id="test", asset_type="테스트타입")

        aashell = model.AssetAdministrationShell(
            id_='https://acplt.org/Simple_AAS', category = 'test cateogty',
            asset_information=asset,
            submodel={model.ModelReference.from_referable(submodel)},
            administration = admin,
            display_name=model.MultiLanguageNameType({'en': 'Simple AAS'})
        )
        
        
        aashell.update()


        aashell_json_string = json.dumps(aashell, cls=basyx.aas.adapter.json.AASToJsonEncoder)
        property_json_string = json.dumps(submodel.submodel_element.get_object_by_attribute("id_short", 'ExampleProperty'), cls=basyx.aas.adapter.json.AASToJsonEncoder)


        json_string = json.dumps({'the_submodel': submodel, 'the_aas': aashell }, cls=basyx.aas.adapter.json.AASToJsonEncoder)

        submodel_and_aas = json.loads(json_string, cls=basyx.aas.adapter.json.AASFromJsonDecoder)

        obj_store: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
        obj_store.add(submodel)
        obj_store.add(aashell)


        submodel.update()
        aashell.update()

        file_store = DictSupplementaryFileContainer()

        out_path = 'test.aasx'
        with AASXWriter(out_path) as w:
            w.write_aas(aas_ids=[aashell.id], object_store=obj_store, file_store=file_store, write_json=True)





        with open('data_test.json', 'a', encoding='utf-8') as json_io:
            basyx.aas.adapter.json.write_aas_json_file(json_io, obj_store)
            #basyx.aas.adapter.json.write_aas_json_file('data_test.json', obj_store)

            basyx.aas.adapter.xml.write_aas_xml_file('data_test.xml', obj_store)


'''
with open('data_test.json', 'r', encoding='utf-8') as json_io:
    json_file_data = basyx.aas.adapter.json.read_aas_json_file(json_io)

with open('data_test.xml', 'r', encoding='utf-8') as xml_io:
    xml_file_data = basyx.aas.adapter.xml.read_aas_xml_file(xml_io)
'''


##################################################################
# Step 5: Reading the Serialized AAS Objects From JSON/XML Files #
##################################################################

# step 5.1: reading contents of the JSON file as an ObjectStore


# By passing the `failsafe=False` argument to `read_aas_json_file()`, we can switch to the `StrictAASFromJsonDecoder`
# (see step 3) for a stricter error reporting.

# step 5.2: reading contents of the XML file as an ObjectStore


# Again, we can use `failsafe=False` for switching on stricter error reporting in the parser.

# step 5.3: Retrieving the objects from the ObjectStore
# For more information on the availiable techniques, see `tutorial_storage.py`.

#submodel_from_xml = xml_file_data.get_identifiable('https://acplt.org/Simple_Submodel')
#assert isinstance(submodel_from_xml, model.Submodel)





aas_test= AASTest()
aas_test.test()
