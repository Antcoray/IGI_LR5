# """
# Management command: python manage.py seed_data
# Fills the database with demo data (10+ records in each category)
# """
# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import date, timedelta
# from decimal import Decimal
# import random

# from catalog.models import (
#     Manufacturer, CarType, Feature, Car,
#     Employee, Client, Order,
#     Article, FAQ, Review, Vacancy, Promo, CompanyInfo, Contact
# )


# class Command(BaseCommand):
#     help = 'Seed database with demo data (10+ records in each category)'

#     def handle(self, *args, **options):
#         self.stdout.write('Seeding database with 10+ records per category...')

#         # ===========================================
#         # 1. COMPANY INFO (1 запись)
#         # ===========================================
#         company, _ = CompanyInfo.objects.get_or_create(
#             name='АвтоПремиум',
#             defaults={
#                 'description': 'Официальный автосалон. Более 10 лет на рынке. Широкий выбор новых и проверенных автомобилей.',
#                 'address': 'г. Минск, пр-т Независимости, 55',
#                 'phone': '+375 (29) 123-45-67',
#                 'email': 'info@autopremium.by',
#                 'founded_year': 2012,
#             }
#         )
#         self.stdout.write('✓ Company info created')

#         # ===========================================
#         # 2. CAR TYPES (10 записей)
#         # ===========================================
#         types_data = [
#             ('Седан', 'Классический четырёхдверный кузов'),
#             ('SUV', 'Внедорожник / кроссовер'),
#             ('Хэтчбек', 'Компактный кузов с пятой дверью'),
#             ('Купе', 'Двухдверный спортивный кузов'),
#             ('Минивэн', 'Вместительный семейный автомобиль'),
#             ('Универсал', 'Кузов с увеличенным багажником'),
#             ('Пикап', 'Грузопассажирский кузов'),
#             ('Кабриолет', 'Открытый кузов с мягкой крышей'),
#             ('Лимузин', 'Удлинённый представительский класс'),
#             ('Фургон', 'Грузовой цельнометаллический кузов'),
#         ]
#         car_types = {}
#         for name, desc in types_data:
#             ct, _ = CarType.objects.get_or_create(name=name, defaults={'description': desc})
#             car_types[name] = ct
#         self.stdout.write(f'✓ Created {len(car_types)} car types')

#         # ===========================================
#         # 3. MANUFACTURERS (10+ записей, включая Lexus)
#         # ===========================================
#         mfr_data = [
#             ('Toyota', 'Япония'),
#             ('BMW', 'Германия'),
#             ('Mercedes-Benz', 'Германия'),
#             ('Volkswagen', 'Германия'),
#             ('Hyundai', 'Южная Корея'),
#             ('Kia', 'Южная Корея'),
#             ('Audi', 'Германия'),
#             ('Ford', 'США'),
#             ('Nissan', 'Япония'),
#             ('Honda', 'Япония'),
#             ('Lexus', 'Япония'),  # ← ДОБАВЛЯЕМ LEXUS
#             ('Volvo', 'Швеция'),   # ← ДОБАВЛЯЕМ VOLVO для запаса
#         ]
#         manufacturers = {}
#         for name, country in mfr_data:
#             m, _ = Manufacturer.objects.get_or_create(name=name, defaults={'country': country})
#             manufacturers[name] = m
#         self.stdout.write(f'✓ Created {len(manufacturers)} manufacturers')

#         # ===========================================
#         # 4. FEATURES (15 записей)
#         # ===========================================
#         feature_names = [
#             'Кожаный салон', 'Панорамная крыша', 'Подогрев сидений',
#             'Климат-контроль', 'Навигация', 'Камера заднего вида',
#             'Адаптивный круиз-контроль', 'Парктроник', 'Bluetooth',
#             'Apple CarPlay / Android Auto', 'Бесключевой доступ',
#             'Электрорегулировка сидений', 'Вентиляция сидений',
#             'Премиум аудиосистема', 'Матричные фары',
#         ]
#         features = {}
#         for fn in feature_names:
#             f, _ = Feature.objects.get_or_create(name=fn)
#             features[fn] = f
#         self.stdout.write(f'✓ Created {len(features)} features')

