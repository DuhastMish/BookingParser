# BookingParser.

Parser of hotels from Russian booking, which collects information in SQLAlchemy.

## Collected data.
Collected data for Russian hotels:
### Table "hotels"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id (Primary key)  |
| name  | Name  |
| score   | Rating  |
| price  | Price  |
| image  | Link to image thumbnail  |
| link   | Hotel link  |
| name  | Name  |
| city   | City  |
| open_date  | Registration date on booking  |

### Table "coordinates"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id   |
| latitude   | Latitude  |
| longitude  | Longitude  |
### Table "extended_rating"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id  |
| rating_name  | Rating name  |
| rating_value   | Rating  |
### Table "important_facilities"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id  |
| important_facilities  | A string with all popular services  |
### Table "neighborhood_structures"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id  |
| neighborhood_structure  | Structure name  |
| structure_type   | Structure type  |
| distance   | Distance from hotel  |
### Table "review_rating"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id  |
| rating_name  | Rating interval  |
| review_rating_count   | Number of reviews  |
### Table "services_offered"
| column_name  | Description |
| ------------- | ------------- |
| hotel_id  | Hotel id  |
| services_offered  | Service offered name  |
| value   | The main amenities of this service  |

## Installation.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install -r requirements.txt
```

## Running.
```
python booking.py
```

### Collect data.
```
python booking.py --get-data
```

## Contributing
Forks are welcome. For major changes, please open an issue first to discuss what you would like to change.