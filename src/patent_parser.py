import pandas as pd
import os
from lxml import etree
from collections import OrderedDict, defaultdict
import csv
import pudb 

def read_patent(file):
    count = 0
    storage_dir = "data"
    storage_path = os.path.join(os.getcwd(), storage_dir)	
    path = os.path.join(storage_path, file.name.values[0])
    #declaring XMLPullParser with end event
    if file.name.values[0].startswith("pgb"):
        pat_xml = etree.XMLPullParser(tag='PATDOC', events=['end'], recover=True)
    elif file.name.values[0].startswith("ipgb"):
        pat_xml = etree.XMLPullParser(tag='us-patent-grant', events=['end'], recover=True)
    with open(path, 'r') as lines:
        for line in lines:
            if line.startswith("<?xml"):
                if(patent_ends(pat_xml, file.name.values[0])):
                    pat_xml.close()
                    if file.name.values[0].startswith("pgb"):
                        pat_xml = etree.XMLPullParser(tag='PATDOC', events=['end'], recover=True)
                    elif file.name.values[0].startswith("ipgb"):
                        pat_xml = etree.XMLPullParser(tag='us-patent-grant', events=['end'], recover=True)
            #Removing unwanted nodes
            elif line.startswith("<!DOCTYPE") or line.startswith("]>") or line.startswith('<!ENTITY'):
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
        #process_patent_version1(element)
        pass
    elif (file.startswith('pgb')):
        process_patent_version2(element)

def process_patent_version1(element):
    patents = defaultdict(str)
    patent_number = element.find('us-bibliographic-data-grant') \
                    .find('publication-reference')\
                    .find('document-id')\
                    .find('doc-number').text

    # Important Info
    patents['title'] = result_or_default(element.find('us-bibliographic-data-grant'), 'invention-title')

    inventors = element.find('us-bibliographic-data-grant').find('us-parties').find('inventors')
    if inventors is not None:
        patents['inventor'] = []
        for inventor in inventors.findall('inventor'):
            addressbook = inventor.find('addressbook')
            if addressbook is not None:
                patents['inventor'].append([result_or_default(addressbook, 'last-name'), result_or_default(addressbook, 'first-name')])
    
    applicants = element.find('us-bibliographic-data-grant').find('us-parties').find('us-applicants')
    if applicants is not None:
        patents['applicant'] = []
        for applicant in applicants.findall('us-applicant'):
            addressbook = applicant.find('addressbook')
            if addressbook is not None:
                patents['applicant'].append([result_or_default(addressbook, 'last-name'), result_or_default(addressbook, 'first-name')])

    assignee = element.find('us-bibliographic-data-grant').find('assignees/assignee/addressbook')
    if assignee is not None:
        patents['owner'] = result_or_default(assignee, 'orgname')

    
    
    # citations
    citation_references = element.find('us-bibliographic-data-grant').find('references-cited')
    prefix = ''
    if citation_references is None:
        citation_references = element.find('us-bibliographic-data-grant').find('us-references-cited')
        prefix = 'us-'

    citations = []
    if citation_references is not None:
        for citation in citation_references.findall(prefix + 'citation'):
            pcitation = citation.find('patcit')
            if pcitation is not None:
                docid = pcitation.find('document-id')
                patent_num = result_or_default(docid, 'doc-number')
                citations.append(patent_num)
        patents['citations'] = citations    
    
    patents['number'] = patent_number

    
    write_citations(patents)
    write_patent_header(patents)


def process_patent_version2(element):
    patents = defaultdict(str)
    patent_number = result_or_default(element.find('SDOBI').find('B100'), 'B110/DNUM/PDAT')
    
    #important info
    patents['title'] = result_or_default(element.find('SDOBI').find('B500'), 'B540/STEXT/PDAT')

    inventors = element.find('SDOBI').find('B700/B720/B721')
    if inventors is not None:
        patents['inventor'] = []
        for inventor in inventors.findall('PARTY-US'):
            details = inventor.find('NAM')
            if details is not None:
                patents['inventor'].append([result_or_default(details, 'FNAM/PDAT'), result_or_default(details, 'SNM/STEXT/PDAT')])
    
    applicants = element.find('SDOBI').find('B700/B730/B731')
    if applicants is not None:
        patents['applicant'] = []
        for applicant in applicants.findall('PARTY-US'):
            details = applicant.find('NAM')
            if details is not None:
                patents['applicant'].append([result_or_default(details, 'FNAM/PDAT'), result_or_default(details, 'SNM/STEXT/PDAT')])
    
    owner = element.find('SDOBI').find('B700/B730/B731/PARTY-US')
    if owner is not None:
        patents['owner'] = result_or_default(owner, 'NAM/ONM/STEXT/PDAT')
    
    citation_references = element.find('SDOBI').find('B500/B560')
    if citation_references is not None:
        citations = []
        for citation in citation_references.findall('B561'):
            patent_num = result_or_default(citation, 'PCIT/DOC/DNUM/PDAT')
            citations.append(patent_num)
        patents['citations'] = citations
    
    patents['number'] = patent_number
    
    
    write_citations(patents)
    write_patent_header(patents)    

def process_patent_version3():
    pass

def clear(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]

def result_or_default(parent,tag,default=''):
    result = parent.find(tag)
    return (result.text or default) if result is not None else default

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

def write_citations(patents):
    line = []
    patent_number = patents['number']
    print(patent_number)
    with open('citations.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        for citation in patents['citations']:
            writer.writerow([patent_number, citation])
    writeFile.close()

def write_patent_header(patents):
    line = []
    patent_number = patents['number']
    print(patent_number)
    with open('patents.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow([patent_number, patents['title'], patents['inventor'], patents['applicant'], patents['owner']])
    writeFile.close()