import uuid
from lxml import etree

def generate_cisco_lab():
    lab_id = str(uuid.uuid4())
    lab = etree.Element('lab', name='Cisco_Simple_VXLAN', id=lab_id, version='1', scripttimeout='300', lock='0')
    topology = etree.SubElement(lab, 'topology')
    nodes = etree.SubElement(topology, 'nodes')
    
    node_configs = [
        {"id": "1", "name": "VTEP-1", "left": "300", "top": "200"},
        {"id": "2", "name": "VTEP-2", "left": "600", "top": "200"},
        {"id": "3", "name": "Client-1", "left": "300", "top": "400"},
        {"id": "4", "name": "Client-2", "left": "600", "top": "400"}
    ]
    
    for config in node_configs:
        node_type = "qemu" if "VTEP" in config["name"] else "vpcs"
        template = "csr1000v" if "VTEP" in config["name"] else "vpcs"
        ram = "3072" if "VTEP" in config["name"] else "128"
        etree.SubElement(nodes, 'node', id=config["id"], name=config["name"], type=node_type, template=template, ram=ram, left=config["left"], top=config["top"], icon="Router.png" if "VTEP" in config["name"] else "Desktop.png", ethernet="4")
        
    networks = etree.SubElement(topology, 'networks')
    links = [{"id": "1", "type": "bridge"}, {"id": "2", "type": "bridge"}, {"id": "3", "type": "bridge"}]
    for link in links:
        etree.SubElement(networks, 'network', id=link["id"], type=link["type"], name=f"Net_{link['id']}")
    
    xml_data = etree.tostring(lab, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    with open('Cisco_Simple_VXLAN.unl', 'wb') as f:
        f.write(xml_data)

if __name__ == "__main__":
    generate_cisco_lab()
