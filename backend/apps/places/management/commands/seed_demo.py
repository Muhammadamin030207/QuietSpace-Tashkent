import random

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.places.models import Category, Place, PlacePhoto
from apps.reviews.models import Review

User = get_user_model()

CATEGORIES = [
    {"key": "cafe", "name_uz": "Kafe", "name_ru": "Кафе", "name_en": "Cafe", "icon": "☕"},
    {"key": "library", "name_uz": "Kutubxona", "name_ru": "Библиотека", "name_en": "Library", "icon": "📚"},
    {"key": "coworking", "name_uz": "Kovorking", "name_ru": "Коворкинг", "name_en": "Coworking", "icon": "💼"},
    {"key": "free_zone", "name_uz": "Bepul zona", "name_ru": "Бесплатная зона", "name_en": "Free zone", "icon": "🆓"},
]

DISTRICTS = {
    "Chilonzor": (41.270, 69.195, 41.315, 69.255),
    "Mirzo Ulug'bek": (41.330, 69.245, 41.375, 69.320),
    "Yunusobod": (41.340, 69.270, 41.395, 69.335),
    "Yakkasaroy": (41.285, 69.235, 41.325, 69.295),
}

PLACE_NAMES = {
    "cafe": [
        "Coffee Room Lab", "Silent Bean", "Cozy Corner", "Barista House",
        "Work&Go Coffee", "Green Desk Cafe", "Kofe Kafasi", "Mokka Point",
        "Quiet Cup", "Cafe Noisette", "Aroma House", "Latte Lane",
        "The Study Cafe", "Brew & Focus", "Nook Espresso",
    ],
    "library": [
        "Alisher Navoiy kutubxonasi", "Milliy kutubxona filiali", "Book Haven",
        "Ilm maskani", "Adabiyot uyi", "Knowledge Hub", "Reading Room 41",
        "Kitob Olami", "Biblioteka Plus", "Sukut zali",
    ],
    "coworking": [
        "WorkSpace Chilonzor", "Focus Hub", "Impact Coworking", "Desk Studio",
        "Mind Office", "Craft Space", "Core Work", "Spark Office",
        "White Desks", "Nomad Base",
    ],
    "free_zone": [
        "IT Park Chilonzor", "Yoshlar markazi zali", "Aloqabank lobby",
        "Metro yonidagi bepul zona", "Universitet kovorkingi", "Campus Hub",
        "Open Plaza zone", "Student Space", "Innovatsiya parki", "Kamolot zali",
    ],
}

AMENITIES = ["ac", "toilet", "parking", "pet_friendly", "outdoor_seats", "quiet_room", "lockers", "coffee_machine"]

REVIEW_TEXTS = [
    ("Wifi juda tez, butun kun ishladim. Joy tinch.", 5),
    ("Shovqin biroz bor edi lekin joy qulay.", 4),
    ("Razetka kam, o'zingiz bilan uzatgich olib keling.", 3),
    ("Eng yaxshi ish joyi, har doim bo'sh joy topiladi.", 5),
    ("Narxi o'rtacha, kofe yaxshi. Wi-Fi pastroq.", 3),
    ("Jim va qulay, tavsiya qilaman.", 5),
    ("Kechqurun olomon bo'ladi, ertalab kelgan ma'qul.", 4),
    ("Kutubxona sifatida juda zo'r, jamiyatda tinch.", 4),
    ("Havo o'tkazgich zo'r, yozda ham soviq.", 5),
    ("Shovqinli musiqa bor, ishlash uchun emas.", 2),
    ("Rozetkalar har stolda, super joy.", 5),
    ("Qulay narxlar, doimiy mijoz bo'ldim.", 4),
    ("Markazga yaqin, transport bilan oson.", 4),
    ("Bir martalik tashrif uchun yaxshi, uzoq ishga emas.", 3),
    ("Ajoyib atmosfera, dizayni chiroyli.", 5),
    ("Wi-Fi tez-tez uzilib qoladi.", 2),
    ("Jimjoy, toza hammom bor.", 4),
    ("Stollar kichkina, lekin joy shinam.", 4),
    ("Narx biroz baland, lekin sifatli.", 4),
    ("Har kuni kelaman, tavsiya qilaman!", 5),
]


