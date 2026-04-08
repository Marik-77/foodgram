HTTPS для Foodgram
==================

В контейнер nginx монтируются файлы:
  ssl/fullchain.pem
  ssl/privkey.pem

Вариант A — Let's Encrypt (зелёный замок в браузере)
-----------------------------------------------------
1. Убедитесь, что домен указывает на IP сервера, порт 80 открыт.

2. В .env на сервере укажите (подставьте свой домен):
   CSRF_TRUSTED_ORIGINS=https://ваш-домен.ru,https://www.ваш-домен.ru
   Для одного хоста без www, например DDNS:
   CSRF_TRUSTED_ORIGINS=https://idealfood.ddns.net

3. Первый выпуск сертификата, если nginx уже слушает 80 (webroot):
   Путь -w должен быть каталог infra/certbot/www на сервере (как в compose).
   Пример для одного домена:
   cd /path/to/foodgram/infra
   sudo certbot certonly --webroot -w "$(pwd)/certbot/www" -d idealfood.ddns.net

   Несколько имён:
   sudo certbot certonly --webroot -w /home/USER/foodgram/infra/certbot/www \
     -d ваш-домен.ru -d www.ваш-домен.ru

   Либо временно остановите nginx и используйте standalone:
   docker compose -f docker-compose.production.yml stop nginx
   sudo certbot certonly --standalone -d ваш-домен.ru
   docker compose -f docker-compose.production.yml start nginx

4. Скопируйте ключи в infra/ssl/ (имя каталога в live/ совпадает с -d):
   sudo cp /etc/letsencrypt/live/idealfood.ddns.net/fullchain.pem ssl/fullchain.pem
   sudo cp /etc/letsencrypt/live/idealfood.ddns.net/privkey.pem ssl/privkey.pem
   (для своего домена замените idealfood.ddns.net)

   Nginx в Docker должен читать ключи: обычно хватает
   sudo chmod 644 ssl/fullchain.pem ssl/privkey.pem

5. Перезапуск: docker compose -f docker-compose.production.yml up -d

Продление: sudo certbot renew && затем снова шаг 4 (или скрипт/hook с reload nginx).

Вариант B — только для проверки (браузер покажет предупреждение)
----------------------------------------------------------------
  cd infra/ssl
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout privkey.pem -out fullchain.pem -subj "/CN=ваш-домен.ru"

Пока нет fullchain.pem: можно поднять только HTTP, смонтировав в compose
файл nginx.http-only.conf вместо nginx.conf (без редиректа на HTTPS).
