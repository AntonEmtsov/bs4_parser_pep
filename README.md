# Проект парсинга pep

### Тенологии используемые в проекте:
- python 3.8
- beautifulsoup4 4.9.3
- tqdm 4.61.0
- lxml 4.6.3

### Как запустить проект:
Клонировать репозиторий:
```
https://github.com/russ044/bs4_parser_pep.git
```
Создать и активировать виртуальное окружение:
```
python -m venv venv
```
Установить зависимостей:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Запустить парсер.
```
python ./src/main.py whats-new -o pretty
```
Режимы:
- ```whats-new``` - нововведения Python;
- ```latest-versions``` - информация о последних версиях;
- ```download``` - загрузка документации;
- ```pep``` - парсинг информации по PEP;

Опции:
- ```-c```   ```--clear-cache``` - очистка кеша;
- ```-o```   ```--output``` - вывод данных; 
  - ```pretty``` - вывод данных парсинга в терминале таблицей;
  -  ```file```  - вывод данных парсинга в файл;
### Автор проекта:
- Емцов А.В.  [russ044](https://github.com/russ044)
