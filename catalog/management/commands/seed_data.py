# """
# python manage.py seed_data
# Fills DB with demo data including Orders with OrderItems.
# WARNING: This script will DELETE all existing data first!
# """
# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import date, timedelta
# from decimal import Decimal
# import random

# from catalog.models import (
#     Manufacturer, CarType, Feature, Car,
#     Employee, Client, Order, OrderItem,
#     Article, FAQ, Review, Vacancy, Promo, CompanyInfo, Contact
# )


# class Command(BaseCommand):
#     help = 'Seed database with demo data (clears existing data first)'

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.WARNING('⚠️  WARNING: This will DELETE ALL existing data!'))
#         confirm = input('Type "yes" to continue: ')
        
#         if confirm.lower() != 'yes':
#             self.stdout.write(self.style.ERROR('Operation cancelled.'))
#             return
        
#         self.stdout.write(self.style.WARNING('Clearing existing data...'))
        
#         # ─────────────────────────────────────────
#         # Очистка всех данных в правильном порядке
#         # (сначала удаляем зависимые модели)
#         # ─────────────────────────────────────────
        
#         # 1. Модели с ForeignKey на другие (самые зависимые)
#         OrderItem.objects.all().delete()
#         Order.objects.all().delete()
#         Review.objects.all().delete()
#         Client.objects.all().delete()
#         Employee.objects.all().delete()
        
#         # 2. Модели с ForeignKey на Car
#         Car.objects.all().delete()
        
#         # 3. Остальные модели
#         Contact.objects.all().delete()
#         Article.objects.all().delete()
#         FAQ.objects.all().delete()
#         Vacancy.objects.all().delete()
#         Promo.objects.all().delete()
#         CompanyInfo.objects.all().delete()
#         Feature.objects.all().delete()
#         CarType.objects.all().delete()
#         Manufacturer.objects.all().delete()
        
#         # 4. Пользователи (кроме суперпользователей, которых мы создадим заново)
#         # Удаляем всех пользователей, кроме возможных суперпользователей, 
#         # но лучше удалить всех и создать заново
#         User.objects.exclude(is_superuser=True).delete()
#         # Также удалим суперпользователя, чтобы создать его с правильными параметрами
#         User.objects.filter(username='admin').delete()
        
#         self.stdout.write(self.style.SUCCESS('✅ All existing data cleared.\n'))
        
#         self.stdout.write('Seeding database...')

#         # ─────────────────────────────────────────
#         # Company (1 запись)
#         # ─────────────────────────────────────────
#         CompanyInfo.objects.create(
#             name='АвтоПремиум',
#             description='Официальный автосалон. Более 10 лет на рынке.',
#             address='г. Минск, пр-т Независимости, 55',
#             phone='+375 (29) 123-45-67',
#             email='info@autopremium.by',
#             founded_year=2012,
#         )

#         # ─────────────────────────────────────────
#         # Car types (6 видов)
#         # ─────────────────────────────────────────
#         types_data = [
#             ('Седан', 'Классический четырёхдверный'),
#             ('SUV', 'Внедорожник / кроссовер'),
#             ('Хэтчбек', 'Компактный пятидверный'),
#             ('Купе', 'Двухдверный спортивный'),
#             ('Минивэн', 'Семейный'),
#             ('Универсал', 'С увеличенным багажником'),
#         ]
#         car_types = {}
#         for name, desc in types_data:
#             ct = CarType.objects.create(name=name, description=desc)
#             car_types[name] = ct
#         self.stdout.write(f'  Created {CarType.objects.count()} car types')

#         # ─────────────────────────────────────────
#         # Manufacturers (12 производителей)
#         # ─────────────────────────────────────────
#         mfr_data = [
#             ('Toyota', 'Япония'), ('BMW', 'Германия'),
#             ('Mercedes-Benz', 'Германия'), ('Volkswagen', 'Германия'),
#             ('Hyundai', 'Южная Корея'), ('Kia', 'Южная Корея'),
#             ('Audi', 'Германия'), ('Ford', 'США'),
#             ('Honda', 'Япония'), ('Nissan', 'Япония'),
#             ('Lexus', 'Япония'), ('Volvo', 'Швеция'),
#         ]
#         manufacturers = {}
#         for name, country in mfr_data:
#             m = Manufacturer.objects.create(name=name, country=country)
#             manufacturers[name] = m
#         self.stdout.write(f'  Created {Manufacturer.objects.count()} manufacturers')

