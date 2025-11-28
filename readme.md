# Django Social Chat Application

A full-featured social media platform with real-time chat functionality built with Django and WebSockets.

## 📋 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Architecture](#project-architecture)
- [Database Schema](#database-schema)
- [Folder Structure](#folder-structure)
- [Installation & Setup](#installation--setup)
- [Workflow](#workflow)
- [API Endpoints](#api-endpoints)
- [WebSocket Routes](#websocket-routes)

---

## ✨ Features

### Social Media Features
- **User Authentication**: Register, login, logout with profile management
- **User Profiles**: Customizable profiles with avatar, bio, and personal information
- **Follow System**: Follow/unfollow users to build your network
- **Posts**: Create, edit, delete posts with image support
- **Likes & Comments**: Interact with posts through likes and comments
- **Real-time Notifications**: Get notified about likes, comments, and follows
- **Feed**: Personalized feed showing posts from followed users

### Chat Features
- **Real-time Messaging**: WebSocket-based instant messaging
- **Friend-only Chat**: Only mutual followers can chat
- **Unread Message Tracking**: Visual indicators for unread messages
- **Chat Rooms**: Persistent one-on-one chat rooms
- **Message History**: All messages stored and retrievable
- **Live Badge Updates**: Real-time unread count updates on navbar

---

## 🛠 Technologies Used

### Backend
- **Python 3.11+**
- **Django 5.1.3** - Web framework
- **Django Channels 4.x** - WebSocket support
- **Daphne** - ASGI server for WebSocket handling
- **SQLite** - Database (can be switched to PostgreSQL)

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5.3** - UI framework
- **Font Awesome 6.4** - Icons
- **JavaScript (Vanilla)** - WebSocket client, AJAX

### Real-time Communication
- **WebSocket Protocol** - Bi-directional communication
- **ASGI (Asynchronous Server Gateway Interface)**
- **Channel Layers** - In-memory for development

---

## 🏗 Project Architecture

```
┌────────────────────────────────────────────────────────────┐
│                        Client Browser                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML/CSS   │  │  JavaScript  │  │  WebSocket   │      │
│  │  Bootstrap   │  │    AJAX      │  │   Client     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS & WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Django Application                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   ASGI Application                   │   │
│  │  ┌────────────┐              ┌──────────────────┐    │   │
│  │  │   HTTP     │              │    WebSocket     │    │   │
│  │  │  Handler   │              │     Handler      │    │   │
│  │  │ (Django)   │              │   (Channels)     │    │   │
│  │  └────────────┘              └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                              │
│  ┌─────────────────┬─────────┴────────┬──────────────────┐  │
│  │                 │                  │                  │  │
│  │   Views Layer   │  Consumers Layer │  Models Layer    │  │
│  │                 │                  │                  │  │
│  │  • User Views   │  • ChatConsumer  │  • User          │  │
│  │  • Post Views   │  • Notification  │  • Profile       │  │
│  │  • Chat Views   │    Consumer      │  • Post          │  │
│  │  • Profile      │                  │  • Comment       │  │
│  │                 │                  │  • ChatRoom      │  │
│  │                 │                  │  • Message       │  │
│  │                 │                  │  • Notification  │  │
│  └─────────────────┴──────────────────┴──────────────────┘  │
│                              │                            │
│                              ▼                              │
│                    ┌──────────────────┐                     │
│                    │  Channel Layers  │                     │
│                    │  (In-Memory)     │                     │
│                    └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  SQLite Database │
                    └──────────────────┘
```

---

## 🗄 Database Schema

### Core Models

#### **User (Django Built-in)**
```python
- id (PK)
- username (unique)
- email (unique)
- password (hashed)
- first_name
- last_name
- is_active
- date_joined
```

#### **Profile**
```python
- id (PK)
- user (FK → User, OneToOne)
- bio (Text)
- location (String)
- birth_date (Date)
- avatar (ImageField)
- created_at (DateTime)
```

#### **Follow**
```python
- id (PK)
- follower (FK → User)
- following (FK → User)
- created_at (DateTime)
- UNIQUE(follower, following)
```

#### **Post**
```python
- id (PK)
- author (FK → User)
- content (Text)
- image (ImageField, optional)
- created_at (DateTime)
- updated_at (DateTime)
```

#### **Comment**
```python
- id (PK)
- post (FK → Post)
- author (FK → User)
- content (Text)
- created_at (DateTime)
```

#### **Like**
```python
- id (PK)
- post (FK → Post)
- user (FK → User)
- created_at (DateTime)
- UNIQUE(post, user)
```

#### **ChatRoom**
```python
- id (PK)
- users (ManyToMany → User)
- created_at (DateTime)
```

#### **Message**
```python
- id (PK)
- room (FK → ChatRoom)
- sender (FK → User)
- text (Text)
- is_read (Boolean)
- timestamp (DateTime)
```

#### **Notification**
```python
- id (PK)
- recipient (FK → User)
- sender (FK → User)
- notification_type (String: like/comment/follow)
- post (FK → Post, optional)
- message (Text)
- is_read (Boolean)
- created_at (DateTime)
```

### Entity Relationship Diagram

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│   User   │◄───────►│ Profile  │         │  Follow  │
│          │  1:1    │          │         │          │
│  • id    │         │  • bio   │         │follower  │
│  • name  │         │  • avatar│         │following │
└────┬─────┘         └──────────┘         └──────────┘
     │                                         │
     │ 1:N                                     │
     ▼                                         │
┌──────────┐         ┌──────────┐              │
│   Post   │◄───────►│ Comment  │              │
│          │  1:N    │          │              │
│  • id    │         │  • id    │              │
│  • image │         │  • text  │              │
└────┬─────┘         └──────────┘              │
     │                                         │
     │ 1:N                                     │
     ▼                                         │
┌──────────┐                                   │
│   Like   │                                   │
│          │                                   │
│  • post  │                                   │
│  • user  │                                   │
└──────────┘                                   │
                                               │
┌──────────┐         ┌──────────┐              │
│ ChatRoom │◄───────►│ Message  │              │
│          │  1:N    │          │              │
│  • users │         │  • text  │              │
│  (M2M)   │         │  • read  │              │
└──────────┘         └──────────┘              │
     ▲                                         │
     │ M:N                                     │
     └─────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
chatapp/
│
├── core/                           # Project settings
│   ├── __init__.py
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # Main URL configuration
│   ├── asgi.py                     # ASGI config for WebSocket
│   └── wsgi.py                     # WSGI config for production
│
├── userapp/                        # User authentication & profiles
│   ├── migrations/
│   ├── templates/
│   │   └── userapp/
│   │       ├── base.html           # Base template with navbar
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── profile.html
│   │       └── edit_profile.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Profile, Follow models
│   ├── forms.py                    # User & Profile forms
│   ├── views.py                    # Auth & profile views
│   └── urls.py
│
├── posts/                          # Posts, likes, comments
│   ├── migrations/
│   ├── templates/
│   │   └── posts/
│   │       ├── feed.html           # Main feed
│   │       ├── create_post.html
│   │       ├── post_detail.html
│   │       └── notifications.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Post, Comment, Like, Notification
│   ├── forms.py
│   ├── views.py                    # Post CRUD, likes, comments
│   └── urls.py
│
├── chat/                           # Real-time chat
│   ├── migrations/
│   ├── templates/
│   │   └── chat/
│   │       ├── chat_list.html      # List of friends to chat with
│   │       ├── chat_room.html      # Chat interface
│   │       └── not_friend.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # ChatRoom, Message
│   ├── views.py                    # Chat views
│   ├── urls.py
│   ├── consumers.py                # WebSocket consumers
│   └── routing.py                  # WebSocket URL routing
│
├── media/                          # User uploads
│   ├── avatars/                    # Profile pictures
│   └── posts/                      # Post images
│
├── static/                         # Static files (CSS, JS, images)
│
├── db.sqlite3                      # SQLite database
├── manage.py                       # Django management script
└── requirements.txt                # Python dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd chatapp
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install django==5.1.3
pip install channels
pip install daphne
pip install Pillow
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
Django==5.1.3
channels==4.0.0
daphne==4.0.0
Pillow==10.1.0
```

### Step 4: Configure Settings

Ensure `core/settings.py` has:

```python
INSTALLED_APPS = [
    'daphne',  # Must be first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'userapp',
    'posts',
    'chat',
]

ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Or with Daphne (recommended for WebSocket):
```bash
daphne -p 8000 core.asgi:application
```

### Step 8: Access the Application

- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 🔄 Workflow

### User Registration & Authentication Flow

```
1. User visits homepage
2. Clicks "Register"
3. Fills registration form (username, email, password)
4. System creates User + Profile
5. Redirects to login
6. User logs in
7. Redirects to feed
```

### Social Interaction Flow

```
┌─────────────┐
│  View Feed  │
└──────┬──────┘
       │
       ├─► Like Post ──► Notification sent to post author
       │
       ├─► Comment ────► Notification sent to post author
       │
       ├─► Follow User ─► Notification sent to followed user
       │
       └─► View Profile ─► Follow/Unfollow actions
```

### Real-time Chat Flow

```
User A                          Server                          User B
  │                               │                               │
  ├──── Opens chat room ─────────►│                               │
  │                               ├──── WebSocket connect ────────┤
  │                               │                               │
  ├──── Types message ───────────►│                               │
  │                               ├──── Save to DB ───────────────┤
  │                               │                               │
  │                               ├──── Broadcast via WS ────────►│
  │                               │                               │
  │◄──── Message appears ─────────┤                               │
  │                               │                               ├─► Message appears
  │                               │                               │
  │                               ├──── Update unread count ─────►│
  │                               │      (if B not in chat)       │
```

### Notification System Flow

```
Action Trigger (Like/Comment/Follow)
         │
         ▼
  Create Notification
  (sender, recipient, type)
         │
         ▼
  Save to Database
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
  HTTP Polling        WebSocket Push
  (every 30s)        (real-time)
         │                  │
         └────────┬─────────┘
                  │
                  ▼
         Update Badge Count
         on Navbar
```

---

## 🌐 API Endpoints

### Authentication
```
GET  /user/login/              - Login page
POST /user/login/              - Login submit
GET  /user/register/           - Registration page
POST /user/register/           - Register submit
GET  /user/logout/             - Logout
```

### Profile
```
GET  /user/profile/<username>/ - View profile
GET  /user/edit-profile/       - Edit profile form
POST /user/edit-profile/       - Update profile
POST /user/follow/<username>/  - Follow user
POST /user/unfollow/<username>/ - Unfollow user
```

### Posts
```
GET  /posts/                   - Feed (posts from followed users)
GET  /posts/create/            - Create post form
POST /posts/create/            - Submit new post
GET  /posts/<id>/              - Post detail
POST /posts/<id>/edit/         - Edit post
POST /posts/<id>/delete/       - Delete post
POST /posts/<id>/like/         - Toggle like
POST /posts/<id>/comment/      - Add comment
```

### Notifications
```
GET  /posts/notifications/            - View all notifications
GET  /posts/notifications/unread-count/ - Get unread count (JSON)
POST /posts/notifications/mark-read/   - Mark notification as read
```

### Chat
```
GET  /chat/                    - List of friends to chat with
GET  /chat/room/<username>/    - Chat room with specific user
GET  /chat/unread-count/       - Get unread message count (JSON)
```

---

## 🔌 WebSocket Routes

### Chat WebSocket
```
ws://localhost:8000/ws/chat/<room_id>/
```

**Events:**
- **Connect**: Join chat room, mark messages as read
- **Receive**: Handle incoming messages, save to DB, broadcast to room
- **Disconnect**: Leave room group

**Message Format:**
```json
// Client → Server
{
  "message": "Hello, how are you?"
}

// Server → Client
{
  "type": "chat_message",
  "message": "Hello, how are you?",
  "sender": "username",
  "sender_name": "John Doe",
  "timestamp": "2024-11-28T10:30:00Z"
}
```

### Notification WebSocket
```
ws://localhost:8000/ws/notifications/
```

**Events:**
- **Connect**: Join user's personal notification group
- **unread_update**: Notify client to refresh unread counts

**Message Format:**
```json
{
  "type": "unread_update",
  "action": "increment" | "refresh"
}
```

---

## 🎨 UI Features

### Responsive Design
- Mobile-first approach
- Bootstrap 5 grid system
- Collapsible navbar on mobile

### Real-time Updates
- WebSocket connections for instant messaging
- Auto-updating notification badges
- Live chat message delivery
- Unread message indicators

### User Experience
- Form validation
- Loading states
- Error messages
- Success notifications
- Smooth scrolling in chat
- Auto-scroll to latest message

---

## 🔒 Security Features

- **CSRF Protection**: Django built-in CSRF tokens
- **Password Hashing**: Django's PBKDF2 algorithm
- **Authentication Required**: `@login_required` decorators
- **WebSocket Authentication**: User authentication check in consumers
- **Friend-only Chat**: Mutual follow verification
- **SQL Injection Prevention**: Django ORM parameterized queries
- **XSS Prevention**: Template auto-escaping

---



## 🚀 Production Deployment

### Recommended Setup

1. **Database**: Switch to PostgreSQL
2. **Channel Layer**: Use Redis instead of in-memory
3. **Static Files**: Configure AWS S3 or similar
4. **Media Files**: Use cloud storage
5. **HTTPS**: Required for WebSocket (wss://)
6. **Environment Variables**: Store secrets securely

### Settings for Production

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### Run with Gunicorn + Daphne

```bash
# HTTP workers
gunicorn core.wsgi:application --bind 0.0.0.0:8000

# WebSocket workers
daphne -b 0.0.0.0 -p 8001 core.asgi:application
```

---

## 📝 Future Enhancements

- [ ] Group chat functionality
- [ ] Voice/video calls
- [ ] Story feature (temporary posts)
- [ ] Direct message requests for non-friends
- [ ] Search functionality (users, posts)
- [ ] Hashtags and trending topics
- [ ] Post sharing/reposting
- [ ] Message reactions
- [ ] Typing indicators
- [ ] Online/offline status
- [ ] Message search
- [ ] File attachments in chat
- [ ] Email notifications
- [ ] Two-factor authentication

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👥 Authors

- **Aayush Aryan** - Initial work

---

## 🙏 Acknowledgments

- Django documentation
- Django Channels documentation
- Bootstrap team
- Font Awesome
- Stack Overflow community

---

## 📧 Contact

For questions or support, please open an issue in the repository or contact [aayusharyan1210@gmail.com]

---

**Happy Coding! 🎉**