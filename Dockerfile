FROM python:3.9

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /homework_2

ADD assistant_bot.py .
# Kopiujemy inne pliki do katalogu roboczego kontenera
COPY assistant_bot.py /homework_2/assistant_bot.py

RUN pip install requests beautifulsoup4

# Uruchomiamy naszą aplikację wewnątrz kontenera
CMD ["python", "./assistant_bot.py"]



