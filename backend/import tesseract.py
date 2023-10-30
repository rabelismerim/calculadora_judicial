import io
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
 
def extract_text_from_pdf(pdf_path):
    # Convert PDF to image
    pages = convert_from_path(pdf_path, 500)
     
    # Extract text from each page using Tesseract OCR
    text_data = ''
    for page in pages:
        text = pytesseract.image_to_string(page)
        results = pytesseract.image_to_data(page, output_type=Output.DICT)
        text_data += text + '\n'
        print("Dicionário convertido\n")
        for i in range(0, len(results["text"])):
            # extract the bounding box coordinates of the text region from
            # the current result
            x = results["left"][i]
            y = results["top"][i]
            w = results["width"][i]
            h = results["height"][i]
            # extract the OCR text itself along with the confidence of the
            # text localization
            text = results["text"][i]
            conf = int(results["conf"][i])
            print("Confidence: {}".format(conf))
            print("Text: {}".format(text))
            
    # Return the text data
    return text_data
 
text = extract_text_from_pdf('report.pdf')
print("Texto convertido\n")
print(text)