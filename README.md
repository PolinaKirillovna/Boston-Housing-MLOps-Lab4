# Boston Housing ML Project

## Описание проекта
Учебный MLOps-проект по теме **«Классический жизненный цикл разработки моделей машинного обучения»** для предсказания стоимости жилья в пригородах Бостона.

Целевая переменная: `medv`  
Тип задачи: **регрессия**  
Основная метрика: **RMSE**

## Датасет
Используется датасет **Boston Housing** (вариант 4).

Основные файлы данных:
- `data/raw/train.csv`
- `data/raw/test.csv`
- `data/raw/submission_example.csv`

## Исследование и выбор модели
На этапе исследования в Google Colab были протестированы несколько моделей:
- `LinearRegression` — baseline;
- `Ridge` — улучшенная линейная модель;
- `RandomForestRegressor` — основная выбранная модель.

## Метрика качества
Основная метрика проекта: **RMSE**.

Текущий результат локальной валидации:
- **RMSE ≈ 2.8**

## Текущее состояние проекта
На текущем этапе реализовано:
- базовый EDA и выбор модели в Google Colab;
- перенос обучения в Python-скрипт;
- сохранение обученной модели в `models/model.joblib`;
- batch prediction для `test.csv`;
- FastAPI API с endpoint'ами:
  - `GET /health`
  - `GET /feature-metadata`
  - `POST /predict`
- `config.ini` для параметров проекта и модели;
- тесты на обучение, batch prediction и API;
- `.editorconfig` для единообразного стиля кода;
- docstring-документация для модулей, функций и классов.

## Структура проекта
```text
Boston-Housing-MLOps/
├── app/
│   ├── __init__.py
│   └── main.py                 # FastAPI приложение
├── data/
│   └── raw/
│       ├── train.csv
│       ├── test.csv
│       └── submission_example.csv
├── models/
│   └── model.joblib            # обученная модель
├── notebooks/
│   └── ...                     # ноутбуки Colab / Jupyter
├── src/
│   ├── __init__.py
│   ├── config.py               # загрузка config.ini
│   ├── train.py                # обучение модели
│   └── predict.py              # batch prediction
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_predict.py
│   └── test_train.py
├── .editorconfig
├── config.ini
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```

## Требования к окружению
Рекомендуемая среда:
- **macOS**
- **PyCharm Community**
- **conda / Anaconda**
- **Python 3.12**

## Зависимости
Основные зависимости проекта:
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `seaborn`
- `fastapi`
- `uvicorn`
- `joblib`
- `pydantic`
- `pytest`
- `httpx`

## Подготовка окружения

### 1. Активировать conda-окружение
```bash
conda activate boston-mlops-py312
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Подготовить данные
CSV-файлы должны лежать в папке:

```text
data/raw/
```

Ожидаемые файлы:
- `train.csv`
- `test.csv`
- `submission_example.csv`

## Конфигурация проекта
Проект использует файл `config.ini`.

Пример основных параметров:
- `random_state`
- `target_col`
- `id_col`
- пути к train/test/model/submission
- гиперпараметры `RandomForestRegressor`
- `test_size`

Это позволяет:
- убрать хардкод из Python-скриптов;
- упростить изменение параметров обучения;
- подготовить проект к DVC, Docker и CI/CD.

## Как запускать проект
Все команды выполняются **из корня проекта**.

### 1. Обучение модели
```bash
python -m src.train
```

Что делает команда:
- читает `data/raw/train.csv`;
- проверяет обязательные колонки;
- выделяет признаки и target;
- делит данные на train/validation;
- обучает `RandomForestRegressor`;
- считает RMSE;
- сохраняет модель в `models/model.joblib`.

Ожидаемый результат:
- создаётся или обновляется файл `models/model.joblib`;
- в консоли печатается `Validation RMSE`.

### 2. Сформировать предсказания для test.csv
```bash
python -m src.predict
```

Что делает команда:
- загружает сохранённую модель;
- читает `data/raw/test.csv`;
- валидирует набор признаков;
- создаёт `submission.csv` в корне проекта.

### 3. Запустить API
```bash
python -m uvicorn app.main:app --reload
```

После запуска сервис доступен по адресам:
- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API

### GET /health
Проверка состояния приложения и наличия модели.

Пример ответа:
```json
{
  "status": "ok",
  "model_exists": true
}
```

### GET /feature-metadata
Служебный endpoint для фронтенда и интеграций.

Пример ответа:
```json
{
  "features": [
    "crim",
    "zn",
    "indus",
    "chas",
    "nox",
    "rm",
    "age",
    "dis",
    "rad",
    "tax",
    "ptratio",
    "black",
    "lstat"
  ],
  "target": "medv"
}
```

### POST /predict
Предсказание `medv` по набору признаков дома.

Пример запроса:
```json
{
  "crim": 0.02729,
  "zn": 0.0,
  "indus": 7.07,
  "chas": 0,
  "nox": 0.469,
  "rm": 7.185,
  "age": 61.1,
  "dis": 4.9671,
  "rad": 2,
  "tax": 242,
  "ptratio": 17.8,
  "black": 392.83,
  "lstat": 4.03
}
```

Пример ответа:
```json
{
  "predicted_medv": 31.8421
}
```

## Тестирование

### Запуск всех тестов
```bash
pytest -v
```

Тестами покрыты:
- функции обучения;
- batch prediction;
- API endpoints.

