from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from builders import form_btn
from reply import main, rmk

from data.databases import DataBase
from utils.states import Form
from utils.city import check

router = Router()


@router.message(CommandStart())
async def my_form(message: Message, state: FSMContext, db: DataBase):
    is_exists = await db.get(message.from_user.id, one=True)
    if is_exists is not None:
        data = await db.get(message.from_user.id)
        usr = data.one()
        pattern = {
            "photo": usr.photo,
            "caption": f"{usr.name} {usr.age}, {usr.city}\n{usr.bio}"
        }

        await message.answer_photo(**pattern, reply_markup=main)
    else:
        await state.set_state(Form.name)
        await message.answer(
            "Отлично, введи своё имя",
            reply_markup=form_btn(message.from_user.first_name)
        )


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("Теперь укажи свой возраст", reply_markup=rmk)


@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if str(message.text).isdigit():
        await state.update_data(age=int(message.text))
        await state.set_state(Form.city)
        await message.answer("Теперь укажи свой город")
    else:
        await message.answer("Попробуй еще раз!")


@router.message(Form.city)
async def form_city(message: Message, state: FSMContext):
    city_exists = await check(message.text)
    if city_exists:
        await state.update_data(city=message.text)
        await state.set_state(Form.sex)
        await message.answer(
            "Теперь давай определимся с полом",
            reply_markup=form_btn(["Парень", "Девушка"])
        )
    else:
        await message.answer("Попробуй еще раз!")


@router.message(Form.sex, F.text.casefold().in_(["парень", "девушка"]))
async def form_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(Form.look_for)
    await message.answer(
        "Кого ты предпочитаешь искать?",
        reply_markup=form_btn(["Парни", "Девушки", "Мне все равно"])
    )


@router.message(Form.sex)
async def incorrect_form_sex(message: Message, state: FSMContext):
    await message.answer("Выбери один вариант!")


@router.message(
    Form.look_for,
    F.text.casefold().in_(["девушки", "парни", "мне все равно"])
)
async def form_look_for(message: Message, state: FSMContext):
    await state.update_data(look_for=message.text)
    await state.set_state(Form.about)
    await message.answer("Теперь расскажи о себе", reply_markup=rmk)


@router.message(Form.look_for)
async def incorrect_form_look_for(message: Message, state: FSMContext):
    await message.answer("Выбери один вариант!")


@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    await state.set_state(Form.photo)
    await message.answer("Теперь отправь фото")


@router.message(Form.photo, F.photo)
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    phid = message.photo[-1].file_id

    data = await state.get_data()
    data["user_id"] = message.from_user.id
    data["photo"] = phid

    await db.insert(**data)
    await state.clear()

    frm_text = []
    [
        frm_text.append(f"{value}")
        for key, value in data.items()
        if key not in ["user_id", "photo"]
    ]
    await message.answer_photo(phid,"\n".join(frm_text))


@router.message(Form.photo, ~F.photo)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь фото!")