#         # ===========================================
#         # 5. CARS (25 записей, большинство в наличии)
#         # ===========================================
#         cars_data = [
#             # Toyota (3 шт.)
#             ('Toyota', 'Camry', 'Седан', 2022, Decimal('89000'), 0, 'Белый', 'AT', 'petrol', Decimal('2.5'), 181, '1HGBH41JXMN109186', 'available'),
#             ('Toyota', 'RAV4', 'SUV', 2023, Decimal('98000'), 0, 'Зелёный', 'AT', 'hybrid', Decimal('2.5'), 222, '2T3Y1RFV5LC012345', 'available'),
#             ('Toyota', 'Corolla', 'Седан', 2023, Decimal('65000'), 0, 'Серебристый', 'CVT', 'petrol', Decimal('1.8'), 140, 'JTDBR4EE6PJ000001', 'available'),
            
#             # BMW (3 шт.)
#             ('BMW', '5 Series', 'Седан', 2023, Decimal('145000'), 0, 'Чёрный', 'AT', 'petrol', Decimal('2.0'), 245, 'WBAFR9C50BC741952', 'available'),
#             ('BMW', 'X5', 'SUV', 2022, Decimal('195000'), 8000, 'Белый', 'AT', 'diesel', Decimal('3.0'), 286, 'WBAFR9C50BC741000', 'available'),
#             ('BMW', '3 Series', 'Седан', 2023, Decimal('125000'), 0, 'Синий', 'AT', 'petrol', Decimal('2.0'), 184, 'WBA8E9C50BC741001', 'available'),
            
#             # Mercedes-Benz (3 шт.)
#             ('Mercedes-Benz', 'GLE 300d', 'SUV', 2022, Decimal('185000'), 12000, 'Серебристый', 'AT', 'diesel', Decimal('2.0'), 245, 'WDC1660091A123456', 'available'),
#             ('Mercedes-Benz', 'C 200', 'Седан', 2023, Decimal('115000'), 0, 'Чёрный', 'AT', 'petrol', Decimal('1.5'), 204, 'WDC1660091B654322', 'available'),
#             ('Mercedes-Benz', 'E-Class', 'Седан', 2023, Decimal('165000'), 0, 'Белый', 'AT', 'petrol', Decimal('2.0'), 258, 'WDC1660091C654323', 'available'),
            
#             # Volkswagen (3 шт.)
#             ('Volkswagen', 'Tiguan', 'SUV', 2023, Decimal('95000'), 0, 'Синий', 'AT', 'petrol', Decimal('1.4'), 150, 'WVGZZZ5NZJW100001', 'available'),
#             ('Volkswagen', 'Passat', 'Седан', 2023, Decimal('85000'), 0, 'Серый', 'DSG', 'petrol', Decimal('2.0'), 190, 'WVWZZZ3CZJE000001', 'available'),
#             ('Volkswagen', 'Golf', 'Хэтчбек', 2023, Decimal('68000'), 0, 'Красный', 'DSG', 'petrol', Decimal('1.4'), 150, 'WVWZZZAUZEW123457', 'available'),
            
#             # Hyundai (2 шт.)
#             ('Hyundai', 'Tucson', 'SUV', 2022, Decimal('78000'), 25000, 'Красный', 'AT', 'petrol', Decimal('2.0'), 150, 'KMHD841ABNU123456', 'available'),
#             ('Hyundai', 'Santa Fe', 'SUV', 2023, Decimal('105000'), 0, 'Белый', 'AT', 'diesel', Decimal('2.2'), 202, 'KMHS841ABNU123457', 'available'),
            
#             # Kia (2 шт.)
#             ('Kia', 'Sportage', 'SUV', 2023, Decimal('82000'), 0, 'Белый', 'DCT', 'petrol', Decimal('1.6'), 180, 'KNADM81EXG7123456', 'available'),
#             ('Kia', 'Sorento', 'SUV', 2023, Decimal('112000'), 0, 'Тёмно-синий', 'AT', 'diesel', Decimal('2.2'), 202, 'KNADM81EXG7123457', 'available'),
            
