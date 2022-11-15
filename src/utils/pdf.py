import csv
import random
import string
from io import BytesIO, StringIO

import pandas as pd
import pdfkit


def get_rand_name():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for i in range(10))


def get_html_from_csv(csv):
    return pd.read_csv(csv).to_html()


def get_table_from_html(table_html, table_title=None, styles=""):
    if table_title:
        return f"""
            <div style="{styles}">
                <h1 style='text-align: left;margin-bottom: 10px;'>{table_title}</h1>
                {table_html}
            </div>
        """
    else:
        return f"""
            <div style="{styles}">
                {table_html}
            </div>
        """


def get_final_html(tables, template: str, prefix_html="", extra_html=""):
    tables_html = " ".join(tables)
    tables_html += extra_html

    return template.replace("{body}", tables_html).replace("{prefix_html}", prefix_html)


def get_pdf_from_html(html):
    return pdfkit.PDFKit(html, "string").to_pdf()


def get_csv_from_rows(rows, headers=None, row_has_heders=True):
    csv_file = StringIO()
    writer = csv.writer(csv_file, dialect="excel", delimiter=",")
    if not row_has_heders:
        writer.writerow(headers)
    writer.writerows(rows)
    csv_file.seek(0)

    return csv_file


def get_pdf_to_bytes(pdf):
    io = BytesIO()
    io.write(pdf)
    io.seek(0)

    return io


def get_rows_to_table(table_rows, table_title, table_headers=None, styles=""):
    csv = get_csv_from_rows(
        table_rows, table_headers, row_has_heders=False if table_headers else True
    )
    html = get_html_from_csv(csv)
    table = get_table_from_html(html, table_title, styles=styles)

    return table
