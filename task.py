
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
from PDFToTextConverter import convertPDFToText

import re
import sys,glob
import nltk

#file location goes here
fileLocation = ""
password = ""
pageData = ""

filepointer = open(fileLocation, "rb")
parser = PDFParser(filepointer)    
# Store parsed data in PDFDocument object
document = PDFDocument(parser, password)    
# Create PDFResourceManager object 
rsrcmgr = PDFResourceManager()    
# Set analysis parameters
laparams = LAParams()
# Translates interpreted information into desired format
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# Create interpreter object to process page content from PDFDocument
interpreter = PDFPageInterpreter(rsrcmgr, device)
    
for page in PDFPage.create_pages(document):
    	interpreter.process_page(page)
    	layout = device.get_result()
    	for layoutObj in layout:
    		if isinstance(layoutObj, LTTextBox) or isinstance(layoutObj, LTTextLine):
    			pageData += layoutObj.get_text()

pdfContent = pageData

#extract names 
def extract_names(inputString):
        # Reads names from namesdataset.txt
        namesList = open("C:/Users/Ramkumar/Desktop/college/VI_SEM/bitgram task/namesDataset.txt", "r").read().lower()
        namesList = set(namesList.split())
        
        otherNameHits = []
        nameHits = []
        name = []
        pos = 0
        try:
            for sent in nltk.sent_tokenize(inputString):
                for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                    if hasattr(chunk,'label'):
                        if( chunk.label() == 'PERSON'): 
                               m = (''.join(c[0] for c in chunk))
                               if m.lower() in namesList and pos == 0:
                                       name = m
                                       pos = 1
                                       
                               else:
                                       otherNameHits.append(m)
        except Exception as e:
            print (e)
        
        return name


def extract_email_addresses(pageData):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(pageData)



def extract_contacts(pageData):
    
    r = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
    match = r.findall(pdfContent)

    # Used to match mobile numbers like (91) 1234567890 or +91 0987654321 or 91 98765 43210
    match = [re.sub(r'[,.]', '', el) for el in match if len(re.sub(r'[()\-.,\s+]', '', el))>6]
    match = [re.sub(r'\D$', '', el).strip() for el in match]
    match = [el for el in match if len(re.sub(r'\D','',el)) <= 15]
    try:
        for el in list(match):
            if len(el.split('-')) > 3: continue # Remove years
            for x in el.split("-"):
                try:
                    # Error catching for non-number characters
                    if x.strip()[-4:].isdigit():
                        if int(x.strip()[-4:]) in range(1900, 2100):
                            match.remove(el)
                except:
                    pass
    except:
        pass
    number = match
    return match

if __name__ == '__main__':
    #args = sys.argv[1:]
    #if len(args == 1):
    inputString = convertPDFToText(fileLocation)
    numbers = extract_contacts(pageData)
    emails = extract_email_addresses(pageData)
    names = extract_names(pageData)
    #else:
     #       print("task.py <folder/file>")

print("Name: ",names)
print("E-mail: ",emails)
print("Phone: ",numbers)
