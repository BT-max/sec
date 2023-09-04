from bs4 import BeautifulSoup


def FLWS(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all("p")
    human_capital_section = ""
    for element in elements:
        if not (element.find("b") and "Human Capital" in element.find("b").text):
            continue
        for sibling in element.find_next_siblings():
            if sibling.find("b") and \
                    "Table of Contents".lower() not in sibling.get_text(strip=True, separator=" ").lower():
                break
            human_capital_section += sibling.get_text(strip=True, separator=" ") + " "
    return human_capital_section


def TXG(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    human_capital_div = soup.find('div', string=lambda text: text and 'Human Capital' in text)
    if not human_capital_div:
        return ""
    next_divs = human_capital_div.find_next_siblings('div')
    human_capital_content = []
    for div in next_divs:
        span = div.find("span")
        if 'style' in span.attrs and "font-style:italic" not in span.attrs['style'] and \
                "font-weight:700" in span.attrs['style']:
            break
        human_capital_content.append(div.text)
    human_capital_text = '\n'.join(human_capital_content)
    return human_capital_text


def ONEM(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    human_capital_div = soup.find('div', string=lambda text: text and 'Human Capital' in text)
    if not human_capital_div:
        return ""
    next_divs = human_capital_div.find_next_siblings('div')
    human_capital_content = []
    for div in next_divs:
        span = div.find("span")
        if not div.get_text(strip=True, separator=" "):
            continue
        if 'style' in span.attrs and "font-style:italic" not in span.attrs['style'] and \
                "font-weight:700" in span.attrs['style'] \
                and "text-indent:36pt" not in div.attrs['style']:
            break
        human_capital_content.append(div.get_text(strip=True, separator=" "))
    human_capital_text = '\n'.join(human_capital_content)
    return human_capital_text


def SRCE(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    human_capital_div = soup.find('div', string=lambda text: text and 'Human Capital'.lower() in text.lower())
    if not human_capital_div:
        return ""
    next_divs = human_capital_div.find_next_siblings('div')
    human_capital_content = []
    for div in next_divs:
        span = div.find("span")
        if not div.get_text(strip=True, separator=" "):
            continue
        if span.find("a"):
            continue
        if 'style' in span.attrs and "text-decoration:underline" in span.attrs['style']:
            break
        human_capital_content.append(div.get_text(strip=True, separator=" "))
    human_capital_text = '\n'.join(human_capital_content)
    return human_capital_text


def DIBS(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    human_capital_div = soup.find('div', string=lambda text: text and 'Human Capital' in text)
    if not human_capital_div:
        return ""
    next_divs = human_capital_div.find_next_siblings('div')
    human_capital_content = []
    for div in next_divs:
        span = div.find("span")
        if not div.get_text(strip=True, separator=" "):
            continue
        if 'style' in span.attrs and "font-weight:700" in span.attrs['style']:
            break
        human_capital_content.append(div.get_text(strip=True, separator=" "))
    human_capital_text = '\n'.join(human_capital_content)
    return human_capital_text