#         # ─────────────────────────────────────────
#         # Features (14 опций)
#         # ─────────────────────────────────────────
#         feature_names = [
#             'Кожаный салон', 'Панорамная крыша', 'Подогрев сидений',
#             'Климат-контроль', 'Навигация', 'Камера заднего вида',
#             'Адаптивный круиз-контроль', 'Парктроник', 'Bluetooth',
#             'Apple CarPlay / Android Auto', 'Бесключевой доступ',
#             'Аудиосистема премиум', 'Вентиляция сидений', 'Подогрев руля',
#         ]
#         features = {}
#         for fn in feature_names:
#             f = Feature.objects.create(name=fn)
#             features[fn] = f
#         self.stdout.write(f'  Created {Feature.objects.count()} features')

#         # ─────────────────────────────────────────
#         # Cars (15 автомобилей)
#         # ─────────────────────────────────────────
#         cars_data = [
#             ('Toyota','Camry','Седан',2022,Decimal('89000'),0,'Белый','AT','petrol',Decimal('2.5'),181,'SEED1000000000001','available'),
#             ('BMW','5 Series','Седан',2023,Decimal('145000'),0,'Чёрный','AT','petrol',Decimal('2.0'),245,'SEED1000000000002','available'),
#             ('Mercedes-Benz','GLE 300d','SUV',2022,Decimal('185000'),12000,'Серебристый','AT','diesel',Decimal('2.0'),245,'SEED1000000000003','available'),
#             ('Volkswagen','Tiguan','SUV',2023,Decimal('95000'),0,'Синий','AT','petrol',Decimal('1.4'),150,'SEED1000000000004','available'),
#             ('Hyundai','Tucson','SUV',2022,Decimal('78000'),25000,'Красный','AT','petrol',Decimal('2.0'),150,'SEED1000000000005','available'),
#             ('Kia','Sportage','SUV',2023,Decimal('82000'),0,'Белый','DCT','petrol',Decimal('1.6'),180,'SEED1000000000006','available'),
#             ('Audi','A6','Седан',2022,Decimal('135000'),18000,'Серый','AT','diesel',Decimal('2.0'),204,'SEED1000000000007','available'),
#             ('Ford','Explorer','SUV',2021,Decimal('110000'),35000,'Чёрный','AT','petrol',Decimal('3.0'),365,'SEED1000000000008','available'),
#             ('Toyota','RAV4','SUV',2023,Decimal('98000'),0,'Зелёный','AT','hybrid',Decimal('2.5'),222,'SEED1000000000009','available'),
#             ('BMW','X5','SUV',2022,Decimal('195000'),8000,'Белый','AT','diesel',Decimal('3.0'),286,'SEED1000000000010','available'),
#             ('Mercedes-Benz','C 200','Седан',2021,Decimal('105000'),45000,'Синий','AT','petrol',Decimal('1.5'),204,'SEED1000000000011','sold'),
#             ('Volkswagen','Golf','Хэтчбек',2022,Decimal('58000'),15000,'Белый','MT','petrol',Decimal('1.2'),105,'SEED1000000000012','available'),
#             ('Honda','CR-V','SUV',2023,Decimal('88000'),0,'Серебристый','CVT','petrol',Decimal('1.5'),190,'SEED1000000000013','available'),
#             ('Nissan','Qashqai','SUV',2022,Decimal('75000'),12000,'Чёрный','CVT','petrol',Decimal('1.3'),160,'SEED1000000000014','available'),
#             ('Lexus','RX','SUV',2023,Decimal('210000'),0,'Белый','AT','hybrid',Decimal('3.5'),300,'SEED1000000000015','available'),
#         ]
#         car_objects = []
#         for (mfr_name,model,type_name,year,price,mileage,color,trans,fuel,eng,hp,vin,status) in cars_data:
#             car = Car.objects.create(
#                 vin=vin,
#                 name=model,
#                 manufacturer=manufacturers[mfr_name],
#                 car_type=car_types[type_name],
#                 year=year,
#                 price=price,
#                 mileage=mileage,
#                 color=color,
#                 transmission=trans,
#                 fuel=fuel,
#                 engine_volume=eng,
#                 horsepower=hp,
#                 status=status,
#                 description=f'{mfr_name} {model} {year} — отличное состояние.',
#             )
#             # Добавляем случайные опции
#             car.features.set(random.sample(list(features.values()), k=random.randint(3, 6)))
#             car_objects.append(car)
#         self.stdout.write(f'  Created {Car.objects.count()} cars')

