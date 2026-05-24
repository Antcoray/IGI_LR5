"""
python manage.py seed_data
Fills DB with demo data including Orders with OrderItems.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from catalog.models import (
    Manufacturer, CarType, Feature, Car,
    Employee, Client, Order, OrderItem,
    Article, FAQ, Review, Vacancy, Promo, CompanyInfo, Contact
)


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Company
        CompanyInfo.objects.get_or_create(
            name='АвтоПремиум',
            defaults={
                'description': 'Официальный автосалон. Более 10 лет на рынке.',
                'address': 'г. Минск, пр-т Независимости, 55',
                'phone': '+375 (29) 123-45-67',
                'email': 'info@autopremium.by',
                'founded_year': 2012,
            }
        )

        # Car types
        types_data = [
            ('Седан', 'Классический четырёхдверный'),
            ('SUV', 'Внедорожник / кроссовер'),
            ('Хэтчбек', 'Компактный пятидверный'),
            ('Купе', 'Двухдверный спортивный'),
            ('Минивэн', 'Семейный'),
            ('Универсал', 'С увеличенным багажником'),
        ]
        car_types = {}
        for name, desc in types_data:
            ct, _ = CarType.objects.get_or_create(name=name, defaults={'description': desc})
            car_types[name] = ct

        # Manufacturers
        mfr_data = [
            ('Toyota', 'Япония'), ('BMW', 'Германия'),
            ('Mercedes-Benz', 'Германия'), ('Volkswagen', 'Германия'),
            ('Hyundai', 'Южная Корея'), ('Kia', 'Южная Корея'),
            ('Audi', 'Германия'), ('Ford', 'США'),
        ]
        manufacturers = {}
        for name, country in mfr_data:
            m, _ = Manufacturer.objects.get_or_create(name=name, defaults={'country': country})
            manufacturers[name] = m

        # Features
        feature_names = [
            'Кожаный салон', 'Панорамная крыша', 'Подогрев сидений',
            'Климат-контроль', 'Навигация', 'Камера заднего вида',
            'Адаптивный круиз-контроль', 'Парктроник', 'Bluetooth',
            'Apple CarPlay / Android Auto',
        ]
        features = {fn: Feature.objects.get_or_create(name=fn)[0] for fn in feature_names}

        # Cars (12 штук)
        cars_data = [
            ('Toyota','Camry','Седан',2022,Decimal('89000'),0,'Белый','AT','petrol',Decimal('2.5'),181,'SEED1000000000001','available'),
            ('BMW','5 Series','Седан',2023,Decimal('145000'),0,'Чёрный','AT','petrol',Decimal('2.0'),245,'SEED1000000000002','available'),
            ('Mercedes-Benz','GLE 300d','SUV',2022,Decimal('185000'),12000,'Серебристый','AT','diesel',Decimal('2.0'),245,'SEED1000000000003','available'),
            ('Volkswagen','Tiguan','SUV',2023,Decimal('95000'),0,'Синий','AT','petrol',Decimal('1.4'),150,'SEED1000000000004','available'),
            ('Hyundai','Tucson','SUV',2022,Decimal('78000'),25000,'Красный','AT','petrol',Decimal('2.0'),150,'SEED1000000000005','available'),
            ('Kia','Sportage','SUV',2023,Decimal('82000'),0,'Белый','DCT','petrol',Decimal('1.6'),180,'SEED1000000000006','available'),
            ('Audi','A6','Седан',2022,Decimal('135000'),18000,'Серый','AT','diesel',Decimal('2.0'),204,'SEED1000000000007','available'),
            ('Ford','Explorer','SUV',2021,Decimal('110000'),35000,'Чёрный','AT','petrol',Decimal('3.0'),365,'SEED1000000000008','available'),
            ('Toyota','RAV4','SUV',2023,Decimal('98000'),0,'Зелёный','AT','hybrid',Decimal('2.5'),222,'SEED1000000000009','available'),
            ('BMW','X5','SUV',2022,Decimal('195000'),8000,'Белый','AT','diesel',Decimal('3.0'),286,'SEED1000000000010','available'),
            ('Mercedes-Benz','C 200','Седан',2021,Decimal('105000'),45000,'Синий','AT','petrol',Decimal('1.5'),204,'SEED1000000000011','sold'),
            ('Volkswagen','Golf','Хэтчбек',2022,Decimal('58000'),15000,'Белый','MT','petrol',Decimal('1.2'),105,'SEED1000000000012','available'),
        ]
        car_objects = []
        for (mfr_name,model,type_name,year,price,mileage,color,trans,fuel,eng,hp,vin,status) in cars_data:
            car, created = Car.objects.get_or_create(
                vin=vin,
                defaults=dict(
                    name=model, manufacturer=manufacturers[mfr_name],
                    car_type=car_types[type_name], year=year, price=price,
                    mileage=mileage, color=color, transmission=trans,
                    fuel=fuel, engine_volume=eng, horsepower=hp, status=status,
                    description=f'{mfr_name} {model} {year} — отличное состояние.',
                )
            )
            if created:
                car.features.set(random.sample(list(features.values()), k=random.randint(3,6)))
            car_objects.append(car)

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@autopremium.by', 'admin123')
            self.stdout.write('  Created superuser: admin / admin123')

        # Employee
        if not User.objects.filter(username='manager1').exists():
            emp_user = User.objects.create_user(
                'manager1', 'manager@autopremium.by', 'manager123',
                first_name='Иван', last_name='Петров'
            )
            employee = Employee.objects.create(
                user=emp_user, role='manager',
                phone='+375 (29) 987-65-43',
                birth_date=date(1990, 5, 15),
            )
            self.stdout.write('  Created employee: manager1 / manager123')
        else:
            emp_user = User.objects.get(username='manager1')
            employee = getattr(emp_user, 'employee_profile', None)

        # Clients (анкетные данные)
        clients_raw = [
            ('client1','Иванов','Алексей','Сергеевич','+375 (29) 111-22-33','client1@mail.ru','ул. Ленина, 10','Минск',date(1985,3,20),'HB','1234567'),
            ('client2','Сидорова','Мария','Игоревна','+375 (33) 222-33-44','client2@mail.ru','ул. Советская, 5','Гомель',date(1992,7,10),'KH','7654321'),
            ('client3','Козлов','Дмитрий','Александрович','+375 (44) 333-44-55','client3@mail.ru','пр. Победы, 22','Брест',date(1988,11,5),'MP','3456789'),
            ('client4','Новикова','Елена','Васильевна','+375 (29) 444-55-66','client4@mail.ru','ул. Пушкина, 1','Минск',date(1995,4,18),'HB','9876543'),
            ('client5','Попов','Андрей','Николаевич','+375 (33) 555-66-77','client5@mail.ru','ул. Мира, 33','Витебск',date(1982,9,2),'AB','1122334'),
        ]
        client_objects = []
        for (uname,last,first,patr,phone,email,addr,city,bd,ps,pn) in clients_raw:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(uname, email, 'client123',
                                             first_name=first, last_name=last)
            else:
                u = User.objects.get(username=uname)
            c, _ = Client.objects.get_or_create(user=u, defaults=dict(
                last_name=last, first_name=first, patronymic=patr,
                phone=phone, email=email, address=addr, city=city,
                birth_date=bd, passport_series=ps, passport_number=pn,
            ))
            client_objects.append(c)
            self.stdout.write(f'  Client: {uname} / client123')

        # Orders with OrderItems
        if client_objects and employee:
            today = date.today()
            orders_raw = [
                # (client_idx, status, sale_date_offset, delivery_offset, items)
                # items = list of (car_idx, qty)
                (0, 'completed', -60, -50, [(10, 1)]),
                (1, 'completed', -45, -35, [(0, 1)]),
                (2, 'completed', -30, -20, [(6, 1)]),
                (3, 'completed', -20, -10, [(2, 1)]),
                (4, 'completed', -15,  -5, [(1, 1)]),
                (0, 'approved',  -5,  None, [(3, 1)]),
                (1, 'pending',  None, None, [(4, 1), (11, 1)]),
                (2, 'completed', -90, -80, [(7, 1)]),
                (3, 'completed', -80, -70, [(8, 1)]),
                (4, 'completed', -10,  -2, [(9, 1)]),
            ]
            for (ci, status, sale_off, del_off, items_list) in orders_raw:
                client = client_objects[ci]
                sale_date     = (today + timedelta(days=sale_off)) if sale_off is not None else None
                delivery_date = (today + timedelta(days=del_off))  if del_off  is not None else None

                order = Order.objects.create(
                    client=client, employee=employee, status=status,
                    sale_date=sale_date, delivery_date=delivery_date,
                )
                for (car_idx, qty) in items_list:
                    car = car_objects[car_idx]
                    OrderItem.objects.create(
                        order=order, car=car,
                        quantity=qty, unit_price=car.price,
                    )
                order.recalculate_total()

        # Articles
        for title, summary, content in [
            ('Новые поступления: Toyota и BMW',
             'Ждём поставку новых авто уже в ноябре!',
             'Наш автосалон рад сообщить о новых поступлениях. В ноябре ожидается поставка Toyota Camry нового поколения и BMW 5 Series 2024 года.'),
            ('Специальные условия кредитования',
             'Кредит от 0% на выбранные модели.',
             'До конца месяца действует специальное предложение — кредит под 0% годовых на автомобили Toyota и Kia.'),
            ('Расширение сервисного центра',
             'Открываем новый сервисный зал.',
             'Мы рады сообщить об открытии нового сервисного зала. Теперь мы обслуживаем до 20 автомобилей в день без очереди.'),
        ]:
            Article.objects.get_or_create(title=title, defaults={'summary': summary, 'content': content})

        # FAQs
        for q, a in [
            ('Что такое VIN-код?', 'VIN — уникальный 17-значный идентификатор автомобиля.'),
            ('Как оформить заказ?', 'Выберите авто в каталоге, нажмите "Заказать". Менеджер свяжется с вами.'),
            ('Какие документы нужны?', 'Паспорт гражданина РБ и водительское удостоверение.'),
            ('Есть ли тест-драйв?', 'Да, запишитесь по телефону. Тест-драйв бесплатный.'),
            ('Какие методы оплаты?', 'Наличные, карта, перевод, автокредит.'),
        ]:
            FAQ.objects.get_or_create(question=q, defaults={'answer': a})

        # Reviews
        if client_objects:
            for c, car_i, rating, text in [
                (client_objects[0], 0, 5, 'Отличный автосалон! Купил Toyota Camry, очень доволен.'),
                (client_objects[1], 2, 4, 'Хороший выбор, цены адекватные.'),
                (client_objects[2], None, 5, 'Рекомендую! Сервис на высшем уровне.'),
            ]:
                Review.objects.get_or_create(client=c, defaults={
                    'car': car_objects[car_i] if car_i is not None else None,
                    'rating': rating, 'text': text,
                })

        # Vacancies
        for title, desc, sf, st in [
            ('Менеджер по продажам', 'Продажа автомобилей. Опыт от 1 года.', Decimal('1500'), Decimal('3000')),
            ('Автомеханик', 'Диагностика и ремонт.', Decimal('1200'), Decimal('2500')),
            ('Специалист по кредитованию', 'Оформление автокредитов.', Decimal('1300'), Decimal('2000')),
        ]:
            Vacancy.objects.get_or_create(title=title, defaults={
                'description': desc, 'salary_from': sf, 'salary_to': st
            })

        # Promos
        today_ = date.today()
        for code, pct, desc, valid, status in [
            ('AUTUMN2024', 10, 'Осенняя скидка на все SUV', today_ + timedelta(days=30), 'active'),
            ('NEW2024',     5, 'Скидка на новые поступления', today_ + timedelta(days=60), 'active'),
            ('SUMMER2024',  7, 'Летняя акция (завершена)', today_ - timedelta(days=10), 'archived'),
        ]:
            Promo.objects.get_or_create(code=code, defaults={
                'discount_percent': pct, 'description': desc,
                'valid_until': valid, 'status': status,
            })

        # Contacts
        for name, pos, phone, email, desc in [
            ('Александр Новиков','Директор','+375 (29) 100-00-01','director@autopremium.by','Общее руководство'),
            ('Елена Кравцова','Менеджер по продажам','+375 (29) 100-00-02','sales@autopremium.by','Консультации по выбору'),
            ('Игорь Семёнов','Специалист по кредитованию','+375 (29) 100-00-03','credit@autopremium.by','Автокредиты'),
        ]:
            Contact.objects.get_or_create(name=name, defaults={
                'position': pos, 'phone': phone, 'email': email, 'description': desc,
            })

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('Logins:  admin/admin123  manager1/manager123  client1-5/client123')
