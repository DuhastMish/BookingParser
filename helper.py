import bs4

def set_lang_and_table_style(path_to_file: str, lang: str, table_border: str, 
                             cellspacing: str, cellpadding: str, td_style: str) -> None:
    """Method to edit attributes in ratio_data.html file: set language, borders and other"""
    with open(path_to_file) as f:
        txt = f.read()
        soup = bs4.BeautifulSoup(txt, "html.parser")
    
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
        
    