#             # Audi (3 шт.)
#             ('Audi', 'A6', 'Седан', 2022, Decimal('135000'), 18000, 'Серый', 'AT', 'diesel', Decimal('2.0'), 204, 'WAUZZZ4G5DN123456', 'available'),
#             ('Audi', 'Q5', 'SUV', 2023, Decimal('125000'), 0, 'Зелёный', 'AT', 'petrol', Decimal('2.0'), 245, 'WAUZZZ4G5DN123457', 'available'),
#             ('Audi', 'Q7', 'SUV', 2023, Decimal('175000'), 0, 'Чёрный', 'AT', 'diesel', Decimal('3.0'), 286, 'WAUZZZ4G5DN123458', 'available'),
            
#             # Ford (2 шт.)
#             ('Ford', 'Explorer', 'SUV', 2021, Decimal('110000'), 35000, 'Чёрный', 'AT', 'petrol', Decimal('3.0'), 365, '1FM5K8GC5LGA12345', 'available'),
#             ('Ford', 'Kuga', 'SUV', 2023, Decimal('88000'), 0, 'Синий', 'AT', 'petrol', Decimal('1.5'), 150, '1FM5K8GC5LGA12346', 'available'),
            
#             # Nissan (2 шт.)
#             ('Nissan', 'X-Trail', 'SUV', 2023, Decimal('88000'), 0, 'Серый', 'CVT', 'petrol', Decimal('2.0'), 163, 'JN1TBNT32U0000001', 'available'),
#             ('Nissan', 'Qashqai', 'SUV', 2023, Decimal('75000'), 0, 'Красный', 'CVT', 'petrol', Decimal('1.3'), 158, 'JN1TBNT32U0000002', 'available'),
            
#             # Honda (2 шт.)
#             ('Honda', 'CR-V', 'SUV', 2023, Decimal('92000'), 0, 'Синий', 'CVT', 'hybrid', Decimal('2.0'), 184, '2HKRW2H53PH000001', 'available'),
#             ('Honda', 'Civic', 'Седан', 2023, Decimal('72000'), 0, 'Белый', 'CVT', 'petrol', Decimal('1.5'), 182, '2HKRW2H53PH000002', 'available'),
            
#             # Lexus (1 шт.)
#             ('Lexus', 'RX', 'SUV', 2023, Decimal('210000'), 0, 'Белый', 'AT', 'hybrid', Decimal('3.5'), 308, 'JTJBC0BA3P2000001', 'available'),
            
#             # ПРОДАННЫЕ/ЗАРЕЗЕРВИРОВАННЫЕ (оставляем несколько для статистики)
#             ('Mercedes-Benz', 'C 200', 'Седан', 2021, Decimal('105000'), 45000, 'Синий', 'AT', 'petrol', Decimal('1.5'), 204, 'WDC1660091B654321', 'sold'),
#             ('Volkswagen', 'Golf', 'Хэтчбек', 2022, Decimal('58000'), 15000, 'Белый', 'MT', 'petrol', Decimal('1.2'), 105, 'WVWZZZAUZEW123456', 'reserved'),
#             ('BMW', 'X5', 'SUV', 2021, Decimal('175000'), 30000, 'Чёрный', 'AT', 'diesel', Decimal('3.0'), 286, 'WBAFR9C50BC741999', 'sold'),
#         ]
        
#         car_objects = []
#         for (mfr_name, model, type_name, year, price, mileage,
#              color, transmission, fuel, engine, hp, vin, status) in cars_data:
#             car, created = Car.objects.get_or_create(
#                 vin=vin,
#                 defaults={
#                     'name': model,
#                     'manufacturer': manufacturers[mfr_name],
#                     'car_type': car_types[type_name],
#                     'year': year,
#                     'price': price,
#                     'mileage': mileage,
#                     'color': color,
#                     'transmission': transmission,
#                     'fuel': fuel,
#                     'engine_volume': engine,
#                     'horsepower': hp,
#                     'status': status,
#                     'description': f'{mfr_name} {model} {year} года — отличное состояние, полная комплектация.',
#                 }
#             )
#             if created:
#                 random_features = random.sample(list(features.values()), k=random.randint(3, 6))
#                 car.features.set(random_features)
#             car_objects.append(car)
#         self.stdout.write(f'✓ Created {len(car_objects)} cars')

