# LK Nails & Lashes Web App Summary

## Product Overview

Design and build a Django web application for `Lknailslashes.de`, a nails and lashes salon website rewritten from the current site `https://lknailslashes.de`.

The product should follow a feminine, soft, modern visual style, with strong frontend polish, clean UX, and Google SEO optimization. The public website should also include store information, embedded map/location details, and links to Instagram and Facebook.

## System Scope

The system has 2 main areas:

- `Public / Anyone`: view services, promotions, salon information, and book appointments online
- `Admin`: manage configuration, services, bookings, content, promotions, email templates, and reporting

## Language Support

- Default language: English
- Secondary language: Deutsch
- Users can switch language directly on the UI

## Service Management

Admin can manage the service catalog.

Each service includes:

- name
- category
- subcategory
- price
- duration in minutes
- active/inactive status
- multiple images

Initial service data should be imported from the provided JSON seed list.

## Booking Requirements

The system must support online booking with these rules:

- One customer can select multiple services in a single booking
- The booking UI must show:
  - total duration of all selected services
  - total estimated price
- Booking information includes:
  - customer name
  - phone number
  - email
  - selected services
  - related category/categories
  - appointment date and time
  - optional note
- Time is divided into 15-minute slots by default
- Salon operates with 3 staff members by default
- In the same time window, the system can accept at most 3 parallel bookings
- Availability must be calculated based on the total duration of the whole selected service group, not per single service
- All booking logic uses Germany timezone

Admin can configure:

- number of staff available simultaneously
- booking slot length
- working hours per weekday

## Email Notifications

After a successful booking:

- send notification email to admin
- send confirmation email to customer

Admin can configure email templates.

## Dashboard and Reporting

Admin dashboard should provide:

- booking status overview
- today appointments
- weekly / monthly / yearly summaries
- booking statistics by service
- top booked services

## Promotions

The system includes a promotions module.

Admin can configure:

- applicable services
- promotion start and end time
- discounted price or discount percentage

Frontend behavior:

- during promotion period, show original price with muted strikethrough
- show promotional price clearly
- after promotion ends, automatically revert to normal price

## Homepage

Homepage should highlight:

- top booked services
- featured services
- hero/banner content for nails and lashes
- a friendly, elegant design targeting female customers
- salon contact details, map, address, and social links

## SEO Requirements

The website should be structured for strong Google SEO:

- clean and readable URLs
- complete metadata
- crawlable and indexable content
- fast page loading
- search-friendly page structure

## Suggested Database Scope

Database design should support at minimum:

- services
- service_images
- bookings
- booking_items
- promotions
- working_hours
- email_templates
- dashboard_statistics
- site_settings

## Short Prompt Add-on

Add booking logic so each customer can choose multiple services in one appointment. The booking UI must display the total service duration and should also display the total cost. The system must validate capacity based on the total duration of the selected service bundle and the maximum number of parallel customers allowed by the configured staff count. The public website must also show salon information, embedded map/location, and links to Instagram/Facebook. This website is a rewrite of `https://lknailslashes.de`.

## Initial Services Seed Data

