from docx2pdf import convert
from docx import Document
from PyPDF2 import PdfReader, PdfWriter
import fitz
import logging
from PIL import Image
import os
import warnings

warnings.simplefilter('ignore')


class Creator:
    
    def docx_to_pdf(docx_path,pdf_path):
        try:
            pdf_path = os.path.abspath(pdf_path)
            pdf_path = os.path.join(pdf_path,'document.pdf')
            docx_path = os.path.abspath(docx_path)            
            convert(docx_path,pdf_path)
            logging.info('¡El archivo fue generado exitosamente!')
        except Exception as e:
            logging.error(f'Fallo la conversión de Word a PDF: {e}')
    
    def dividir_pdf(file_pdf,path_pdf,num_page,columns_name = None):
        try:
            path_pdf = os.path.abspath(path_pdf)
            reader = PdfReader(file_pdf)
            
            if not isinstance(num_page,int) or num_page < 1:
                raise ValueError('El numero de paginas no puede ser <= 0')
            contador = 0
            for page in range(0,len(reader.pages),num_page):
                writer = PdfWriter()
                for i in range(num_page):
                    if page + i < len(reader.pages):
                        pagina = reader.pages[page + i]
                        writer.add_page(pagina)
                if columns_name is not None and not columns_name.empty:
                    with open(f'{os.path.join(path_pdf,str(columns_name[contador]))}.pdf','wb') as output_pdf:
                        writer.write(output_pdf)
                else:
                    with open(f'{os.path.join(path_pdf,"document_" + str(contador))}.pdf','wb') as output_pdf:
                        writer.write(output_pdf)
                contador += 1
            logging.info('¡El archivo se dividio de manera exitosa')
        except ValueError as ve:
            logging.error(f'Error de validación: {ve}')
        except Exception as e:
            logging.error(f'Fallo la división del archivo PDF: {e}')
    
    def pdf_to_images(file_pdf,pdf_path):
        try:
            pdf_path = os.path.abspath(pdf_path)
            resolution = 300
            images = []
            pdf_document = fitz.open(file_pdf)
            contador = 1
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                zoom = 2
                mat = fitz.Matrix(zoom,zoom)
                pixmap = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                images.append(img)
                contador += 1
            pdf_document.close()
            logging.info('¡La conversión de PDF a Imagenes se genero exitosamente!')
            return images
        except Exception as e:
            logging.error(f"Fallo la conversión de PDF a Imagen: {e}")
            
    def combine_images(input_images, output_path, numpages, columns_name = None):
        
        images = input_images
        sta = 0
        end = numpages
        num_iter = len(images) // numpages
        output_path = os.path.abspath(output_path)
        resolution = 300
        
        try:
            contador = 0
            for i in range(num_iter):
                img_list = images[sta:end]
                
                total_width = max(img.width for img in img_list)
                max_height = sum(img.height for img in img_list)
                
                combined_image = Image.new("RGB", (total_width, max_height))
                
                y_offset = 0
                
                for img in img_list:
                    combined_image.paste(img, (0,y_offset))
                    y_offset += img.height
                if columns_name is not None and not columns_name.empty:
                    combined_image.save(os.path.join(output_path,f'{columns_name[contador]}.png'),dpi=(resolution,resolution))
                else:
                    combined_image.save(os.path.join(output_path,f'{contador}_Image.png'),dpi=(resolution,resolution))
                    
                sta = end
                end += numpages
                contador +=1
            logging.info('¡La combinación de imagenes fue exitosa!')
        
        except IndexError as ie:
            logging.error(f'Error de indice: {ie}')
        except Exception as e:
            logging.error(f'La combinación de imagenes fallo: {e}')