#         # ─────────────────────────────────────────
#         # Superuser
#         # ─────────────────────────────────────────
#         admin = User.objects.create_superuser('admin', 'admin@autopremium.by', 'admin123')
#         self.stdout.write('  Created superuser: admin / admin123')

#         # ─────────────────────────────────────────
#         # Employees (3 сотрудника)
#         # ─────────────────────────────────────────
#         employees_data = [
#             ('manager1', 'Иван', 'Петров', 'manager@autopremium.by', 'manager123', 
#              'manager', '+375 (29) 987-65-43', date(1990, 5, 15)),
#             ('manager2', 'Анна', 'Смирнова', 'anna@autopremium.by', 'manager123', 
#              'manager', '+375 (29) 987-65-44', date(1992, 8, 20)),
#             ('manager3', 'Сергей', 'Козлов', 'sergey@autopremium.by', 'manager123', 
#              'manager', '+375 (29) 987-65-45', date(1988, 3, 10)),
#         ]
#         employees = []
#         for username, first_name, last_name, email, password, role, phone, birth_date in employees_data:
#             user = User.objects.create_user(
#                 username, email, password,
#                 first_name=first_name, last_name=last_name
#             )
#             user.is_staff = True
#             user.save()
            
#             emp = Employee.objects.create(
#                 user=user,
#                 role=role,
#                 phone=phone,
#                 birth_date=birth_date,
#             )
#             employees.append(emp)
#             self.stdout.write(f'  Created employee: {username} / {password}')

#         # ─────────────────────────────────────────
#         # Clients (11 клиентов с полными данными)
#         # ─────────────────────────────────────────
#         clients_data = [
#             ('client1', 'Иванов', 'Алексей', 'Сергеевич', '+375 (29) 111-22-33', 
#              'client1@mail.ru', 'ул. Ленина, 10', 'Минск', date(1985, 3, 20), 'HB', '1234567'),
#             ('client2', 'Сидорова', 'Мария', 'Игоревна', '+375 (33) 222-33-44', 
#              'client2@mail.ru', 'ул. Советская, 5', 'Гомель', date(1992, 7, 10), 'KH', '7654321'),
#             ('client3', 'Козлов', 'Дмитрий', 'Александрович', '+375 (44) 333-44-55', 
#              'client3@mail.ru', 'пр. Победы, 22', 'Брест', date(1988, 11, 5), 'MP', '3456789'),
#             ('client4', 'Новикова', 'Елена', 'Васильевна', '+375 (29) 444-55-66', 
#              'client4@mail.ru', 'ул. Пушкина, 1', 'Минск', date(1995, 4, 18), 'HB', '9876543'),
#             ('client5', 'Попов', 'Андрей', 'Николаевич', '+375 (33) 555-66-77', 
#              'client5@mail.ru', 'ул. Мира, 33', 'Витебск', date(1982, 9, 2), 'AB', '1122334'),
#             ('client6', 'Морозова', 'Ольга', 'Владимировна', '+375 (29) 666-77-88', 
#              'client6@mail.ru', 'ул. Горького, 15', 'Могилёв', date(1990, 12, 15), 'HB', '2233445'),
#             ('client7', 'Соколов', 'Павел', 'Андреевич', '+375 (44) 777-88-99', 
#              'client7@mail.ru', 'пр. Франциска Скорины, 8', 'Гродно', date(1987, 6, 25), 'KH', '3344556'),
#             ('client8', 'Лебедева', 'Татьяна', 'Викторовна', '+375 (29) 888-99-00', 
#              'client8@mail.ru', 'ул. Якуба Коласа, 42', 'Брест', date(1993, 2, 8), 'MP', '4455667'),
#             ('client9', 'Павлов', 'Константин', 'Дмитриевич', '+375 (33) 999-00-11', 
#              'client9@mail.ru', 'ул. Кирова, 7', 'Витебск', date(1984, 9, 30), 'AB', '5566778'),
#             ('client10', 'Васильева', 'Ирина', 'Петровна', '+375 (29) 000-11-22', 
#              'client10@mail.ru', 'ул. Московская, 23', 'Минск', date(1991, 11, 12), 'HB', '6677889'),
#             ('client11', 'Николаев', 'Денис', 'Сергеевич', '+375 (44) 111-22-33', 
#              'client11@mail.ru', 'пр. Дзержинского, 56', 'Гомель', date(1989, 4, 5), 'KH', '7788990'),
#         ]
#         client_objects = []
#         for username, last, first, patronymic, phone, email, addr, city, bd, ps, pn in clients_data:
#             user = User.objects.create_user(
#                 username, email, 'cl123456',
#                 first_name=first, last_name=last
#             )
#             client = Client.objects.create(
#                 user=user,
#                 last_name=last,
#                 first_name=first,
#                 patronymic=patronymic,
#                 phone=phone,
#                 email=email,
#                 address=addr,
#                 city=city,
#                 birth_date=bd,
#                 passport_series=ps,
#                 passport_number=pn,
#             )
#             client_objects.append(client)
#             self.stdout.write(f'  Created client: {username} / cl123456')