```json
[
  {
    "name": "Ablösen Wimpernverlängerung",
    "category": "Wimpern",
    "subcategory": "Sonstiges",
    "price": 10.0,
    "duration_minutes": 30,
    "is_active": true
  },
  {
    "name": "Augenbrauen zupfen & färben",
    "category": "Wimpern",
    "subcategory": "Sonstiges",
    "price": 17.0,
    "duration_minutes": 20,
    "is_active": true
  },
  {
    "name": "Wimpern färben",
    "category": "Wimpern",
    "subcategory": "Sonstiges",
    "price": 8.0,
    "duration_minutes": 15,
    "is_active": true
  },
  {
    "name": "Wimpernlifting",
    "category": "Wimpern",
    "subcategory": "Sonstiges",
    "price": 35.0,
    "duration_minutes": 45,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 4 Wochen",
    "category": "Wimpern",
    "subcategory": "Mega Volume ab 6D",
    "price": 50.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 3 Wochen",
    "category": "Wimpern",
    "subcategory": "Mega Volume ab 6D",
    "price": 45.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 2 Wochen",
    "category": "Wimpern",
    "subcategory": "Mega Volume ab 6D",
    "price": 40.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Neuset",
    "category": "Wimpern",
    "subcategory": "Mega Volume ab 6D",
    "price": 99.0,
    "duration_minutes": 120,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 4 Wochen",
    "category": "Wimpern",
    "subcategory": "Volume 4D-5D",
    "price": 45.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 3 Wochen",
    "category": "Wimpern",
    "subcategory": "Volume 4D-5D",
    "price": 40.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 2 Wochen",
    "category": "Wimpern",
    "subcategory": "Volume 4D-5D",
    "price": 35.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Neuset",
    "category": "Wimpern",
    "subcategory": "Volume 4D-5D",
    "price": 79.0,
    "duration_minutes": 90,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 4 Wochen",
    "category": "Wimpern",
    "subcategory": "Light Volume 2D-3D",
    "price": 40.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 3 Wochen",
    "category": "Wimpern",
    "subcategory": "Light Volume 2D-3D",
    "price": 35.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Aufüllen nach 2 Wochen",
    "category": "Wimpern",
    "subcategory": "Light Volume 2D-3D",
    "price": 30.0,
    "duration_minutes": 60,
    "is_active": true
  },
  {
    "name": "Neuset",
    "category": "Wimpern",
    "subcategory": "Light Volume 2D-3D",
    "price": 69.0,
    "duration_minutes": 90,
    "is_active": true
  },
  {
    "name": "Neuset",
    "category": "Wimpern",
    "subcategory": "Classic 1:1",
    "price": 55.0,
    "duration_minutes": 60,
    "is_active": true,
    "bookings": 7,
    "images": 1
  },
  {
    "name": "Strass-Stein",
    "category": "Nägel",
    "subcategory": "-",
    "price": 0.5,
    "duration_minutes": 10,
    "is_active": true,
    "bookings": 3,
    "images": 1
  },
  {
    "name": "Überlänge",
    "category": "Nägel",
    "subcategory": "-",
    "price": 3.0,
    "duration_minutes": 10,
    "is_active": true,
    "bookings": 5,
    "images": 1
  },
  {
    "name": "AUFFÜLLEN: Trend mit Farbe Babyboomer / Ombre / French / Glitzer",
    "category": "Nägel",
    "subcategory": "-",
    "price": 40.0,
    "duration_minutes": 60,
    "is_active": true,
    "bookings": 28,
    "images": 1
  },
  {
    "name": "AUFFÜLLEN: Weiß Babyboomer / Ombre / French / Glitzer",
    "category": "Nägel",
    "subcategory": "-",
    "price": 33.0,
    "duration_minutes": 50,
    "is_active": true,
    "bookings": 33,
    "images": 1
  },
  {
    "name": "AUFFÜLLEN: mit Farbe",
    "category": "Nägel",
    "subcategory": "-",
    "price": 30.0,
    "duration_minutes": 45,
    "is_active": true,
    "bookings": 20,
    "images": 1
  },
  {
    "name": "AUFFÜLLEN: Natur",
    "category": "Nägel",
    "subcategory": "-",
    "price": 25.0,
    "duration_minutes": 40,
    "is_active": true,
    "bookings": 3,
    "images": 1
  },
  {
    "name": "NEUMODELLAGE: Zehenmodellage oder Neu",
    "category": "Nägel",
    "subcategory": "-",
    "price": 40.0,
    "duration_minutes": 60,
    "is_active": true,
    "bookings": 2,
    "images": 1
  },
  {
    "name": "NEUMODELLAGE: Trend mit Farbe Babyboomer / Ombre / French / Glitzer",
    "category": "Nägel",
    "subcategory": "-",
    "price": 43.0,
    "duration_minutes": 60,
    "is_active": true,
    "bookings": 19,
    "images": 1
  },
  {
    "name": "NEUMODELLAGE: Weiß / Babyboomer / Ombre / French / Glitzer",
    "category": "Nägel",
    "subcategory": "-",
    "price": 35.0,
    "duration_minutes": 60,
    "is_active": true,
    "bookings": 28,
    "images": 1
  },
  {
    "name": "NEUMODELLAGE: mit Farbe",
    "category": "Nägel",
    "subcategory": "-",
    "price": 33.0,
    "duration_minutes": 50,
    "is_active": true,
    "bookings": 11,
    "images": 1
  },
  {
    "name": "NEUMODELLAGE: Natur",
    "category": "Nägel",
    "subcategory": "-",
    "price": 28.0,
    "duration_minutes": 40,
    "is_active": true,
    "bookings": 6,
    "images": 1
  },
  {
    "name": "Pediküre mit Acryl inkl. Massage",
    "category": "Nägel",
    "subcategory": "-",
    "price": 45.0,
    "duration_minutes": 45,
    "is_active": true,
    "bookings": 0,
    "images": 1
  },
  {
    "name": "Pediküre mit Shellac inkl. Massage",
    "category": "Nägel",
    "subcategory": "-",
    "price": 35.0,
    "duration_minutes": 35,
    "is_active": true,
    "bookings": 13,
    "images": 1
  },
  {
    "name": "Pediküre mit Massage",
    "category": "Nägel",
    "subcategory": "-",
    "price": 25.0,
    "duration_minutes": 25,
    "is_active": true,
    "bookings": 8,
    "images": 1
  },
  {
    "name": "Mit Shellac",
    "category": "Nägel",
    "subcategory": "-",
    "price": 25.0,
    "duration_minutes": 25,
    "is_active": true,
    "bookings": 11,
    "images": 1
  },
  {
    "name": "Maniküre ab",
    "category": "Nägel",
    "subcategory": "-",
    "price": 15.0,
    "duration_minutes": 15,
    "is_active": true,
    "bookings": 12,
    "images": 1
  }
]
```