#         # ===========================================
#         # 6. SUPERUSER (только один)
#         # ===========================================
#         if not User.objects.filter(username='admin').exists():
#             User.objects.create_superuser('admin', 'admin@autopremium.by', 'admin123')
#             self.stdout.write('✓ Created superuser: admin / admin123')
#         else:
#             self.stdout.write('✓ Superuser already exists')

#         # ===========================================
#         # 7. EMPLOYEES (10 МЕНЕДЖЕРОВ)
#         # ===========================================
#         employees = []
#         employees_data = [
#             ('manager1', 'Иван', 'Петров', '+375 (29) 100-00-01', date(1985, 3, 15), 'manager'),
#             ('manager2', 'Анна', 'Сидорова', '+375 (29) 100-00-02', date(1988, 7, 22), 'manager'),
#             ('manager3', 'Сергей', 'Козлов', '+375 (29) 100-00-03', date(1990, 11, 5), 'manager'),
#             ('manager4', 'Елена', 'Новикова', '+375 (29) 100-00-04', date(1992, 1, 18), 'manager'),
#             ('manager5', 'Дмитрий', 'Морозов', '+375 (29) 100-00-05', date(1987, 5, 30), 'manager'),
#             ('manager6', 'Татьяна', 'Волкова', '+375 (29) 100-00-06', date(1991, 9, 12), 'manager'),
#             ('manager7', 'Алексей', 'Соколов', '+375 (29) 100-00-07', date(1986, 4, 25), 'director'),
#             ('manager8', 'Ольга', 'Лебедева', '+375 (29) 100-00-08', date(1993, 8, 8), 'manager'),
#             ('manager9', 'Павел', 'Зайцев', '+375 (29) 100-00-09', date(1989, 12, 3), 'manager'),
#             ('manager10', 'Мария', 'Кузнецова', '+375 (29) 100-00-10', date(1994, 6, 20), 'manager'),
#         ]
        
#         for username, first_name, last_name, phone, birth_date, role in employees_data:
#             if not User.objects.filter(username=username).exists():
#                 user = User.objects.create_user(
#                     username=username,
#                     email=f'{username}@autopremium.by',
#                     password='manager123',
#                     first_name=first_name,
#                     last_name=last_name
#                 )
#                 employee = Employee.objects.create(
#                     user=user,
#                     role=role,
#                     phone=phone,
#                     birth_date=birth_date,
#                     hired_at=date.today() - timedelta(days=random.randint(30, 1000))
#                 )
#                 employees.append(employee)
#                 self.stdout.write(f'  Created employee: {username} ({first_name} {last_name})')
#             else:
#                 user = User.objects.get(username=username)
#                 if hasattr(user, 'employee_profile'):
#                     employees.append(user.employee_profile)
        
#         self.stdout.write(f'✓ Total employees: {len(employees)}')

#         # ===========================================
#         # 8. CLIENTS (15 клиентов)
#         # ===========================================
#         clients = []
#         clients_data = [
#             ('client1', 'Алексей', 'Иванов', '+375 (29) 111-22-33', 'Минск', date(1985, 3, 20)),
#             ('client2', 'Мария', 'Сидорова', '+375 (33) 222-33-44', 'Гомель', date(1992, 7, 10)),
#             ('client3', 'Дмитрий', 'Козлов', '+375 (44) 333-44-55', 'Брест', date(1988, 11, 5)),
#             ('client4', 'Елена', 'Петрова', '+375 (29) 444-55-66', 'Витебск', date(1995, 2, 15)),
#             ('client5', 'Сергей', 'Михайлов', '+375 (33) 555-66-77', 'Гродно', date(1990, 8, 25)),
#             ('client6', 'Ольга', 'Новикова', '+375 (44) 666-77-88', 'Могилёв', date(1987, 12, 10)),
#             ('client7', 'Павел', 'Фёдоров', '+375 (29) 777-88-99', 'Минск', date(1993, 5, 30)),
#             ('client8', 'Татьяна', 'Морозова', '+375 (33) 888-99-00', 'Брест', date(1991, 9, 18)),
#             ('client9', 'Андрей', 'Волков', '+375 (44) 999-00-11', 'Гомель', date(1984, 1, 22)),
#             ('client10', 'Наталья', 'Зайцева', '+375 (29) 000-11-22', 'Минск', date(1994, 4, 7)),
#             ('client11', 'Владимир', 'Соколов', '+375 (33) 111-22-33', 'Витебск', date(1989, 6, 14)),
#             ('client12', 'Ирина', 'Лебедева', '+375 (44) 222-33-44', 'Гродно', date(1996, 10, 3)),
#             ('client13', 'Георгий', 'Андреев', '+375 (29) 333-44-55', 'Минск', date(1983, 1, 25)),
#             ('client14', 'София', 'Егорова', '+375 (33) 444-55-66', 'Гомель', date(1991, 7, 19)),
#             ('client15', 'Артём', 'Николаев', '+375 (44) 555-66-77', 'Брест', date(1998, 3, 12)),
#         ]
        