def random_point(district_bounds):
    lat_min, lng_min, lat_max, lng_max = district_bounds
    lat = random.uniform(lat_min, lat_max)
    lng = random.uniform(lng_min, lng_max)
    return lat, lng


class Command(BaseCommand):
    help = "Seed demo data: categories, 40+ places, reviews"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")
        random.seed(42)

        for cat in CATEGORIES:
            Category.objects.update_or_create(
                key=cat["key"], defaults=cat
            )

        demo_user, _ = User.objects.get_or_create(
            username="demo_user",
            defaults={"first_name": "Demo", "language": "uz"},
        )
        reviewer_users = []
        for i in range(6):
            user, created = User.objects.get_or_create(
                username=f"reviewer_{i}",
                defaults={"first_name": f"Reviewer {i}", "language": random.choice(["uz", "ru", "en"])},
            )
            reviewer_users.append(user)

        wifi_levels = ["none", "slow", "medium", "fast"]
        noise_levels = ["very_quiet", "quiet", "moderate", "noisy"]
        outlets_levels = ["none", "few", "every_table"]
        price_by_cat = {
            "cafe": ["$", "$", "$$", "$$$"],
            "library": ["free", "free", "$"],
            "coworking": ["$$", "$$", "$$$"],
            "free_zone": ["free", "free", "$"],
        }

        places_count = 0
        reviews_count = 0
        for cat in CATEGORIES:
            names = PLACE_NAMES[cat["key"]]
            for i, name in enumerate(names):
                district = random.choice(list(DISTRICTS.keys()))
                lat, lng = random_point(DISTRICTS[district])
                place, created = Place.objects.update_or_create(
                    name=name,
                    defaults={
                        "category": Category.objects.get(key=cat["key"]),
                        "owner": demo_user,
                        "location": Point(lng, lat, srid=4326),
                        "address": f"{district} tumani, {name} ko'chasi {random.randint(1, 90)}",
                        "district": district,
                        "wifi_speed": random.choices(wifi_levels, weights=[1, 2, 5, 6])[0],
                        "noise_level": random.choices(noise_levels, weights=[4, 5, 3, 1])[0],
                        "outlets_level": random.choices(outlets_levels, weights=[2, 4, 5])[0],
                        "price_level": random.choice(price_by_cat[cat["key"]]),
                        "working_hours": {
                            "mon": "08:00-22:00",
                            "tue": "08:00-22:00",
                            "wed": "08:00-22:00",
                            "thu": "08:00-22:00",
                            "fri": "08:00-22:00",
                            "sat": "09:00-23:00",
                            "sun": "09:00-21:00",
                        },
                        "amenities": random.sample(
                            AMENITIES, k=random.randint(2, 5)
                        ),
                        "is_verified": random.random() < 0.7,
                    },
                )
                if created:
                    places_count += 1

                for _ in range(random.randint(2, 5)):
                    text, rating = random.choice(REVIEW_TEXTS)
                    user = random.choice(reviewer_users)
                    if Review.objects.filter(
                        place=place, user=user, text=text
                    ).exists():
                        continue
                    Review.objects.create(
                        place=place,
                        user=user,
                        rating=rating,
                        wifi_rating=random.randint(1, 5),
                        noise_rating=random.randint(1, 5),
                        comfort_rating=random.randint(1, 5),
                        text=text,
                        ai_summary_tag=random.choice(
                            ["shovqinli kechqurun", "tez wifi", "jim joy", "qulay stollar", ""]
                        ),
                    )
                    reviews_count += 1

        for place in Place.objects.all():
            place.update_avg_rating()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {places_count} places created, {reviews_count} reviews. "
                f"Total places: {Place.objects.count()}, reviews: {Review.objects.count()}"
            )
        )
