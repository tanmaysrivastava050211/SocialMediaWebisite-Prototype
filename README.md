SocialSphere
A complete Django social media web application with authentication, feeds, posts, likes, comments, follows, profiles, responsive styling, and demo data.

Running Instructions
pip install django
cd socialapp
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver
Then open http://127.0.0.1:8000 and log in as alice / password123