#         for username, first, last, phone, city, bd in clients_data:
#             if not User.objects.filter(username=username).exists():
#                 u = User.objects.create_user(username, f'{username}@mail.ru', 'client123',
#                                              first_name=first, last_name=last)
#                 c = Client.objects.create(user=u, phone=phone, city=city, birth_date=bd,
#                                           email=f'{username}@mail.ru', address=f'{city}, ул. Ленина, {random.randint(1, 100)}')
#                 clients.append(c)
#                 self.stdout.write(f'  Created client: {username}')
#             else:
#                 u = User.objects.get(username=username)
#                 c, _ = Client.objects.get_or_create(user=u, defaults={
#                     'phone': phone, 'city': city, 'birth_date': bd, 'email': f'{username}@mail.ru'
#                 })
#                 clients.append(c)
#         self.stdout.write(f'✓ Total clients: {len(clients)}')

#         # ===========================================
#         # 9. ORDERS (минимум 10 COMPLETED заказов + дополнительные)
#         # ===========================================
#         if clients and car_objects and employees:
#             orders_created = 0
#             completed_orders = 0
            
#             # Создаём минимум 10 завершённых заказов (completed)
#             self.stdout.write('\n  Creating completed orders...')
#             for i in range(10):  # Гарантированно 10 completed заказов
#                 car = car_objects[i % len(car_objects)]
#                 client = clients[i % len(clients)]
#                 employee = employees[i % len(employees)]
#                 sale_date = date.today() - timedelta(days=random.randint(1, 180))
                
#                 order, created = Order.objects.get_or_create(
#                     car=car,
#                     client=client,
#                     sale_date=sale_date,  # Добавляем для уникальности
#                     defaults={
#                         'employee': employee,
#                         'status': 'completed',
#                         'sale_price': car.price * Decimal(str(random.uniform(0.95, 1.0))),
#                         'delivery_date': sale_date + timedelta(days=random.randint(1, 14)),
#                         'comment': f'Заказ #{i+1} — полностью завершён. Клиент доволен покупкой.',
#                     }
#                 )
#                 if created:
#                     orders_created += 1
#                     completed_orders += 1
#                     # Меняем статус автомобиля на sold
#                     car.status = 'sold'
#                     car.save()
#                     self.stdout.write(f'    Completed order #{order.pk}: {client.user.get_full_name()} → {car.name} (Manager: {employee.user.get_full_name()})')
            
#             # Создаём дополнительные заказы с разными статусами
#             self.stdout.write('\n  Creating additional orders with various statuses...')
#             additional_statuses = ['pending', 'approved', 'cancelled']
#             for i in range(10):  # Ещё 10 заказов разных статусов
#                 car = car_objects[(i + 5) % len(car_objects)]
#                 client = clients[(i + 3) % len(clients)]
#                 employee = employees[i % len(employees)]
#                 status = random.choice(additional_statuses)
                
