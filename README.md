# BookingParser.

Parser of hotels from Russian booking, which collects information in SQLAlchemy.

## Collected data.
Collected data for Russian hotels:
### Table "hotels"
Name
Rating
Price
Link to image thumbnail
Hotel link
City
Registration date on booking
### Table "coordinates"
Hotel coordinates (latitude and longitude)
### Table "extended_rating"
Extended rating (for example, rating for cleanliness, staff and others)
### Table "important_facilities"
Most popular services
### Table "neighborhood_structures"
Nearest district structures (with distance and type)
### Table "review_rating"
Number of reviews with different ratings
### Table "services_offered"
Services offered (room type and service offered for this room)

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