# Django-mailer login/registration technical task

Template link: https://esk.one/p/Ga6snzW9UMSzhY/


## Login

2 Fields
1. Username field.
2. Password field

3 buttons
1. Log in
2. Registration
3. Reset password

### Rus
Пользователь должен заполнить все поля. 
При попытке входа, если пользователь ввёл НЕВЕРНО один из параметров(не смог залогиниться) - выводит оповещение с текстом (“Неверные данные для входа”, к примеру).
Если пользователь ввёл данные для входа верно, но ещё не допущен к входу, т.к. не подтвердил e-mail - выводится сообщение с текстом (“E-mail ещё не подтверждён”)
Если пользователь ввёл данные для входа верно, подтвердил свой e-mail, но админ ещё не одобрил пользователя - выводится сообщение с текстом (“Аккаунт не активирован администрацией”)
Если пользователь ввёл данные верно и его аккаунт активирован администрацией - он входит в аккаунт и начинает пользоваться системой.

Для того что бы была возможность реализовать подобную систему, нужено расширить модель пользователя за счёт поля со статусом пользователя, в котором будет три состояния:
``` python
# status user
not_confirmed_user = "NCN"
mail_confirmed_user = "MCN"
admin_confirmed_user = "ACN"
user_status_choice = (
        (not_confirmed_user, 'Not confirmed mail'),
        (mail_confirmed_user, 'Confirmed mail'),
        (admin_confirmed_user, 'Admin confirmed'),
    )
mailer_user_status = models.CharField(max_length=3,
                                      choices=user_status_choice,
                                      default=not_confirmed_user,
                                      verbose_name='user status')
```
Админ будет сам вручную менять статус пользователя в панели админа(там будет выпадающее меню с вариантами).
Подробнее про создание пользователя в - Registration

### Eng
User must fill in all fields.
When trying to log in, if the user entered FALSE one of the parameters (could not log in) - displays an alert with text (“Wrong login data”, for example).

If the user has entered the login data correctly, but is not yet allowed to enter, because did not confirm e-mail - a message is displayed with the text (“E-mail has not yet been confirmed”)
If the user entered the login information correctly, he confirmed his e-mail, but the admin has not yet approved the user - a message is displayed with the text (“The account has not been activated by the administration”)

If the user has entered the data correctly and his account has been activated by the administration, he logs into the account and starts using the system.

In order to be able to implement such a system, it is necessary to expand the user's model by means of a field with a user status, in which there will be three states:
``` python
# status user
not_confirmed_user = "NCN"
mail_confirmed_user = "MCN"
admin_confirmed_user = "ACN"
user_status_choice = (
        (not_confirmed_user, 'Not confirmed mail'),
        (mail_confirmed_user, 'Confirmed mail'),
        (admin_confirmed_user, 'Admin confirmed'),
    )
mailer_user_status = models.CharField(max_length=3,
                                      choices=user_status_choice,
                                      default=not_confirmed_user,
                                      verbose_name='user status')
```
The admin will manually change the user's status in the admin panel (there will be a drop-down menu with options).
Learn more about creating a user in - Registration


## Registration

2 Fields
1. Username field
2. Password field
3. Password repeat field
4. Company name
5. Company address
6. First email
7. Second email
8. Contact number
9. Industry
10. Website

3 buttons
1. Log in
2. Registration
3. Reset password

### Rus
Пользователь при регистрации должен заполнить ВСЕ поля.

Поля First email и Second email отличаются.

В поле где пользователь вводит First email/Second email он может ввести почту лишь с доменом своей фирмы, для этого создаётся модель с чёрным списком доменов(общественные домены, такие как: gmail.com, yandex.ru and etc.) в этом списке хранится всё что идёт в e-mail’е после @, при регистрации на бэкэнде проверяется совпадение введённого домена и доменов из черного списка и если совпадение найдено - регистрация не происходит и выводится ошибка(“В регистрации отказано, данный домен в чёрном списке”).
Если регистрация прошла успешно, то пользователю на First email/Second email высылается сообщение со ссылкой для подтверждения почты и выставляется стандартный статус - not_confirmed_user(который не позволяет логиниться в систему).

После того как пользователь подтвердил email его статус меняется на - mail_confirmed_user(он всё ещё не может логиниться).
После того как админ увидит с панеле админа пользователя со статусом mail_confirmed_user, он сможет его проверить и изменить статус на admin_confirmed_user, который позволит пользователю входить в аккаунт и пользоваться системой.

### Eng
The user must fill in ALL the fields when registering.
The First email and Second email fields are different.
In the field where the user enters First email/Second email, he can enter mail only with the domain of his company, a model with a black list of domains (public domains such as: gmail.com, yandex.ru and etc.) is created for this purpose. all that goes to the e-mail after @, when registering on the backend, the match of the entered domain and the domains from the black list is checked and if a match is found - registration does not occur and an error is displayed (“Registration denied, this domain is blacklisted”).

If the registration was successful, then a message will be sent to the First email / Second email to the user with a link to confirm mail and the standard status is not_confirmed_user (which does not allow logging into the system).
After the user has confirmed the email, his status changes to - mail_confirmed_user (he still cannot log in).
After the admin sees the admin user with the mail_confirmed_user status, he can check it and change the status to admin_confirmed_user, which will allow the user to log in and use the system.

## Verification
### Rus
Каждый email пользователя должен быть подтверждён.

Для этого на оба введённых email высылается по одному письму со ссылками для активации. 

Ссылка имеет вид:

```www.host.com/activation/<user_id>/<mail_id(1,2)>/<verify_key>```

После активации двух почт - пользователь получает возможность входа в аккаунт.

### Eng
Each user email must be confirmed.

To do this, both emails are sent one by one with activation links.

The link looks like:

```www.host.com/activation/<user_id>/<mail_id(1,2)>/<verify_key>```

After activating the two mails - the user gets the opportunity to log into the account.

