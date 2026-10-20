from django.core.management.base import BaseCommand

from store.models import Product


BOOKS = [
    ("Atomic Habits", "James Clear", "1250.00", "AtomicHabits.jpg"),
    ("Christian Theology", "John Calvin", "2050.00", "ChristianTheology.jpg"),
    ("Communicate with Misery", "Jonathan Schooler", "1000.00", "CommunicateWithMisery.jpg"),
    ("Daily Doctraine", "Kevin Davey", "880.00", "DailyDoctraine.jpg"),
    ("Developing Talent in Young People", "Kevin Davey", "950.00", "DevelopingTalentInYoungPeople.jpg"),
    ("Good to Great", "Jim Collins", "250.00", "GoodToGreat.jpg"),
    ("Hard Business", "Kevin Davey", "500.00", "HardBusiness.jpg"),
    ("How Children Fail", "John Holt", "250.00", "HowChildrenFail.jpg"),
    ("How to Be Calm in a Busy World", "Shawn Achor", "250.00", "HowToBeCalmInABusyWorld.jpg"),
    ("Moonwalking with Einstein", "Jonathan Schooler", "750.00", "MoonwalkingWithEinstein.jpg"),
    ("Naked Forex", "Kevin Davey", "650.00", "NakedForex.jpg"),
    ("Never Split the Difference", "Chris Voss", "900.00", "NeverSplitTheDifference.jpg"),
    ("Rich Dad, Poor Dad", "Robert Kiyosaki", "290.00", "RichDadPoorDad.jpg"),
    ("Start with Why", "Simon Sinek", "200.00", "StartWithWhy.jpg"),
    ("The Compassionate Mind", "Paul Gilbert", "290.00", "TheCompassionateMind.jpg"),
    ("The Four-Hour Workweek", "Tim Ferriss", "250.00", "TheFourHourWorkweek.jpg"),
    ("The Godly Man", "Kevin Davey", "450.00", "TheGodlyMan.jpg"),
    ("The Lean Startup", "Eric Ries", "950.00", "TheLEanStartUp.jpg"),
    ("The New Testament", "Kevin Davey", "550.00", "TheNEwTestament.jpg"),
    ("The One Thing", "Kevin Davey", "250.00", "TheOneThing.jpg"),
    ("The Psychology of Money", "Kevin Davey", "500.00", "ThePsychologyOfMoney.jpg"),
    ("The Story of Humankind", "Kevin Davey", "900.00", "TheSroryOfHumankind.jpg"),
    ("The Upside of Your Dark Side", "Kevin Davey", "350.00", "TheUpsideOfYourDarkside.jpg"),
    ("The Worry Cure", "Kevin Davey", "290.00", "TheWorryCure.jpg"),
    ("Think and Grow Rich", "Kevin Davey", "700.00", "ThinkAndGrowRich.webp"),
    ("Trade Your Way to Financial Way", "Kevin Davey", "700.00", "TradeYourWayToFinancialWay.jpg"),
    ("The Way of the Turtle", "Kevin Davey", "650.00", "WayOfTheTurtle.jpg"),
    ("What is Biblical Theology", "Kevin Davey", "270.00", "WhatIsBiblicalTheology.jpg"),
    ("Women Who Think Too Much", "Kevin Davey", "300.00", "WomenWhoThinkTooMuch.jpg"),
    ("Zero to One", "Kevin Davey", "550.00", "ZeroToOne.jpg"),
]


class Command(BaseCommand):
    help = "Add the existing Page Co. Books catalog to the database."

    def handle(self, *args, **options):
        created_count = 0
        for title, author, price, image in BOOKS:
            _, created = Product.objects.get_or_create(
                title=title,
                defaults={
                    "author": author,
                    "description": f"Discover {title}, written by {author}.",
                    "price": price,
                    "image": image,
                    "stock": 10,
                },
            )
            created_count += int(created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog ready: added {created_count} new books "
                f"({Product.objects.count()} total)."
            )
        )
