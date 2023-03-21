import io
import os
from typing import List

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import pdfkit
from PyPDF2 import PdfFileMerger, PdfFileReader


app = FastAPI()

@app.post("/combine_excel_and_text")
async def combine_excel_and_text(
    excel_files: List[UploadFile] = File(...),
    text: str = ""
):
    #let  Create an empty PDF file
    output_pdf = io.BytesIO()
    pdf_merger = PdfFileMerger()
    
    # let combine all the Excel files into one DataFrame
    dfs = []
    for excel_file in excel_files:
        df = pd.read_excel(excel_file.file)
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    
    #let write the combined DataFrame to a CSV file
    csv_bytes = combined_df.to_csv().encode('utf-8')
    csv_file = io.BytesIO(csv_bytes)
    
    # let convert the CSV file to a PDF file using pdfkit
    pdfkit_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }
    pdfkit.from_file(csv_file, output_pdf, options=pdfkit_options)
    
    # let add the text as a header to the PDF file
    pdf_merger.append(io.BytesIO(text.encode('utf-8')))
    pdf_merger.append(PdfFileReader(output_pdf))
    pdf_merger.write(output_pdf)
    
    # reset the output PDF file to the beginning
    output_pdf.seek(0)
    
    # return the PDF file with the text as the filename and header
    filename = f"{text}.pdf"
    return FileResponse(output_pdf, filename=filename, headers={"Content-Disposition": f"attachment; filename={filename}"})