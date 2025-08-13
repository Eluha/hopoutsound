# 🎙 HopOutSound Bot
Telegram-бот, разработанный по заказу стороннего клиента для поддержки и развития начинающих специалистов в сфере сведения музыки, работы со звуком и продакшена.

Бот помогает пользователям получить полезные материалы, узнать больше о процессе сведения и при желании заказать услуги у профессионала.
## 📌 Возможности
- 🔥 Бесплатный чеклист — мини-гайд для начинающих звукорежиссёров, доступный только подписчикам Telegram-канала.

- 💽 Темплейт для сведения — готовая схема обработки вокала, которую можно приобрести через оплату в Tribute.

- 🎚 Контакты для сотрудничества — возможность связаться с профессионалом и обсудить проект.

Интеграция с Tribute Webhook — автоматическая фиксация пожертвований в базе данных и проверка подписи HMAC.

Автовыдача файлов — бот самостоятельно отправляет материалы после получения доната.

## 🛠 Технологии
- Python 3.12+

- Aiogram 3 — Telegram-бот

- FastAPI — API для связи бота и вебхука

- PostgreSQL — хранение данных о платежах

- aiohttp — асинхронные HTTP-запросы

- Docker + docker-compose — развёртывание и изоляция сервисов

## Let\`s Encrypt получение сертификата
Нам нужно получить доменное имя и настроить его (DNS-сервера и пр.). Свое доменное имя я купил на сайте https://www.reg.ru/. Так как сервер был взят и другого хостинг сервиса, то и DNS-сервера я взял оттуда.
*Установка Certbot*:
```sudo apt install certbot```
Перед использованием команды, убедитесь, что на сервере не запущена служба веб-сервера или любая другая служба, которая использует **80** порт. В противном случае команда не сработает, т. к. утилита использует свой собственный веб-сервер для доступа к регистрационному адресу Let’s Encrypt.

Для этого нужно остановить nginx процессы командой`sudo systemctl stop nginx`. Если не работает и говорит, что порт все еще занят, посмотрите процесс командой  `sudo netstat -tulnp | grep :80.`

Пример вывода:
```tcp   0   0 0.0.0.0:80    0.0.0.0:\*    LISTEN      3612348/nginx: mast 
tcp6  0   0 :::80         :::\*         LISTEN      3612348/nginx: mast```
При необходимости убейте процесс, либо остановите.
Далее нам нужно в фаервол открыть 80/tcp порт (если он у Вас не открыт) командой `sudo ufw allow 80/tcp,` затем получаем сертификат командой `sudo certbot certonly --standalone -d test.domain.ru`
Вывод при успешном создании сертификата:
```Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/ваше_имя_домена/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/ваше_имя_домена/privkey.pem
This certificate expires on 2025-11-04.
These files will be updated when the certificate renews.

NEXT STEPS:
\- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

\- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 \* Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 \* Donating to EFF:                    https://eff.org/donate-le
\- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -```


# Схема проекта
<img width="1286" height="542" alt="image" src="https://github.com/user-attachments/assets/f240d21f-c345-40c4-9057-66955343d979" />



# Что стоит исправить
1) Прописать версии библиотек, чтобы проект не сломался при пересборке
2) Добавить флаг выдачи файла
3) Фиксировать пользователей, которые получили бесплатный файл / платный файл
