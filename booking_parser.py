import logging  # noqa : D100


RU_MONTH_VALUES = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12',
}


class BookingParser:  # noqa
    def __init__(self, hotel):  # noqa
        self.hotel = hotel

    def name(self):
        """Возвращает имя отеля."""
        logging.info('Getting hotel name.')
        if self.hotel.select_one("span.sr-hotel__name") is None:
            return ''
        else:
            return self.hotel.select_one("span.sr-hotel__name").text.strip().replace("'", '')

    def rating(self):
        """Возвращает рейтинг отеля."""
        logging.info('Getting hotel rating.')
        if self.hotel.select_one("div.bui-review-score__badge") is None:
            return ''
        else:
            return self.hotel.select_one("div.bui-review-score__badge").text.strip().replace(',', '.')

    def city(self):
        """Возвращает город отеля."""
        logging.info('Getting hotel city.')
        if self.hotel.select_one("div.sr_card_address_line") is None:
            return ''
        else:
            return self.hotel.select_one(
                "div.sr_card_address_line").text.strip().split('\n')[0].replace("'", '')

    def price(self):
        """Возвращает даты на выбранные период времени."""
        logging.info('Getting hotel minimal price.')
        if self.hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper") is None:
            return ''
        else:
            return self.hotel.select_one(
                "div.bui-price-display__value.prco-inline-block-maker-helper"
                ).text.strip()[:-5].replace(" ", "")

    def star(self):
        """Return hotel stars."""
        logging.info('Getting hotel stars.')
        if self.hotel.select_one("span.bui-rating.bui-rating--smaller") is None:
            return ''
        else:
            return int(self.hotel.select_one(
                "span.bui-rating.bui-rating--smaller")['aria-label'].split(' ')[0])

    def detail_link(self):
        """Возвращает ссылку на отель."""
        logging.info('Getting hotel link.')
        if self.hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button") is None:
            return ''
        else:
            link = self.hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button")['href']
            logging.info(f'Hotel link: https://www.booking.com{link}.')
            return link

    def image(self):
        """Возвращает ссылку на изображение отеля."""
        logging.info('Getting hotel image link.')
        if self.hotel.select_one("img.hotel_image") is None:
            return ''
        else:
            return self.hotel.select_one("img.hotel_image")['src']

    def coordinates(self, soup):
        """Получает координаты отеля."""
        logging.info('Getting hotel coordinates.')
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
        logging.info('Getting hotel important facilities.')
        if soup.select_one(
                "div.hp_desc_important_facilities.clearfix.hp_desc_important_facilities--bui") is None:
            return []
        else:
            return list(dict.fromkeys([service.text.strip() for service in soup.findAll(
                "div", {"class": "important_facility"})]))

    def offered_services(self, soup):
        """Возвращает предлагаемые услуги отелем."""
        logging.info('Getting hotel service offered.')
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
        logging.info('Getting hotel neighbothood structures.')
        neighborhood_list = []

        if soup.select_one(
                'div.hp_location_block__content_container.hp-poi-content-container--column') is None:
            neighborhood_list = []
        else:
            for neighborhood in soup.select_one(
                    'div.hp_location_block__content_container.hp-poi-content-container--column').findAll(
                        'li', {"class": "bui-list__item"}):
                neighborhood_structures = {}
                logging.info('Getting hotel neighbothood structures name.')
                if neighborhood.find("div", {"class": "bui-list__description"}).contents[0].strip() == '':
                    neighborhood_structures['name'] = neighborhood.find(
                        "div", {"class": "bui-list__description"}).contents[-1].strip().replace("'", '')
                else:
                    neighborhood_structures['name'] = neighborhood.find(
                        "div", {"class": "bui-list__description"}).contents[-1].strip().replace("'", '')

                try:
                    logging.info('Getting hotel neighbothood structures type.')
                    neighborhood_structures['structure_type'] = neighborhood.find(
                        "div", {"class": "bui-list__body"}).select_one(
                            "span.hp_location_block__section_list_key_tag").text.strip()
                except AttributeError:
                    logging.error('Maybe structure type is none?')
                    neighborhood_structures['structure_type'] = ''

                try:
                    logging.info('Getting hotel neighbothood structures distance.')
                    neighborhood_structures['distance'] = neighborhood.find(
                        'div', {"class": "bui-list__body"}).select_one(
                            "div.bui-list__item-action.hp_location_block__section_list_distance").text.strip()
                except AttributeError:
                    logging.error('Cant get distance.')
                    neighborhood_structures['distance'] = ''
                neighborhood_list.append(neighborhood_structures)

        return neighborhood_list

    def extended_rating(self, soup):
        """Get an extended rating from which the normal rating is added."""
        logging.info('Getting hotel extended rating.')
        extended_rating = {}
        if soup.select_one('div.v2_review-scores__body.v2_review-scores__body--compared_to_average') is None:
            logging.error('Cant get extended rating.')
            extended_rating = {}
        else:
            for rating in soup.select_one(
                'div.v2_review-scores__body.v2_review-scores__body--compared_to_average').findAll(
                    'li', {"class": "v2_review-scores__subscore"}):
                rating_name = rating.find("div", {"class": "c-score-bar"}).contents[0].text.strip()
                rating_score = rating.find("div", {"class": "c-score-bar"}).contents[1].text
                extended_rating[rating_name] = rating_score
        return extended_rating

    def review_rating(self, soup):
        """Get the number of reviews by rating."""
        logging.info('Getting hotel review rating.')
        reviews_rating = {}
        if soup.select_one('div.scores_full_layout') is None:
            logging.error('Cant get extended rating.')
            reviews_rating = {}
        else:
            for review_rating in soup.select_one('div.scores_full_layout').findAll(
                    'li', {"class": "clearfix"}):
                rating_class = review_rating.find("p", {"class": "review_score_name"}).text.strip()
                rating_score = review_rating.find("p", {"class": "review_score_value"}).text.strip()
                reviews_rating[rating_class] = rating_score

        return reviews_rating

    def open_hotel_date(self, soup):
        """Get the date of registration of the hotel on booking.com."""
        logging.info('Getting hotel booking registration date.')
        if soup.select_one('span.hp-desc-highlighted') is None:
            logging.error('Cant get hotel date.')
            return ''
        else:
            open_date_text = soup.select_one('span.hp-desc-highlighted').text.strip()
            if " с " in open_date_text:
                index = soup.select_one('span.hp-desc-highlighted').text.strip().find(" с ")
                date = open_date_text[index+3:].replace('.', '')
                try:
                    day, month, year = date.split(' ')
                    month = RU_MONTH_VALUES[month[0:3]]
                    date = '/'.join([day, month, year])
                except Exception:
                    logging.error('Cant get hotel date.')
                    return ''
                return date
            else:
                logging.error('Cant get hotel date.')
                return ''

    def apartaments(self, soup):
        """Get apartaments information of the hotel on booking.com."""
        logging.info('Getting hotel apartaments information.')
        apartaments = []
        if soup.select_one('table.hprt-table') is None:
            logging.error('Cant apartaments information.')
            return apartaments
        else:
            apartament_name = ''
            for apart in soup.select_one('table.hprt-table').findAll('tr')[1:]:
                apartament = {}
                try:
                    logging.info('Getting apartaments name.')
                    apartament['name'] = apartament_name = apart.select_one(
                        'span.hprt-roomtype-icon-link').text.strip()
                except AttributeError:
                    logging.error('Cant apartaments name.')
                    apartament['name'] = apartament_name
                try:
                    logging.info('Getting apartaments price.')
                    apartament['price'] = int(apart.select_one(
                        'div.bui-price-display__value.prco-inline-block-maker-helper.prco-font16-helper'
                        ).text.strip()[:-5].replace(" ", ""))
                except Exception:
                    logging.error('Cant apartaments price.')
                    continue
                try:
                    logging.info('Getting apartaments capacity.')
                    apartament['capacity'] = apart.select_one(
                        'div.c-occupancy-icons.hprt-occupancy-occupancy-info'
                        ).select_one('span.bui-u-sr-only').text.strip().split(':')[1].strip()
                except AttributeError:
                    logging.error('Cant apartaments capacity.')
                    continue
                apartaments.append(apartament)

        return apartaments