#         # ─────────────────────────────────────────
#         # Contacts (все сотрудники + дополнительные)
#         # ─────────────────────────────────────────
#         # Сотрудники в контактах
#         for emp in employees:
#             Contact.objects.create(
#                 name=f"{emp.user.first_name} {emp.user.last_name}",
#                 position=emp.get_role_display(),
#                 phone=emp.phone,
#                 email=emp.user.email,
#                 description='Сотрудник отдела продаж',
#             )
        
#         # Дополнительные контакты
#         extra_contacts = [
#             ('Петр Сидоров', 'Главный механик', '+375 (29) 100-00-04', 'mechanic@autopremium.by', 'Техническое обслуживание'),
#             ('Марина Кузнецова', 'PR-менеджер', '+375 (29) 100-00-05', 'pr@autopremium.by', 'Связи с общественностью'),
#             ('Алексей Фёдоров', 'Юрисконсульт', '+375 (29) 100-00-06', 'lawyer@autopremium.by', 'Юридические вопросы'),
#         ]
#         for name, pos, phone, email, desc in extra_contacts:
#             Contact.objects.create(
#                 name=name,
#                 position=pos,
#                 phone=phone,
#                 email=email,
#                 description=desc,
#             )
#         self.stdout.write(f'  Created {Contact.objects.count()} contacts')

#         # ─────────────────────────────────────────
#         # Orders with OrderItems (16 заказов)
#         # ─────────────────────────────────────────
#         today = date.today()
#         orders_raw = [
#             (0, 'completed', -60, -50, [(0, 1)]),
#             (1, 'completed', -45, -35, [(1, 1)]),
#             (2, 'completed', -30, -20, [(2, 1)]),
#             (3, 'completed', -20, -10, [(3, 1)]),
#             (4, 'completed', -15, -5, [(4, 1)]),
#             (5, 'completed', -10, -3, [(5, 1)]),
#             (6, 'completed', -5, 0, [(6, 1)]),
#             (7, 'approved', -3, None, [(7, 1)]),
#             (8, 'pending', None, None, [(8, 1)]),
#             (9, 'completed', -25, -15, [(9, 1)]),
#             (10, 'completed', -8, -2, [(10, 1)]),
#             (0, 'approved', -2, None, [(11, 1)]),
#             (1, 'pending', None, None, [(12, 1)]),
#             (2, 'completed', -12, -7, [(13, 1)]),
#             (3, 'completed', -7, -1, [(14, 1)]),
#             (4, 'completed', -3, None, [(0, 1), (1, 1)]),
#         ]
#         for ci, status, sale_off, del_off, items_list in orders_raw:
#             client = client_objects[ci % len(client_objects)]
#             employee = employees[ci % len(employees)]
#             sale_date = (today + timedelta(days=sale_off)) if sale_off is not None else None
#             delivery_date = (today + timedelta(days=del_off)) if del_off is not None else None

#             order = Order.objects.create(
#                 client=client,
#                 employee=employee,
#                 status=status,
#                 sale_date=sale_date,
#                 delivery_date=delivery_date,
#             )
#             total = 0
#             for car_idx, qty in items_list:
#                 car = car_objects[car_idx % len(car_objects)]
#                 OrderItem.objects.create(
#                     order=order,
#                     car=car,
#                     quantity=qty,
#                     unit_price=car.price,
#                 )
#                 total += car.price * qty
#             order.total_amount = total
#             order.save(update_fields=['total_amount'])
#         self.stdout.write(f'  Created {Order.objects.count()} orders with items')

