class BookingParser:  # noqa:D100
    def name(self, hotel):
        """Возвращает имя отеля."""
        if hotel.select_one("span.sr-hotel__name") is None:
            return ''
        else:
            return hotel.select_one("span.sr-hotel__name").text.strip()

    def rating(self, hotel):
        """Возвращает рейтинг отеля."""
        if hotel.select_one("div.bui-review-score__badge") is None:
            return ''
        else:
            return hotel.select_one("div.bui-review-score__badge").text.strip()

    def price(self, hotel):
        """Возвращает даты на выбранные период времени."""
        if hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper") is None:
            return ''
        else:
            return hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper"
                                    ).text.strip()[:-5].replace(" ", "")

    def detail_link(self, hotel):
        """Возвращает ссылку на отель."""
        if hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button") is None:
            return ''
        else:
            return hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button")['href']

    def image(self, hotel):
        """Возвращает ссылку на изображение отеля."""
        if hotel.select_one("img.hotel_image") is None:
            return ''
        else:
            return hotel.select_one("img.hotel_image")['src']

    def coordinates(self, soup):
        """Получает координаты отеля."""
        coordinates = []
        if soup.select_one("#hotel_sidebar_static_map") is None:
            coordinates.append('')
            coordinates.append('')
        else:
            coordinates.append(soup.select_one(
                "#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[0])
            coordinates.append(soup.select_one(
                "#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[1])

        return coordinates

    def important_facilites(self, soup):
        """Возвращает важные услуги."""
        if soup.select_one(
                "div.hp_desc_important_facilities.clearfix.hp_desc_important_facilities--bui") is None:
            return []
        else:
            return list(dict.fromkeys([service.text.strip() for service in soup.findAll(
                "div", {"class": "important_facility"})]))

    def offered_services(self, soup):
        """Возвращает предлагаемые услуги отелем."""
        services_offered_list = []

        if soup.select_one('div.facilitiesChecklist') is None:
            services_offered_list = []
        else:

            for services in soup.findAll("div", class_="facilitiesChecklistSection"):

                services_offered = {}
                services_offered['type'] = services.find("h5").text.strip()

                services_offered['value'] = []
                for checks in services.findAll("li"):

                    if checks.find("p") is not None:
                        services_offered['value'].append(
                            checks.findNext(
                                "p").text.strip().replace("\n", " ").replace("\r", " ").replace("  ", " "))

                    elif checks.find("span") is not None:
                        services_offered['value'].append(checks.find("span").text.strip())
                    else:
                        services_offered['value'].append(checks.text.strip())

                services_offered_list.append(services_offered)

        return services_offered_list

    def neighborhood_structures(self, soup):
        """Возвращает ближайщие достопримечательности."""
        neighborhood_list = []

        if soup.select_one('div.hp-poi-content-container.hp-poi-content-container--column.clearfix') is None:
            neighborhood_list = []
        else:
            for neighborhood in soup.select_one(
                    'div.hp-poi-content-container.hp-poi-content-container--column.clearfix').findAll(
                        'li', {"class": "bui-list__item"}):
                neighborhood_structures = {}

                if neighborhood.find("div", {"class": "hp-poi-list__description"}).contents[0].strip() == '':
                    neighborhood_structures['name'] = neighborhood.find(
                        "div", {"class": "hp-poi-list__description"}).span.text.strip()
                else:
                    neighborhood_structures['name'] = neighborhood.find(
                        "div", {"class": "hp-poi-list__description"}).contents[0].strip()

                try:
                    neighborhood_structures['structure_type'] = neighborhood.find(
                        "div", {"class": "hp-poi-list__body"}).select_one(
                            "span.bui-badge.bui-badge--outline").text.strip()
                except AttributeError:
                    neighborhood_structures['structure_type'] = ''

                try:
                    neighborhood_structures['distance'] = neighborhood.find(
                        'span', {"class": "hp-poi-list__distance"}).text.strip()
                except AttributeError:
                    neighborhood_structures['distance'] = ''

                neighborhood_list.append(neighborhood_structures)

        return neighborhood_list
