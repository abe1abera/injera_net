#  InjeraNet - Smart Local Food Delivery System

![Django](https://img.shields.io/badge/Django-4.2-green)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14-blue)
![JWT](https://img.shields.io/badge/JWT_Authentication-Secure-orange)

## Project Overview

InjeraNet is a comprehensive backend platform that digitalizes local food businesses, specifically targeting traditional food makers like injera producers. The system connects customers, food makers, delivery partners, and suppliers in one organized ecosystem.

## Live Demo Video: [https://www.loom.com/share/97a3d70f2fd748dba3888ef4f4392222]

## Problem Statement

Local food businesses in many communities operate informally:
-  Order management through phone calls and word-of-mouth
- Manual inventory tracking leading to stockouts  
-  Unreliable delivery coordination
- No sales analytics or performance tracking

InjeraNet solves these problems by providing a structured digital platform.

##  Key Features

###  Multi-Role User System
- Customers: Browse menu, place orders, track deliveries
- Makers: Manage products, accept orders, track inventory
- Delivery Partners: Accept deliveries, update status, view earnings
- Suppliers: Manage ingredient supplies
- Admin: Platform management and analytics

### Complete Order Workflow

Order Placement → Payment Processing → Maker Acceptance → 
Delivery Assignment → Real-time Tracking → Delivery Completion
`

###  Payment System
- Automated payment record creation
- Payment status tracking (Pending → Paid → Refunded)
- Simulation of mobile money integration

###  Smart Delivery Management
- Automatic delivery partner assignment
- Real-time delivery status updates
- Delivery partner availability tracking

###  Business Intelligence
    Maker Analytics: Sales performance, top products, revenue
   Customer Analytics: Order history, spending patterns
    Delivery Analytics: Completion rates, efficiency metrics
    Admin Dashboard: Platform-wide statistics

###  Inventory Management
- Stock level tracking
- Low-stock alerts and notifications
- Automated inventory updates

###  Notification System
- Real-time order updates
- Payment confirmations
- Delivery status notifications
- Low-stock alerts

##  Technology Stack

   Backend Framework: Django 4.2 & Django REST Framework
    Database: SQLite (Development)
   Authentication: JWT (JSON Web Tokens)
- Testing: Thunder Client
- Version Control: Git & GitHub

##  Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/abe1abera/injera_net
   cd injera_net
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - JWT token obtain
- `POST /api/auth/refresh/` - Token refresh

### Core API Endpoints
- `GET/POST /api/products/` - Product management
- `GET/POST /api/orders/` - Order operations
- `GET/POST /api/payments/` - Payment processing
- `GET/POST /api/deliveries/` - Delivery management
- `GET/POST /api/inventory/` - Inventory tracking
- `GET/POST /api/notifications/` - Notifications
- `GET/POST /api/reviews/` - Customer reviews
- `GET /api/analytics/` - Business analytics

### Order Workflow Actions
- `POST /api/orders/{id}/accept/` - Accept order (Maker)
- `POST /api/orders/{id}/mark_paid/` - Mark as paid
- `POST /api/orders/{id}/assign_delivery/` - Assign delivery
- `POST /api/orders/{id}/mark_delivered/` - Mark as delivered

## 🧪 Testing the API

### Using Thunder Client in VS Code

1. **Install Thunder Client Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Thunder Client" and install

2. **Test User Registration**
   ```http
   POST http://127.0.0.1:8000/api/auth/register/
   Content-Type: application/json

   {
     "username": "test_customer",
     "email": "customer@test.com",
     "password": "password123",
     "password2": "password123",
     "role": "customer"
   }
   ```

3. **Test Login & Get Token**
   ```http
   POST http://127.0.0.1:8000/api/auth/login/
   Content-Type: application/json

   {
     "username": "test_customer",
     "password": "password123"
   }
   ```

4. **Test Complete Workflow**
   - Use the token in Authorization header: `Bearer YOUR_TOKEN`
   - Create products, place orders, process payments, assign deliveries

## 🗄️ Database Models

- **User**: Custom user model with 5 roles
- **Product**: Food items with pricing and stock
- **Order**: Customer orders with status tracking
- **Payment**: Transaction records
- **Delivery**: Delivery tracking and partner assignment
- **Inventory**: Stock management
- **Notification**: System messages and alerts
- **Review**: Customer feedback and ratings

## 👥 User Roles & Permissions

Role  Permissions 

Customer  Place orders, view history, make payments  Maker  Manage products, accept orders, view analytics 
Delivery Partner  Accept deliveries, update status, view earnings 
Supplier  Manage inventory supplies 
Admin  Full system access and management 

## 🎬 Demo Video

[https://www.loom.com/share/97a3d70f2fd748dba3888ef4f4392222]

Watch the complete demo video showing:
- User registration and authentication
- Complete order workflow
- Payment processing
- Delivery management
- Analytics dashboard
- Notification system

##  Future Enhancements

- Real payment gateway integration
- Mobile app development
- Delivery route optimization
- SMS notifications
- Multi-language support

##  Author

ABEL ABERA BELETE  
- GitHub: [abe1abers](https://github.com/abe1abera)

##  License

This project is licensed under the MIT License.

---

**Built with  using Django REST Framework**
