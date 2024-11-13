from PyPDF2 import PdfReader 


def read_pdf(file_paths):
    """
        Inputs:- 
        file_paths:- List of filepaths that point to knowledge base

        Returns:- 
        readers:- PDF readers that contain the text of PDF files
    """

    readers = []
    for file_path in file_paths: 
        print(file_path)
        reader = PdfReader(file_path)
        readers.append(reader)

    return readers

def parse_pages(reader):
    """
        Inputs:- 
            reader- PDF reader object 
        
        Output:- 
            pages - List of all pages, currently only supports text
    """
    return [page.extract_text() for page in reader.pages]




def embed_pdfs(pages):
    """
        Inputs:- 
            pages:- list of pages from PDF

        Returns:- 
            

    """