#         # ─────────────────────────────────────────
#         # Articles (6 новостей)
#         # ─────────────────────────────────────────
#         articles_data = [
#             ('Новые поступления: Toyota и BMW', 'Ждём поставку новых авто уже в ноябре!',
#              'Наш автосалон рад сообщить о новых поступлениях. В ноябре ожидается поставка Toyota Camry нового поколения и BMW 5 Series 2024 года.'),
#             ('Специальные условия кредитования', 'Кредит от 0% на выбранные модели.',
#              'До конца месяца действует специальное предложение — кредит под 0% годовых на автомобили Toyota и Kia.'),
#             ('Расширение сервисного центра', 'Открываем новый сервисный зал.',
#              'Мы рады сообщить об открытии нового сервисного зала. Теперь мы обслуживаем до 20 автомобилей в день без очереди.'),
#             ('Лучший автосалон 2024 года', 'АвтоПремиум признан лучшим автосалоном!',
#              'По итогам голосования наших клиентов, мы признаны лучшим автосалоном Минска. Спасибо за доверие!'),
#             ('Зимние скидки до 20%', 'Специальное предложение на зимнюю резину и обслуживание',
#              'При покупке автомобиля в декабре вы получаете зимнюю резину в подарок и сертификат на бесплатное ТО.'),
#             ('Тест-драйв электромобилей', 'Попробуйте новые электромобили',
#              'В нашем салоне появились новые электромобили. Записывайтесь на тест-драйв уже сегодня!'),
#         ]
#         for title, summary, content in articles_data:
#             Article.objects.create(
#                 title=title,
#                 summary=summary,
#                 content=content,
#                 is_published=True,
#             )
#         self.stdout.write(f'  Created {Article.objects.count()} articles')

#         # ─────────────────────────────────────────
#         # FAQs (7 вопросов)
#         # ─────────────────────────────────────────
#         faqs_data = [
#             ('Что такое VIN-код?', 'VIN — уникальный 17-значный идентификатор автомобиля.'),
#             ('Как оформить заказ?', 'Выберите авто в каталоге, нажмите "Заказать". Менеджер свяжется с вами.'),
#             ('Какие документы нужны?', 'Паспорт гражданина РБ и водительское удостоверение.'),
#             ('Есть ли тест-драйв?', 'Да, запишитесь по телефону. Тест-драйв бесплатный.'),
#             ('Какие методы оплаты?', 'Наличные, карта, перевод, автокредит.'),
#             ('Можно ли вернуть автомобиль?', 'Да, в течение 14 дней при условии сохранения товарного вида.'),
#             ('Есть ли гарантия?', 'На все новые автомобили гарантия 3 года или 100 000 км пробега.'),
#         ]
#         for q, a in faqs_data:
#             FAQ.objects.create(question=q, answer=a)
#         self.stdout.write(f'  Created {FAQ.objects.count()} FAQs')

#         # ─────────────────────────────────────────
#         # Reviews (11 отзывов)
#         # ─────────────────────────────────────────
#         reviews_data = [
#             (0, 0, 5, 'Отличный автосалон! Купил Toyota Camry, очень доволен.'),
#             (1, 2, 4, 'Хороший выбор, цены адекватные.'),
#             (2, None, 5, 'Рекомендую! Сервис на высшем уровне.'),
#             (3, 1, 5, 'Вежливый персонал, помогли с выбором. Спасибо!'),
#             (4, 3, 4, 'Оформление быстрое, авто в отличном состоянии.'),
#             (5, 5, 5, 'Лучший автосалон в городе!'),
#             (6, None, 4, 'Довольна покупкой, спасибо менеджеру Анне.'),
#             (7, 8, 5, 'BMW X5 - мечта сбылась! Отдельное спасибо за кредит.'),
#             (8, 10, 5, 'Отличное обслуживание, буду рекомендовать друзьям.'),
#             (9, None, 4, 'Хороший выбор автомобилей, но долго ждал оформления.'),
#             (10, 12, 5, 'Всё понравилось! Быстро, качественно, профессионально.'),
#         ]
#         for ci, car_idx, rating, text in reviews_data:
#             client = client_objects[ci % len(client_objects)]
#             car = car_objects[car_idx] if car_idx is not None else None
#             Review.objects.create(
#                 client=client,
#                 car=car,
#                 rating=rating,
#                 text=text,
#             )
#         self.stdout.write(f'  Created {Review.objects.count()} reviews')

