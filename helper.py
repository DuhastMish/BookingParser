from bs4 import BeautifulSoup  # noqa: D100
import logging


def set_lang_and_table_style(path_to_file: str, charset: str, lang: str, table_border: str,
                             cellspacing: str, cellpadding: str, td_style: str) -> None:
    """Edit attributes in ratio_data.html file: set language, borders and other."""
    logging.info('Seting styles for html table.')
    with open(path_to_file) as f:
        txt = f.read()
        soup = BeautifulSoup(txt, "html.parser")

    meta_tag = soup.meta
    meta_tag['charset'] = charset

    html_tag = soup.html
    html_tag['lang'] = lang

    table_tag = soup.table
    table_tag['border'] = table_border
    table_tag['cellspacing'] = cellspacing
    table_tag['cellpadding'] = cellpadding

    tds = soup.find("table").find_all("td")
    for td in tds:
        td['style'] = td_style

    with open(path_to_file, "w") as outf:
        outf.write(str(soup))