#                 order, created = Order.objects.get_or_create(
#                     car=car,
#                     client=client,
#                     created_at__date=date.today() - timedelta(days=random.randint(0, 30)),
#                     defaults={
#                         'employee': employee,
#                         'status': status,
#                         'sale_price': car.price * Decimal(str(random.uniform(0.95, 1.0))),
#                         'comment': f'Заказ #{i+11} — статус: {status}',
#                     }
#                 )
#                 if created:
#                     orders_created += 1
#                     if status == 'approved':
#                         car.status = 'reserved'
#                         car.save()
#                     self.stdout.write(f'    {status.capitalize()} order #{order.pk}: {client.user.get_full_name()} → {car.name}')
            
#             self.stdout.write(f'\n✓ Total orders created: {orders_created}')
#             self.stdout.write(f'✓ Completed orders: {completed_orders} (min 10 ✓)')
#         else:
#             self.stdout.write('⚠ Skipping orders - missing data')

#         # ===========================================
#         # 10. ARTICLES (10 записей)
#         # ===========================================
#         articles_data = [
#             ('Новые поступления: Toyota и BMW', 'Ждём поставку новых авто уже в ноябре!',
#              'Наш автосалон рад сообщить о новых поступлениях. В ноябре ожидается поставка Toyota Camry нового поколения и BMW 5 Series 2024 года.'),
#             ('Специальные условия кредитования', 'Кредит от 0% на выбранные модели.',
#              'До конца месяца действует специальное предложение — кредит под 0% годовых на автомобили Toyota и Kia.'),
#             ('Расширение сервисного центра', 'Открываем новый сервисный зал.',
#              'Мы рады сообщить об открытии нового сервисного зала. Теперь мы обслуживаем до 20 автомобилей в день без очереди.'),
#             ('Зимние шины в подарок', 'При покупке автомобиля до декабря',
#              'При покупке любого автомобиля в нашем салоне вы получаете комплект зимних шин в подарок!'),
#             ('Скидка 10% на сервис', 'Для постоянных клиентов',
#              'Всем клиентам, оформившим заказ в нашем салоне, предоставляется скидка 10% на сервисное обслуживание.'),
#             ('Новый автомобиль Audi A8', 'Представительский класс',
#              'В нашем салоне появился новый Audi A8 2024 года. Приходите на тест-драйв!'),
#             ('Клуб владельцев BMW', 'Присоединяйтесь к сообществу',
#              'Мы запускаем клуб владельцев BMW. Участие бесплатно, много преимуществ!'),
#             ('Итоги года: лучший автосалон 2024', 'Награда от читателей',
#              'Мы признаны лучшим автосалоном года по версии журнала "Автомир". Спасибо нашим клиентам!'),
#             ('Программа Trade-in', 'Обменяйте свой автомобиль',
#              'Запущена обновлённая программа trade-in. Оценка автомобиля за 1 час.'),
#             ('Расширение парка электромобилей', 'Новые электромобили',
#              'В нашем салоне появились новые электромобили: Tesla Model 3 и BYD Han.'),
#         ]
#         for title, summary, content in articles_data:
#             Article.objects.get_or_create(title=title, defaults={'summary': summary, 'content': content})
#         self.stdout.write(f'✓ Created {len(articles_data)} articles')

#         # ===========================================
#         # 11. FAQS (10 записей)
#         # ===========================================
#         faqs_data = [
#             ('Что такое VIN-код?', 'VIN — уникальный 17-значный идентификатор автомобиля.'),
#             ('Как оформить заказ на автомобиль?', 'Зарегистрируйтесь, выберите автомобиль и нажмите "Заказать".'),
#             ('Какие документы нужны для покупки?', 'Паспорт гражданина РБ и водительское удостоверение.'),
#             ('Есть ли возможность тест-драйва?', 'Да! Запишитесь по телефону или через форму на сайте.'),
#             ('Какие методы оплаты принимаются?', 'Наличные, карта, банковский перевод, автокредит.'),
#             ('Какова гарантия на автомобили?', 'Гарантия 3 года или 100 000 км пробега.'),
#             ('Можно ли обменять старый автомобиль?', 'Да, у нас есть программа trade-in.'),
#             ('Есть ли доставка по Беларуси?', 'Да, доставляем автомобиль в любой город Беларуси.'),
#             ('Сколько времени занимает оформление?', 'Обычно 1-2 часа.'),
#             ('Нужно ли проходить техосмотр?', 'Для новых автомобилей первые 3 года не требуется.'),
#         ]
#         for q, a in faqs_data:
#             FAQ.objects.get_or_create(question=q, defaults={'answer': a})
#         self.stdout.write(f'✓ Created {len(faqs_data)} FAQs')

