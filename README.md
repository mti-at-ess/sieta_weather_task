# Sieta Weather Task
## Instructions:

1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the django application: `python manage.py runserver`.
4. Access the API endpoints:
   - `/forecasts`: `http://localhost:8000/forecasts/?now=2020-11-01T00:00:00.0000&then=2020-11-01T00:00:00.0000`
   - `/tomorrow`: `http://localhost:8000/tomorrow/?now=2020-11-02T00:00:00.0000`

## Project Structure:

- `weather/`: Add directory for weather module, contains dataset, endpoints, views, etc.
- `sieta_weather_task/`: Django project app directory which includes overall project urls and settings file.
- `.gitignore`: Ignores unnecessary files from version control.
- `requirements.txt`: Project's library dependancies.
- `pytest.ini`: Configuration file for python test package.
- `.env`: Environment file
- `env.example`: Example environment file

## Testing:

Run unit tests from the root directory:

```bash
python -m pytest .
```