#         # ─────────────────────────────────────────
#         # Vacancies (6 вакансий)
#         # ─────────────────────────────────────────
#         vacancies_data = [
#             ('Менеджер по продажам', 'Продажа автомобилей. Опыт от 1 года.', Decimal('1500'), Decimal('3000')),
#             ('Автомеханик', 'Диагностика и ремонт.', Decimal('1200'), Decimal('2500')),
#             ('Специалист по кредитованию', 'Оформление автокредитов.', Decimal('1300'), Decimal('2000')),
#             ('Автослесарь', 'Ремонт и обслуживание автомобилей.', Decimal('1100'), Decimal('2200')),
#             ('Маляр-кузовщик', 'Кузовной ремонт и покраска.', Decimal('1400'), Decimal('2800')),
#             ('Мойщик автомобилей', 'Химчистка и мойка авто.', Decimal('800'), Decimal('1200')),
#         ]
#         for title, desc, sf, st in vacancies_data:
#             Vacancy.objects.create(
#                 title=title,
#                 description=desc,
#                 salary_from=sf,
#                 salary_to=st,
#                 is_active=True,
#             )
#         self.stdout.write(f'  Created {Vacancy.objects.count()} vacancies')

#         # ─────────────────────────────────────────
#         # Promos (6 промокодов)
#         # ─────────────────────────────────────────
#         today_ = date.today()
#         promos_data = [
#             ('AUTUMN2024', 10, 'Осенняя скидка на все SUV', today_ + timedelta(days=30), 'active'),
#             ('NEW2024', 5, 'Скидка на новые поступления', today_ + timedelta(days=60), 'active'),
#             ('WINTER2024', 15, 'Зимняя распродажа', today_ + timedelta(days=45), 'active'),
#             ('SUMMER2024', 7, 'Летняя акция (завершена)', today_ - timedelta(days=10), 'archived'),
#             ('CREDIT2024', 3, 'Скидка при автокредите', today_ + timedelta(days=90), 'active'),
#             ('TESTDRIVE', 5, 'Скидка после тест-драйва', today_ + timedelta(days=20), 'active'),
#         ]
#         for code, pct, desc, valid, status in promos_data:
#             Promo.objects.create(
#                 code=code,
#                 discount_percent=pct,
#                 description=desc,
#                 valid_until=valid,
#                 status=status,
#             )
#         self.stdout.write(f'  Created {Promo.objects.count()} promos')

#         # ─────────────────────────────────────────
#         # Final summary
#         # ─────────────────────────────────────────
#         self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
#         self.stdout.write(self.style.SUCCESS('📊 Final summary:'))
#         self.stdout.write(f'  - Companies:      {CompanyInfo.objects.count()}')
#         self.stdout.write(f'  - Car types:      {CarType.objects.count()}')
#         self.stdout.write(f'  - Manufacturers:  {Manufacturer.objects.count()}')
#         self.stdout.write(f'  - Features:       {Feature.objects.count()}')
#         self.stdout.write(f'  - Cars:           {Car.objects.count()}')
#         self.stdout.write(f'  - Employees:      {Employee.objects.count()}')
#         self.stdout.write(f'  - Clients:        {Client.objects.count()}')
#         self.stdout.write(f'  - Contacts:       {Contact.objects.count()}')
#         self.stdout.write(f'  - Orders:         {Order.objects.count()}')
#         self.stdout.write(f'  - Articles:       {Article.objects.count()}')
#         self.stdout.write(f'  - FAQs:           {FAQ.objects.count()}')
#         self.stdout.write(f'  - Reviews:        {Review.objects.count()}')
#         self.stdout.write(f'  - Vacancies:      {Vacancy.objects.count()}')
#         self.stdout.write(f'  - Promos:         {Promo.objects.count()}')
        
#         self.stdout.write('\n🔐 Logins:')
#         self.stdout.write('  Admin:      admin / admin123')
#         self.stdout.write('  Employees:  manager1, manager2, manager3 / manager123')
#         self.stdout.write('  Clients:    client1-11 / cl123456')