#         # ===========================================
#         # 12. REVIEWS (15 отзывов)
#         # ===========================================
#         if clients:
#             reviews_data = [
#                 (clients[0], car_objects[0], 5, 'Отличный автосалон! Купил Toyota Camry, очень доволен.'),
#                 (clients[1], car_objects[2], 4, 'Хороший выбор автомобилей, цены адекватные.'),
#                 (clients[2], None, 5, 'Рекомендую всем! Сервис на высшем уровне.'),
#                 (clients[3], car_objects[4], 5, 'Купил Hyundai Tucson, машина супер!'),
#                 (clients[4], car_objects[6], 4, 'Хороший автосалон. Быстро оформили кредит.'),
#                 (clients[5], None, 5, 'Обслуживание на высоте! Приятные цены.'),
#                 (clients[6], car_objects[8], 5, 'Toyota RAV4 - мечта! Спасибо салону.'),
#                 (clients[7], car_objects[10], 4, 'Немного долго оформляли документы, но в целом хорошо.'),
#                 (clients[8], None, 5, 'Первоклассный сервис! Обязательно вернусь.'),
#                 (clients[9], car_objects[1], 5, 'BMW 5 Series - отличный выбор.'),
#                 (clients[10], car_objects[12], 5, 'Nissan X-Trail - доволен покупкой!'),
#                 (clients[11], None, 4, 'Хороший салон, широкий выбор.'),
#                 (clients[12], car_objects[3], 5, 'Volkswagen Tiguan - отличный автомобиль!'),
#                 (clients[13], car_objects[7], 4, 'Ford Explorer - мощный внедорожник.'),
#                 (clients[14], car_objects[14], 5, 'Lexus RX - роскошь и комфорт!'),
#             ]
#             for client, car, rating, text in reviews_data:
#                 Review.objects.get_or_create(
#                     client=client,
#                     car=car,
#                     defaults={'rating': rating, 'text': text}
#                 )
#             self.stdout.write(f'✓ Created {len(reviews_data)} reviews')

#         # ===========================================
#         # 13. VACANCIES (5 записей)
#         # ===========================================
#         vacancies_data = [
#             ('Менеджер по продажам автомобилей', 'Продажа новых и б/у автомобилей. Опыт в продажах от 1 года.', Decimal('1500'), Decimal('3000')),
#             ('Автомеханик', 'Диагностика и ремонт автомобилей. СТО, допуск к ТО.', Decimal('1200'), Decimal('2500')),
#             ('Специалист по кредитованию', 'Оформление автокредитов. Опыт в банковской сфере приветствуется.', Decimal('1300'), Decimal('2000')),
#             ('Мойщик автомобилей', 'Мойка автомобилей клиентов. Опыт не требуется.', Decimal('800'), Decimal('1200')),
#             ('Бухгалтер', 'Ведение бухгалтерии автосалона. Высшее образование.', Decimal('1800'), Decimal('2500')),
#         ]
#         for title, desc, sal_from, sal_to in vacancies_data:
#             Vacancy.objects.get_or_create(title=title, defaults={
#                 'description': desc, 'salary_from': sal_from, 'salary_to': sal_to
#             })
#         self.stdout.write(f'✓ Created {len(vacancies_data)} vacancies')

#         # ===========================================
#         # 14. PROMOS (5 записей)
#         # ===========================================
#         promos_data = [
#             ('AUTUMN2024', 10, 'Осенняя скидка на все SUV', date.today() + timedelta(days=30), 'active'),
#             ('NEW2024', 5, 'Скидка на новые поступления', date.today() + timedelta(days=60), 'active'),
#             ('WINTER2024', 15, 'Зимняя распродажа', date.today() + timedelta(days=45), 'active'),
#             ('CREDIT2024', 0, 'Кредит 0% на 3 месяца', date.today() + timedelta(days=90), 'active'),
#             ('LOYALTY2024', 7, 'Скидка для постоянных клиентов', date.today() + timedelta(days=365), 'active'),
#         ]
#         for code, pct, desc, valid, status in promos_data:
#             Promo.objects.get_or_create(code=code, defaults={
#                 'discount_percent': pct, 'description': desc,
#                 'valid_until': valid, 'status': status
#             })
#         self.stdout.write(f'✓ Created {len(promos_data)} promos')

