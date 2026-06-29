import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Comment, Follow, Post, UserProfile

USERS = [
    ('alice', 'Alice Nova', 'Designing calm interfaces and vivid weekends.', 'Paris'),
    ('bob', 'Bob Stone', 'Backend builder, coffee enthusiast, mountain walker.', 'Denver'),
    ('carol', 'Carol Moon', 'Photographer chasing soft light and tiny details.', 'Seoul'),
    ('dave', 'Dave Ray', 'Full-stack developer sharing experiments in public.', 'Berlin'),
    ('eve', 'Eve Vale', 'Product thinker, notes app collector, city explorer.', 'London'),
    ('frank', 'Frank West', 'Writer, traveler, and occasional CSS perfectionist.', 'Austin'),
]

POSTS = [
    'Shipping small improvements every day compounds faster than waiting for perfect.',
    'Found a quiet trail this morning and remembered how good offline feels.',
    'A clean feed is really a set of kind defaults.',
    'Prototype first, polish second, listen always.',
    'Golden hour made the whole street look like a movie set.',
    'Today I learned one thoughtful comment can change the direction of an idea.',
    'Building with Django still feels wonderfully direct.',
    'The best dashboards are boring in the places users need speed.',
    'Weekend sketchbook dump: color studies, layout grids, and too many arrows.',
    'Tiny rituals before deep work: water, notes, one clear goal.',
    'Refactored a feature and deleted more code than I added. Excellent feeling.',
    'Nature photos are basically free therapy with better lighting.',
    'Community is what happens when people keep showing up kindly.',
    'The comment section is open for book recommendations.',
    'Trying a new recipe tonight and pretending mise en place is a personality.',
    'A slow morning, a fast deploy, and a surprisingly good playlist.',
    'Reminder: your first draft only needs to exist.',
    'Social apps should make people feel more human, not more measured.',
]

COMMENTS = [
    'Love this perspective.', 'This is beautifully put.', 'Adding this to my notes.',
    'Totally agree.', 'That photo energy is immaculate.', 'Needed this today.'
]

AVATAR_URLS = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&h=400&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&h=400&q=80",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&h=400&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&h=400&q=80",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&h=400&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&h=400&q=80"
]

POST_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1511884642898-4c92249e20b6?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&h=500&q=80",
    "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&h=500&q=80"
]

class Command(BaseCommand):
    help = 'Create demo SocialSphere users, posts, follows, likes, and comments.'

    def handle(self, *args, **options):
        users = []
        for index, (username, full_name, bio, location) in enumerate(USERS):
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com', 'first_name': full_name.split()[0], 'last_name': full_name.split()[-1]})
            user.email = f'{username}@example.com'
            user.first_name = full_name.split()[0]
            user.last_name = full_name.split()[-1]
            user.set_password('password123')
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.bio = bio
            profile.location = location
            profile.website = f'https://example.com/{username}'
            profile.avatar = AVATAR_URLS[index % len(AVATAR_URLS)]
            profile.save()
            users.append(user)

        for index, content in enumerate(POSTS):
            post, _ = Post.objects.get_or_create(
                author=users[index % len(users)],
                content=content,
            )
            post.image_url = POST_IMAGE_URLS[index % len(POST_IMAGE_URLS)]
            post.save(update_fields=['image_url'])

        posts = list(Post.objects.all())
        for follower in users:
            for following in random.sample([u for u in users if u != follower], k=3):
                Follow.objects.get_or_create(follower=follower, following=following)

        for post in posts:
            for user in random.sample(users, k=random.randint(1, min(5, len(users)))):
                post.likes.add(user)
            for user in random.sample(users, k=random.randint(1, 3)):
                Comment.objects.get_or_create(post=post, author=user, content=random.choice(COMMENTS))

        self.stdout.write(self.style.SUCCESS('Seed data created. Login as alice / password123.'))
