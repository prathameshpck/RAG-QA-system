from utils import read_pdf, parse_pages


file_paths = ['/home/pinto/Desktop/MLE/s3-simul/Szeliski_CVAABook_2ndEd.pdf']


readers = read_pdf(file_paths)
pages = [parse_pages(reader) for reader in readers]
print(len(pages[0]))