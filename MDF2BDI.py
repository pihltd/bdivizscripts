# Reads an MDF model and writes a version compatible with BDIViz
#The BDI model file appears to be mostly properties: https://vida-nyu.github.io/bdi-viz-manual/docs/manual/upload-your-data/

import bento_mdf
import json
import argparse
from crdclib import crdclib


def getPVs(cdeid, cdever):
    cdejson = crdclib.getCDERecord(cdeid, cdever)
    if cdejson['DataElement']['ValueDomain']['type'] == 'Enumerated':
        pvlist = []
        if 'PermissibleValues' in cdejson['DataElement']['ValueDomain']:
           for pventries in cdejson['DataElement']['ValueDomain']['PermissibleValues']:
                pvlist.append(pventries['value'])
        return pvlist
    else:
        return None

def main(args):
    configs = crdclib.readYAML(args.configfile)
    
    mdf = bento_mdf.mdf.MDF(*configs['mdffiles'])
    
    
    bdijson = {}
    
    props = mdf.model.props
    nodes = mdf.model.nodes
    
    for node, prop in props:
        propinfo = props[(node,prop)].get_attr_dict()
        nodetags = nodes[node].tags
        temp = {}
        temp['column_name'] = prop
        temp['category'] = (nodetags['Category'].get_attr_dict())['value']
        temp['node'] = node
        temp['type'] = propinfo['value_domain']
        temp['description'] = propinfo['desc']
        
        #Get the CDE ID and version
        if props[(node, prop)].concept is not None:
            propterms = props[(node, prop)].concept.terms
            for termobj in propterms.values():
                termdict = termobj.get_attr_dict()
                cdeid = termdict['origin_id']
                cdever = termdict['origin_version']
                pvlist = getPVs(cdeid, cdever)
                if pvlist is not None:
                    temp['type'] = 'enum'
                    temp['enum'] = pvlist
                
        
        bdijson[prop] = temp
        
        
        jsonobj = json.dumps(bdijson, indent=4)
        with open(configs['jsonfile'], 'w') as f:
            f.write(jsonobj)
            
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    main(args)