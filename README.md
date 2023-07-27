# Инструкция по запуску 
./start_bot.sh <путь до корня проекта> [-s]
Опция -s запускает в бота в detached-сессии screen (в фоновом режиме) 
Примеры:
/home/username/air_bot_repo/start_bot.sh /home/username/air_bot_repo
./start_bot.sh . -s
Подключиться к сессии:
screen -x air_bot
Остановить бота: Ctrl+C

Для автоматического запуска после перезагрузки:
crontab -e
Добавить строчку
/home/denis/my_github/AviasalestTicketCheckerBot
