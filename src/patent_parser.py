import pandas as pd
import os
from lxml import etree
import pudb 

def read_patent(file):
    count = 0
    storage_dir = "data"
    storage_path = os.path.join(os.getcwd(), storage_dir)	
    path = os.path.join(storage_path, file.name.values[0])
    #declaring XMLPullParser with end event
    pat_xml = etree.XMLPullParser(tag='us-patent-grant', events=['end'], recover=True)
    with open(path, 'r') as lines:
        for line in lines:
            if line.startswith("<?xml"):
                if(patent_ends(pat_xml, file.name.values[0])):
                    pat_xml.close()
                    pat_xml = etree.XMLPullParser(tag='us-patent-grant', events=['end'], recover=True)
            #Removing unwanted nodes
            elif line.startswith("<!DOCTYPE") or line.startswith("]>"):
                pass
            else:
                #pudb.set_trace()
                #Using feed Parser for line by line parsing
                pat_xml.feed(line)

def patent_ends(pat_xml, file):
    for action, element in pat_xml.read_events():
        init_patent_processing(element, file)
        clear(element)
        return True
    return False   

def init_patent_processing(element, file):
    if(file.startswith("ipgb")):
        process_patent_version1(element)

def process_patent_version1(element):
    patent = element.find('us-bibliographic-data-grant') \
                    .find('publication-reference')\
                    .find('document-id')\
                    .find('doc-number').text
    print(patent)

def clear(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]

def split_patents(path):
	try:
		cnt = 0
		fw = None
		fp = open(path)
		for line in fp:
			if line.startswith("<?xml"):
				cnt += 1
				if fw is not None:
					fw.close()
				w_file = str(cnt) +'.xml'
				fw = open(w_file, 'a')
				fw.write(line)
			else:
				fw.write(line)
		fw.close()
	finally:
		fp.close()	
