# Social Media Django Project

This is a Django-based social media application. It includes features such as user authentication, profile management, posting images, reels, and more.


##Checkout the Website :
https://chatx31.pythonanywhere.com/

## Features
- User signup, login, and profile management
- Post images and reels
- Explore and search users
- Admin panel for custom management

## Project Structure
- `socialmedia/` - Main Django project
- `customadmin/` - Custom admin app
- `userauth/` - User authentication app
- `media/` - Uploaded media files
- `static/` - Static files (CSS, JS)

## Setup Instructions
1. Create and activate a virtual environment:
   ```cmd
   python -m venv env
   env\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```cmd
   python manage.py migrate
   ```
4. Start the development server:
   ```cmd
   python manage.py runserver
   ```

## License
MIT