#         # ===========================================
#         # 15. CONTACTS (5 записей)
#         # ===========================================
#         contacts_data = [
#             ('Александр Новиков', 'Директор', '+375 (29) 100-00-01', 'director@autopremium.by', 'Общее руководство салоном'),
#             ('Елена Кравцова', 'Менеджер по продажам', '+375 (29) 100-00-02', 'sales@autopremium.by', 'Консультации по выбору автомобиля'),
#             ('Игорь Семёнов', 'Специалист по кредитованию', '+375 (29) 100-00-03', 'credit@autopremium.by', 'Оформление автокредитов и лизинга'),
#             ('Марина Васильева', 'Главный бухгалтер', '+375 (29) 100-00-04', 'accounting@autopremium.by', 'Финансовые вопросы'),
#             ('Денис Кузнецов', 'Руководитель сервиса', '+375 (29) 100-00-05', 'service@autopremium.by', 'Техническое обслуживание'),
#         ]
#         for name, pos, phone, email, desc in contacts_data:
#             Contact.objects.get_or_create(name=name, defaults={
#                 'position': pos, 'phone': phone, 'email': email, 'description': desc
#             })
#         self.stdout.write(f'✓ Created {len(contacts_data)} contacts')

#         # ===========================================
#         # ИТОГОВАЯ СТАТИСТИКА
#         # ===========================================
#         self.stdout.write(self.style.SUCCESS('\n' + '='*60))
#         self.stdout.write(self.style.SUCCESS('DATABASE SEEDING COMPLETED SUCCESSFULLY!'))
#         self.stdout.write(self.style.SUCCESS('='*60))
        
#         completed_count = Order.objects.filter(status='completed').count()
        
#         self.stdout.write('\n📊 FINAL COUNTS:')
#         self.stdout.write(f'  • Cars: {Car.objects.count()} (✓ min 10)')
#         self.stdout.write(f'  • Clients: {Client.objects.count()} (✓ min 10)')
#         self.stdout.write(f'  • Employees (Managers): {Employee.objects.count()} (✓ 10 managers)')
#         self.stdout.write(f'  • Orders (Total): {Order.objects.count()}')
#         self.stdout.write(f'  • Completed Orders: {completed_count} (✓ min 10)')
#         self.stdout.write(f'  • Manufacturers: {Manufacturer.objects.count()}')
#         self.stdout.write(f'  • Car Types: {CarType.objects.count()}')
#         self.stdout.write(f'  • Reviews: {Review.objects.count()}')
#         self.stdout.write(f'  • Articles: {Article.objects.count()}')
#         self.stdout.write(f'  • FAQs: {FAQ.objects.count()}')
#         self.stdout.write(f'  • Vacancies: {Vacancy.objects.count()}')
#         self.stdout.write(f'  • Promos: {Promo.objects.count()}')
#         self.stdout.write(f'  • Contacts: {Contact.objects.count()}')
        
#         self.stdout.write('\n🔐 ACCOUNTS:')
#         self.stdout.write('  SUPERUSER:')
#         self.stdout.write('    • admin / admin123')
#         self.stdout.write('\n  EMPLOYEES (10 менеджеров):')
#         for emp in employees[:10]:
#             self.stdout.write(f'    • {emp.user.username} / manager123 ({emp.user.get_full_name()})')
#         self.stdout.write('\n  CLIENTS (15 клиентов):')
#         for client in clients[:5]:
#             self.stdout.write(f'    • {client.user.username} / client123 ({client.user.get_full_name()})')
#         self.stdout.write('    • ... и ещё 10 клиентов')
        
#         self.stdout.write(self.style.SUCCESS('\n✨ Seeding complete! ✨'))