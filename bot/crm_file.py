import asyncio
from amocrm.v2 import Lead as _Lead, custom_field
from amocrm.v2.exceptions import AmoApiException


class Lead(_Lead):
    vacancy = custom_field.TextCustomField("Отклик")
    user_id = custom_field.NumericCustomField('id_user')
    name = custom_field.TextCustomField("Имя")
    last_name = custom_field.TextCustomField("Фамилия")
    telephone_number = custom_field.TextCustomField("Номер телефона")
    category = custom_field.TextCustomField('Категория')


async def create_lead(name='ivan', surname='ivanov', user_id=123, text='qefq', tel_number='212412', category='Общая рассылка', count=0):
    try:
        lead_name = f'{name} {surname}'
        created_lead = Lead.objects.create({'name': lead_name})
        created_lead.vacancy = text[:100]
        created_lead.user_id = int(user_id)
        created_lead.telephone_number = tel_number[:50]
        created_lead.category = category[:40]
        created_lead.name = name[:20]
        created_lead.last_name = surname[:20]
        created_lead.save()
    except AmoApiException:
        if count == 0:
            await asyncio.sleep(2)
            count += 1
            return await create_lead(name, surname, user_id, text, tel_number, category, count)
        else:
            return
    except Exception:
        return
