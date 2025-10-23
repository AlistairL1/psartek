# Psartek Vacation Games Website

A Django web application for hosting interactive games and contests for Psartek vacation trips. The platform features two main games: a transportation prediction poll and a GeoGuessr-style location guessing game.

## 🎮 Features

### Games
1. **Transport Prediction Poll** - Users guess which transportation methods will be used during the trip
2. **Map Guess (GeoGuessr)** - Users pinpoint their guess for the vacation destination on an interactive map

### User Features
- User authentication and login system
- Personalized game interface
- View and modify responses (until admin verification)
- Leaderboard and results display
- Session management (30-minute sessions)

### Admin/Organizer Features
- Evaluate and verify user responses
- Assign scores to players
- View all responses
- Delete responses if needed
- Access to detailed statistics

## 🛠️ Tech Stack

- **Backend**: Django 5.1.7
- **Database**: SQLite3 (development)
- **Frontend**: HTML, CSS (with Font Awesome icons)
- **Python**: 3.x

## 📋 Prerequisites

- Python 3.x
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository** (or navigate to the project directory)
   ```bash
   cd psartek
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Games: http://127.0.0.1:8000/games/

## 👥 User Roles

### Regular Users
- Participate in games
- View their own responses
- Check leaderboard
- Modify responses until admin verification

### Organizers
- Access to all user responses
- Evaluate and score responses
- Delete responses
- View comprehensive statistics

### Technicians
- Excluded from leaderboard rankings
- Can participate in games but won't appear in results

## 🎯 Game Rules

### Transport Prediction Poll
- Select one or more transportation methods from the available options:
  - Voiture (Car)
  - Train
  - Bus
  - Avion (Plane)
  - Bateau (Ship)
  - Marche (Walking)
  - Vélo (Bike)
  - Métro/RER (Subway)

### Map Guess
- Click on the map to indicate your guess for the destination
- Optionally enter the city name
- Responses are scored based on accuracy

## 📊 Scoring System

- Organizers manually assign scores to participants
- Scores are stored in the `total_score` field
- Leaderboard displays ranked results
- Users can only modify responses before admin verification

## 📁 Project Structure

```
psartek/
├── games/                    # Main games application
│   ├── models.py            # TransportGuess and MapGuess models
│   ├── views.py             # Game logic and views
│   ├── urls.py              # URL routing
│   ├── admin.py             # Admin interface configuration
│   ├── templates/           # HTML templates
│   └── static/              # CSS, images, and static files
├── users/                    # User authentication app
│   ├── views.py             # Login/logout views
│   ├── urls.py              # URL routing
│   └── templates/           # HTML templates
├── psartek_website/         # Main Django project
│   ├── settings.py          # Django settings
│   └── urls.py              # Root URL configuration
├── manage.py                # Django management script
├── db.sqlite3               # SQLite database
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Settings
Key settings in `psartek_website/settings.py`:
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Configure for your domain
- `SESSION_COOKIE_AGE`: 1800 seconds (30 minutes)
- `SESSION_SAVE_EVERY_REQUEST`: True

### Database
Currently using SQLite3. For production, consider switching to PostgreSQL:
- Update `DATABASES` in `settings.py`
- Use `psycopg2-binary` (already in requirements.txt)

## 🚢 Deployment

The application is configured to run on PythonAnywhere:
- Host: `alistonks.pythonanywhere.com`
- Static files are collected in the `staticfiles/` directory

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use a production database (PostgreSQL recommended)
- [ ] Set up secure `SECRET_KEY`
- [ ] Configure HTTPS
- [ ] Set up proper static file serving

## 📝 Admin Features

### Creating Organizer Groups
To create an organizer group in Django admin:
1. Go to Groups section
2. Create a new group named "Organisateur"
3. Assign users to this group

### Managing Responses
- View all responses in the admin panel
- Update `is_verified` status
- Modify `total_score` values
- Delete responses if needed

## 🎨 Customization

### Adding New Transport Options
Edit `games/models.py`:
```python
TRANSPORT_CHOICES = [
    ('car', 'Voiture'),
    # Add your new option here
    ('new_option', 'New Transport'),
]
```

### Styling
CSS files are located in:
- `games/static/css/` - Game-specific styles
- `users/static/css/` - User app styles

## 🐛 Troubleshooting

### Common Issues

1. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` in settings

2. **Database errors**
   - Run `python manage.py migrate`
   - Check database file permissions

3. **Session expiry**
   - Sessions expire after 30 minutes of inactivity
   - Users need to log in again

## 📄 License

This project is developed for Psartek internal use.

## 👨‍💻 Development

### Making Changes
1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Run `python manage.py makemigrations` if models changed
5. Run `python manage.py migrate`
6. Test the application

### Testing
Run Django tests:
```bash
python manage.py test
```

## 📞 Support

For issues or questions, contact the development team.

---

**Note**: This application is designed for the Psartek vacation trip in April 2025 (19-26).

