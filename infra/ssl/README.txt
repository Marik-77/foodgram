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

3. Первый выпуск сертификата, если nginx уже слушает 80 (webroot):
   sudo certbot certonly --webroot -w /home/USER/foodgram/infra/certbot/www \
     -d ваш-домен.ru -d www.ваш-домен.ru

   Либо временно остановите nginx и используйте standalone:
   docker compose -f docker-compose.production.yml stop nginx
   sudo certbot certonly --standalone -d ваш-домен.ru
   docker compose -f docker-compose.production.yml start nginx

4. Скопируйте ключи в infra/ssl/ (пути зависят от certbot):
   sudo cp /etc/letsencrypt/live/ваш-домен.ru/fullchain.pem ssl/fullchain.pem
   sudo cp /etc/letsencrypt/live/ваш-домен.ru/privkey.pem ssl/privkey.pem
   sudo chown USER:USER ssl/*.pem

5. Перезапуск: docker compose -f docker-compose.production.yml up -d

Вариант B — только для проверки (браузер покажет предупреждение)
----------------------------------------------------------------
  cd infra/ssl
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout privkey.pem -out fullchain.pem -subj "/CN=ваш-домен.ru"

Пока нет fullchain.pem: можно поднять только HTTP, смонтировав в compose
файл nginx.http-only.conf вместо nginx.conf (без редиректа на HTTPS).
